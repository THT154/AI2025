# app/controllers/__init__.py
"""
Controllers Package - Presentation Layer Adapters
"""

from .auth_controller import AuthController
from .student_controller import StudentController
from .teacher_controller import TeacherController

__all__ = [
    'AuthController',
    'StudentController',
    'TeacherController'
]
