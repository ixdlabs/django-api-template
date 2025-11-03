from rest_framework import serializers

from apps.users.models import User


class UserAuthCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "user_type", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "user_type", "username"]


class LoginCustomerSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()


class LoginCustomerResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserAuthCustomerSerializer()
