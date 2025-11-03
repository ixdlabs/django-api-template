from rest_framework import serializers

from apps.users.models import User

# User Serializer
# ----------------------------------------------------------------------------------------------------------------------


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "user_type", "username", "email", "photo", "first_name", "last_name"]
        read_only_fields = ["id", "user_type", "username", "photo"]
