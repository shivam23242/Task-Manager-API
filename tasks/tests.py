from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Task

User = get_user_model()


class TaskModelTest(TestCase):
    """Test cases for Task model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': False,
            'owner': self.user
        }
    
    def test_create_task(self):
        """Test creating a task"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(task.title, self.task_data['title'])
        self.assertEqual(task.description, self.task_data['description'])
        self.assertEqual(task.completed, False)
        self.assertEqual(task.owner, self.user)
    
    def test_task_str_method(self):
        """Test task string representation"""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(str(task), self.task_data['title'])
    
    def test_task_timestamps(self):
        """Test task timestamps are automatically set"""
        task = Task.objects.create(**self.task_data)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)


class TaskAPITest(APITestCase):
    """Test cases for Task API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        
        # Create another user
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # URLs
        self.list_url = reverse('task-list-create')
        
        # Sample task data
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': False
        }
        
        # Create a task for the user
        self.user_task = Task.objects.create(
            title='User Task',
            description='User task description',
            completed=False,
            owner=self.user
        )
        
        # Create a task for the other user
        self.other_task = Task.objects.create(
            title='Other User Task',
            description='Other user task description',
            completed=False,
            owner=self.other_user
        )
    
    def test_create_task(self):
        """Test creating a new task"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.task_data['title'])
        self.assertEqual(response.data['owner'], self.user.username)
    
    def test_create_task_without_authentication(self):
        """Test creating task without authentication fails"""
        response = self.client.post(self.list_url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_tasks(self):
        """Test listing tasks"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User should only see their own tasks
        self.assertEqual(response.data['count'], 1)
    
    def test_admin_list_all_tasks(self):
        """Test admin can see all tasks"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should see all tasks
        self.assertEqual(response.data['count'], 2)
    
    def test_retrieve_task(self):
        """Test retrieving a specific task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.user_task.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user_task.id)
    
    def test_retrieve_other_user_task(self):
        """Test regular user cannot retrieve another user's task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.other_task.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_retrieve_any_task(self):
        """Test admin can retrieve any task"""
        self.client.force_authenticate(user=self.admin)
        detail_url = reverse('task-detail', kwargs={'pk': self.user_task.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_task(self):
        """Test updating a task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.user_task.pk})
        update_data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'completed': True
        }
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
        self.assertEqual(response.data['completed'], True)
    
    def test_partial_update_task(self):
        """Test partially updating a task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.user_task.pk})
        update_data = {'completed': True}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed'], True)
        # Title should remain unchanged
        self.assertEqual(response.data['title'], self.user_task.title)
    
    def test_update_other_user_task(self):
        """Test user cannot update another user's task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.other_task.pk})
        update_data = {'completed': True}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_update_any_task(self):
        """Test admin can update any task"""
        self.client.force_authenticate(user=self.admin)
        detail_url = reverse('task-detail', kwargs={'pk': self.user_task.pk})
        update_data = {'completed': True}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed'], True)
    
    def test_delete_task(self):
        """Test deleting a task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.user_task.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify task is deleted
        self.assertFalse(Task.objects.filter(pk=self.user_task.pk).exists())
    
    def test_delete_other_user_task(self):
        """Test user cannot delete another user's task"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse('task-detail', kwargs={'pk': self.other_task.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_filter_tasks_by_completed(self):
        """Test filtering tasks by completion status"""
        self.client.force_authenticate(user=self.user)
        # Create completed task
        Task.objects.create(
            title='Completed Task',
            description='Completed',
            completed=True,
            owner=self.user
        )
        
        response = self.client.get(self.list_url, {'completed': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        
        response = self.client.get(self.list_url, {'completed': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_search_tasks(self):
        """Test searching tasks"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {'search': 'User Task'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
    
    def test_ordering_tasks(self):
        """Test ordering tasks"""
        self.client.force_authenticate(user=self.user)
        # Create another task
        Task.objects.create(
            title='Another Task',
            description='Another',
            completed=False,
            owner=self.user
        )
        
        response = self.client.get(self.list_url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # First result should be "Another Task" (alphabetically first)
        self.assertEqual(response.data['results'][0]['title'], 'Another Task')
    
    def test_pagination(self):
        """Test pagination"""
        self.client.force_authenticate(user=self.user)
        # Create multiple tasks
        for i in range(15):
            Task.objects.create(
                title=f'Task {i}',
                description=f'Description {i}',
                completed=False,
                owner=self.user
            )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        # Default page size is 10
        self.assertLessEqual(len(response.data['results']), 10)
    
    def test_task_stats(self):
        """Test task statistics endpoint"""
        self.client.force_authenticate(user=self.user)
        # Create additional tasks
        Task.objects.create(
            title='Completed Task',
            description='Completed',
            completed=True,
            owner=self.user
        )
        
        stats_url = reverse('task-stats')
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_tasks'], 2)
        self.assertEqual(response.data['completed_tasks'], 1)
        self.assertEqual(response.data['pending_tasks'], 1)

