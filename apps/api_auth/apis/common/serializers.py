from rest_framework import serializers

from apps.organizations.apis.customer.serializers import OrganizationCustomerSerializer
from apps.users.apis.customer.serializers import CustomerEnrollmentCustomerSerializer
from apps.users.models import User

# User Serializer
# ----------------------------------------------------------------------------------------------------------------------


class UserSerializer(serializers.ModelSerializer):
    emp_organization = OrganizationCustomerSerializer(required=False, read_only=True)
    cus_enrollment = CustomerEnrollmentCustomerSerializer(required=False, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "user_type",
            "username",
            "email",
            "photo",
            "first_name",
            "last_name",
            "emp_role",
            "emp_organization",
            "cus_enrollment",
        ]
        read_only_fields = ["id", "user_type", "username", "photo", "emp_role", "emp_organization", "cus_enrollment"]
