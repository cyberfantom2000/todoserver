from dataclasses import dataclass
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

from exceptions import CouldNotValidateCredentials, InvalidArguments, InvalidCredentials
from models.user import User, UserCreate
from .token import Token, TokenData


@dataclass
class AuthSecrets:
    algorithm: str
    key: str


class Hasher:
    def __init__(self, context):
        self.context = context

    def hash(self, string) -> str:
        return self.context.hash(string)

    def verify(self, string, string_hash) -> bool:
        return self.context.verify(string, string_hash)


class TokenManager:
    def __init__(self, secrets: AuthSecrets):
        self.secrets = secrets
        self._token_expired_minutes = 60 * 8

    @property
    def token_expired_minutes(self):
        return self._token_expired_minutes

    @token_expired_minutes.setter
    def token_expired_minutes(self, value):
        if not value or not isinstance(value, int) or value < 0:
            raise ValueError(f'Invalid value {value}')
        self._token_expired_minutes = value

    @token_expired_minutes.deleter
    def token_expired_minutes(self):
        raise NotImplementedError('Invalid operation')

    def create(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_expired_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secrets.key, algorithm=self.secrets.algorithm)

    def decode(self, token) -> dict:
        return jwt.decode(token, self.secrets.key, algorithms=[self.secrets.algorithm])


class AuthSystem:
    def __init__(self, token_manager, repo, hasher):
        self.token_manager = token_manager
        self.repo = repo
        self.hasher = hasher

    def login(self, username: str, password: str) -> Token:
        user = self._authenticate_user(username, password)
        return self.token_manager.create(data={'sub': str(user.id), 'login': user.login})

    def registration(self, new_user: User | UserCreate) -> User:
        users_ids = self.repo.get_fields(User, User.id, filters={'login': new_user.login})
        if users_ids:
            raise InvalidArguments('Login already used')

        new_user.password = self.hasher.hash(new_user.password)
        return self.repo.create(User, model_data=new_user)

    def user_by_token(self, token) -> User:
        try:
            payload = self.token_manager.decode(token)
            user_id = int(payload.get('sub'))
            user_login = payload.get('login')
            if user_id is None:
                raise CouldNotValidateCredentials()
            token_data = TokenData(user_id=user_id, user_login=user_login)
        except JWTError as err:
            print(err)
            raise CouldNotValidateCredentials()

        user = self._get_user_by_id(token_data.user_id)
        if not user:
            raise CouldNotValidateCredentials()

        return user

    def _authenticate_user(self, username: str, password: str):
        user = self._get_user_by_login(username)
        if not user or not self.hasher.verify(password, user.password):
            raise InvalidCredentials()
        return user

    def _get_user_by_login(self, login: str) -> User | None:
        return self._get_user_by_filters({'login': login})

    def _get_user_by_id(self, user_id: int) -> User | None:
        return self._get_user_by_filters({'id': user_id})

    def _get_user_by_filters(self, filters) -> User:
        return self.repo.get_item(User, filters=filters)


def create_auth_system(secrets: AuthSecrets, repo) -> AuthSystem:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    hasher = Hasher(pwd_context)
    manager = TokenManager(secrets)
    return AuthSystem(manager, repo, hasher)
