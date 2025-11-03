from rest_framework import serializers

from apps.users.models import User


class UserCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "user_type", "username", "first_name", "last_name", "email"]
        read_only_fields = ["id", "user_type", "username"]
