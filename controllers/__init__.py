# controllers/__init__.py
from .auth_controller import AuthController
from .teacher_controller import TeacherController
from .student_controller import StudentController
from .moderator_controller import ModeratorController

__all__ = ['AuthController', 'TeacherController', 'StudentController', 'ModeratorController']
