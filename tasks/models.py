from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Task model representing a task in the task manager
    """
    title = models.CharField(max_length=200, help_text='Task title')
    description = models.TextField(blank=True, help_text='Detailed task description')
    completed = models.BooleanField(default=False, help_text='Task completion status')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Timestamp when task was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='Timestamp when task was last updated')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text='User who owns this task'
    )
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['completed']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.title

