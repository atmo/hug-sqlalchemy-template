import hug
from falcon import HTTP_200, HTTP_400

from .. import UserAPITest

from api.models import User
from api.app import db
from api.resources.authentication.jwt import jwt_decode


class LoginEndpointTestCase(UserAPITest):

    def test_login_endpoint_response(self):
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'testuser@email.com', 'password': '!Password'}
        )
        self.assertEqual(response.status, HTTP_200)
        self.assertIn('Token', response.data)
        self.assertTrue(isinstance(response.data['Token'], str))

    def test_invalid_login_and_password(self):
        # invalid login and password
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'invalid@email.com', 'password': 'INVALID'}
        )
        self.assertEqual(response.status, HTTP_400)
        self.assertIn('errors', response.data)
        self.assertIn('Validation Error', response.data['errors'])
        self.assertEqual(response.data['errors']['Validation Error'],
                         'Invalid credentials')
        # invalid login
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'testuser2@email.com', 'password': 'PASSWORD'}
        )
        self.assertEqual(response.status, HTTP_400)
        self.assertIn('errors', response.data)
        self.assertIn('Validation Error', response.data['errors'])
        self.assertEqual(response.data['errors']['Validation Error'],
                         'Invalid credentials')
        # invalid password
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'testuser@email.com', 'password': 'PASSWORD1'}
        )
        self.assertEqual(response.status, HTTP_400)
        self.assertIn('errors', response.data)
        self.assertIn('Validation Error', response.data['errors'])
        self.assertEqual(response.data['errors']['Validation Error'],
                         'Invalid credentials')

    def test_try_login_on_other_user_password(self):
        db.connect()
        user = User(email='testuser2@email.com', password='PASSWORD2')
        db.session.add(user)
        db.close()
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'testuser@email.com', 'password': 'PASSWORD2'}
        )
        self.assertEqual(response.status, HTTP_400)
        self.assertIn('errors', response.data)
        self.assertIn('Validation Error', response.data['errors'])
        self.assertEqual(response.data['errors']['Validation Error'],
                         'Invalid credentials')

    def test_login_is_not_proper_email(self):
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'not_an_email', 'password': '!Password'}
        )
        self.assertEqual(response.status, HTTP_400)
        self.assertIn('errors', response.data)
        self.assertIn('Validation Error', response.data['errors'])
        self.assertEqual(response.data['errors']['Validation Error'],
                         'Invalid email format')

    def test_proper_jwt_is_returned(self):
        response = hug.test.post(
            hug.current_app, 'auth/login',
            body={'login': 'testuser@email.com', 'password': '!Password'}
        )
        token = response.data['Token']
        decoded = jwt_decode(token)
        self.assertEqual(decoded['email'], 'testuser@email.com')