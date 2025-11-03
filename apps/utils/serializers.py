from rest_framework import serializers


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()
