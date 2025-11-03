from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from apps.organizations.apis.customer.serializers import BranchCustomerSerializer
from apps.organizations.models import Branch
from apps.users.models import CustomerEnrollment, User


class CustomerEnrollmentCustomerSerializer(serializers.ModelSerializer):
    branch = BranchCustomerSerializer(read_only=True)

    class Meta:
        model = CustomerEnrollment
        fields = ["id", "branch", "created", "customer_sn"]


class UserCustomerSerializer(serializers.ModelSerializer):
    cus_enrollment = CustomerEnrollmentCustomerSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "user_type",
            "username",
            "photo",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "nic_number",
            "address_line1",
            "address_line2",
            "address_city",
            "address_state",
            "address_zip",
            "emergency_contact_name",
            "emergency_contact_phone_number",
            "recent_surgery",
            "recent_surgery_notes",
            "health_complications",
            "health_complications_notes",
            "cus_enrollment",
        ]
        read_only_fields = ["id", "user_type", "username", "photo", "phone_number", "cus_enrollment"]


class UserPhotoCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "photo"]
        read_only_fields = ["id"]


class EnrollCustomerSerializer(serializers.Serializer):
    branch = PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = User
        fields = ["branch_id"]
