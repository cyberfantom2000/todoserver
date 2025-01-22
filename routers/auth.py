import re
from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from exceptions import InvalidArguments
from auth import AuthSystem, Token
from models import User, UserCreate, UserPublic


# oauth2 = OAuth2PasswordBearer(tokenUrl='/api/token')
#
#
# def get_user_by_token(token: Annotated[str, Depends(oauth2)]) -> User:
#     auth = AuthSystem.instance()
#     return auth.user_by_token(token)


def strip_string(s: str) -> str:
    return s.lstrip().rstrip()


def is_valid_login(login: str):
    base_pattern = r'^[a-zA-Z0-9](?!.*\.\.)(?!.*\.$)[a-zA-Z0-9._-]{2,19}$'
    escape_sequence_pattern = r'\\[abfnrtv\'"\\]|\\x[0-9A-Fa-f]{2}|\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8}'
    if not bool(re.match(base_pattern, login)) or bool(re.search(escape_sequence_pattern, login)):
        return False

    return True


def is_validate_password(password: str):
    return len(password) >= 3  # FIXME: for develop
    # return len(password) >= 8 and \
    #        re.search(r'[A-Z]', password) and \
    #        re.search(r'[a-z]', password) and \
    #        re.search(r'[0-9]', password) and \
    #        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)


def is_valid_email(email: str):
    pattern = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    return bool(re.match(pattern, email))


class AuthRouter:
    def __init__(self, auth_system: AuthSystem):
        self.router = APIRouter(prefix='/api', tags=['auth'])
        self.auth = auth_system

        self.router.add_api_route('/token', self.get_access_token, methods=['POST'], response_model=Token)
        self.router.add_api_route('/registration', self.registration, methods=['POST'], response_model=UserPublic)

    async def get_access_token(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        """ Get access token by login and password """
        access_token = self.auth.login(form_data.username, form_data.password)
        return Token(access_token=access_token, token_type='bearer')

    async def registration(self, new_user: UserCreate):
        """ Registration new user """
        new_user.login = strip_string(new_user.login)
        if not is_valid_login(new_user.login):
            raise InvalidArguments('Login must not contains: spaces, escape sequence and characters "#, ?, %, @, &, ="')

        new_user.password = strip_string(new_user.password)
        if not is_validate_password(new_user.password):
            raise InvalidArguments('The password must be more than 7 characters and also contain: lowercase letters, '
                                   'uppercase letters, numbers and special symbols')
        new_user.email = strip_string(new_user.email)
        if not is_valid_email(new_user.email):
            raise InvalidArguments('Invalid email address')

        return self.auth.registration(new_user)
