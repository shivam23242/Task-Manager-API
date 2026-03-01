from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import UserSession

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_create_admin_user(self):
        """Test creating an admin user"""
        user = User.objects.create_user(**self.user_data, role='admin')
        self.assertTrue(user.is_admin())
    
    def test_user_str_method(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['username'])


class AuthenticationAPITest(APITestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], self.user_data['username'])
        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(UserSession.objects.filter(user=user, is_active=True).exists())
    
    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_with_existing_username(self):
        """Test registration with existing username"""
        User.objects.create_user(
            username=self.user_data['username'],
            email='other@example.com',
            password='testpass123'
        )
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login"""
        # Create user
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Login
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertTrue(UserSession.objects.filter(user__username=self.user_data['username'], is_active=True).exists())
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_expires_current_session(self):
        """Test logout marks the current session expired and token stops working"""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['tokens']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post(self.logout_url, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_profile(self):
        """Test retrieving user profile"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['email'], user.email)
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        self.client.force_authenticate(user=user)
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': user.email,
            'username': user.username
        }
        response = self.client.patch(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
    
    def test_change_password(self):
        """Test password change"""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        self.client.force_authenticate(user=user)
        change_password_url = reverse('change_password')
        data = {
            'old_password': self.user_data['password'],
            'new_password': 'NewTestPass123!'
        }
        response = self.client.post(change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewTestPass123!'))
    
    def test_unauthorized_access_to_profile(self):
        """Test accessing profile without authentication"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
