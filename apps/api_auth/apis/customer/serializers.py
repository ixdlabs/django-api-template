from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from apps.users.apis.customer.serializers import CustomerEnrollmentCustomerSerializer
from apps.users.models import User


class UserAuthCustomerSerializer(serializers.ModelSerializer):
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
            "cus_enrollment",
        ]
        read_only_fields = ["id", "user_type", "username", "photo", "cus_enrollment"]


class LoginSendOtpCustomerSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class LoginSendOtpResponseCustomerSerializer(serializers.Serializer):
    retry_after = serializers.DateTimeField()
    expiration_at = serializers.DateTimeField()


class LoginVerifyOtpCustomerSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    code = serializers.CharField()


class LoginResponseCustomerSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserAuthCustomerSerializer()
