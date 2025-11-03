from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.choices import UserTypes
from apps.users.models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def test_checks_users_for_validation_errors_on_save(self):
        with self.assertRaises(ValidationError) as e:
            User.objects.create()
        self.assertIn("password", e.exception.message_dict)
        self.assertIn("username", e.exception.message_dict)

    # ------------------------------------------------------------------------------------------------------------------
    def test_can_create_customer(self):
        user = User.objects.create_user(username="test", user_type=UserTypes.CUSTOMER)
        self.assertEqual(user.user_type, UserTypes.CUSTOMER)

    # ------------------------------------------------------------------------------------------------------------------
    def test_can_create_unset(self):
        user = User.objects.create_user(username="test")
        self.assertEqual(user.user_type, UserTypes.UNSET)

    # ------------------------------------------------------------------------------------------------------------------
    def test_can_create_superadmin(self):
        user1 = User.objects.create_user(username="test1", is_staff=True, is_superuser=True)
        self.assertEqual(user1.user_type, UserTypes.UNSET)
        self.assertEqual(user1.username, "test1")
        user2 = User.objects.create_superuser(username="test2")
        self.assertEqual(user2.user_type, UserTypes.UNSET)
        self.assertEqual(user2.username, "test2")

    # ------------------------------------------------------------------------------------------------------------------
    def test_username_must_be_unique(self):
        User.objects.create_user(username="test1", user_type=UserTypes.CUSTOMER)
        with self.assertRaises(ValidationError) as e:
            User.objects.create_user(username="test1", user_type=UserTypes.CUSTOMER)
        self.assertIn("username", e.exception.message_dict)
