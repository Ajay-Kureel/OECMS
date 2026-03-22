from django.db import models
from django.contrib.auth.models import AbstractUser
from academics.models import Course
class CustomUser(AbstractUser):
    # Define Roles
    ADMIN = 'admin'
    FACULTY = 'faculty'
    STUDENT = 'student'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (FACULTY, 'Faculty'),
        (STUDENT, 'Student'),
    ]

    # Add custom fields
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True)

    # --- NEW: Academic Identity (For Students Only) ---
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year = models.PositiveIntegerField(null=True, blank=True, help_text="e.g., 1, 2, 3")
    section = models.CharField(max_length=50, null=True, blank=True, help_text="e.g., BCA11, A, CS-3A")
    
    # Specific fields for validation
    is_approved = models.BooleanField(default=False) # For faculty/students waiting for admin approval

    def __str__(self):
        return f"{self.username} ({self.role})"