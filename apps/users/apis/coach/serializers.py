from rest_framework import serializers

from apps.users.models import User


class UserCoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "photo", "first_name", "last_name", "cover_photo", "profile_bio", "profile_heading"]
        read_only_fields = ["id", "photo", "cover_photo"]


class UserPhotoCoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "photo", "cover_photo"]
        read_only_fields = ["id"]
