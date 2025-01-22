import unittest

from routers.auth import is_validate_password, is_valid_login, is_valid_email


class TestValidators(unittest.TestCase):
    def test_check_valid_login(self):
        logins = ['valid_se', 'abc', 'aaaaaaaaaaaaaaaaaaa', 'login_', 'lLoGin']
        self.assertTrue(any(is_valid_login(login) for login in logins))

    def test_check_invalid_login(self):
        logins = ['val..a', '...v', '...', 'rrrrrrrrrrrrrrrrrrrrr', 'rt', 'user@name', 'user$name', 'test a',
                  'test\nd', 'test\t', 'test\\', '\\test', 'te\\st', 'login%', 'log#', 'log?', 'log=', 'test test',
                  'loGin\r', '\rloGin', '\x01test']
        self.assertFalse(any(is_valid_login(login) for login in logins))

    def test_check_valid_password(self):
        passwords = ["ddS_ddtl22", "ddDD2ta>", "!daTesppp[a", '{dsds}R2a']
        self.assertTrue(any(is_validate_password(password) for password in passwords))

    def test_check_invalid_password(self):
        passwords = ['dddTR22a', 'rT{2art', 'dtaE!dsdg', 'prst22{dsa', 'GRTAC{213LG']
        self.assertFalse(any(is_validate_password(password) for password in passwords))

    def test_check_valid_email(self):
        emails = ['test@mail.ru', 'tessfasa@gmail.com', 'check@yandex.ru']
        self.assertTrue(any(is_valid_email(email) for email in emails))

    def test_check_invalid_email(self):
        emails = ['testmail.ru', 'tessfasa@gmail', 'checkyandexru']
        self.assertFalse(any(is_valid_email(email) for email in emails))


if __name__ == '__main__':
    unittest.main()
