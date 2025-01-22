import unittest
from unittest.mock import MagicMock

from routers.auth import AuthRouter
from exceptions import InvalidArguments
from models import UserCreate, User


def registration_mock(user):
    return User.model_validate(user.model_dump())


class TestAuthRouter(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        mock = MagicMock()
        mock.registration = MagicMock(side_effect=registration_mock)
        self.auth = AuthRouter(mock)

    async def test_invalid_registration(self):
        tuples = [('valid_login', 'invalidPassword{', 'valid@email.ru'),
                  ('.invalid login', 'validPassword{22', 'valid@gmail.com'),
                  ('invalid_\x04login', 'valid;paswOrd2', 'valid@yandex.ru'),
                  ('invalid\rlogin', 'invalidPasswd2', 'valid@mail.ru'),
                  ('valid_login', 'validPassword{22', 'invalidmail.ru')]

        for login, password, email in tuples:
            with self.assertRaises(InvalidArguments):
                await self.auth.registration(UserCreate(login=login, password=password, email=email))

    async def test_valid_registration(self):
        tuples = [('valid_login', 'validPassword{2', 'valid@email.ru'),
                  ('validlogin77', 'valid78Password!', 'valid@gmail.com'),
                  ('ValidLogin123', 'valid<passwOrd2', 'valid@yandex.ru')]

        for login, password, email in tuples:
            user = await self.auth.registration(UserCreate(login=login, password=password, email=email))
            self.assertEqual(user.login, login)
            self.assertEqual(user.email, email)


if __name__ == '__main__':
    unittest.main()
