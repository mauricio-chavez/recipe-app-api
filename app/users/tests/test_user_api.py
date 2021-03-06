"""Unit test for users app"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('users:create')
TOKEN_URL = reverse('users:token')


def create_user(**params):
    """Makes easier to create users"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Tests the user API (public)"""

    def setUp(self):
        """Initial setup for testing"""
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@mauriciochavez.dev',
            'password': 'testPassword123',
            'name': 'Test name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Tests creating user that already exists fails"""
        payload = {
            'email': 'test@mauriciochavez.dev',
            'password': 'testPassword123',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Tests that password must be more than 5 characters"""
        payload = {
            'email': 'test@mauriciochavez.dev',
            'password': 'pw',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Tests that token is created for the user"""
        payload = {
            'email': 'test@mauriciochavez.dev',
            'password': 'testPassword123',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Tests that token is not created if invalid credentials are given"""
        create_user(
            email='test@mauriciochavez.dev',
            password='testPassword321'
        )
        payload = {
            'email': 'test@mauriciochavez.dev',
            'password': 'wrongPass321',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_user(self):
        """Tests that token is not created if user doesn't exists"""
        payload = {
            'email': 'test@mauriciochavez.dev',
            'password': 'testPass321',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Tests that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
