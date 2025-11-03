from typing import Sequence

from rest_framework.routers import DefaultRouter


class PublicEndpoint:
    permission_classes: Sequence = ()
    authentication_classes: Sequence = ()


class PrefixedDefaultRouter(DefaultRouter):
    def __init__(self, prefix: str, trailing_slash=True, use_regex_path=True, *, root_renderers=...):
        super().__init__(trailing_slash, use_regex_path, root_renderers=root_renderers)
        self.prefix = prefix

    def register(self, prefix, viewset, basename=..., base_name=...):
        return super().register(f"{self.prefix}/{prefix}", viewset, f"{self.prefix}-{basename}")
