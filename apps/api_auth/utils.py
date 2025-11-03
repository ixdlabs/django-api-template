from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


def jwt_encode(user: User):
    refresh = TokenObtainPairSerializer.get_token(user)
    assert isinstance(refresh, RefreshToken)
    return refresh.access_token, refresh
