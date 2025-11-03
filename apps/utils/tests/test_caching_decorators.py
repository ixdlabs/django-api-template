import uuid
from typing import Any

from django.core.cache import cache
from django.test import RequestFactory, TestCase

from apps.utils.cache import (
    cache_current_request_property,
    cache_global_property,
    cache_serializer_result_per_object,
)


class CachingDecoratorsTestCase(TestCase):
    # ------------------------------------------------------------------------------------------------------------------
    def test_cache_global_property_caches_and_reuses_result(self):
        calls = {"count": 0}

        @cache_global_property("global_settings_key", timeout=60)
        def get_settings():
            calls["count"] += 1
            return {"mode": "prod"}

        # First call computes
        v1 = get_settings()
        assert v1 == {"mode": "prod"}
        assert calls["count"] == 1

        # Second call should be served from cache (no increment)
        v2 = get_settings()
        assert v2 == {"mode": "prod"}
        assert calls["count"] == 1

        # Manual invalidation -> should recompute once
        cache.delete("global_settings_key")
        v3 = get_settings()
        assert v3 == {"mode": "prod"}
        assert calls["count"] == 2

    # ------------------------------------------------------------------------------------------------------------------
    def test_cache_current_request_property_per_request(self):
        rf = RequestFactory()
        calls = {"count": 0}

        @cache_current_request_property("current_permissions")
        def get_perms(request):
            calls["count"] += 1
            return ["read", "write"]

        # Request A: first call computes, second call uses request attribute cache
        req_a = rf.get("/sample")
        p1 = get_perms(req_a)
        p2 = get_perms(req_a)
        assert p1 == ["read", "write"]
        assert p2 == ["read", "write"]
        assert calls["count"] == 1  # only computed once for this request

        # Request B: new request should trigger a new compute
        req_b = rf.get("/sample")
        p3 = get_perms(req_b)
        assert p3 == ["read", "write"]
        assert calls["count"] == 2

    # ------------------------------------------------------------------------------------------------------------------
    def test_cache_serializer_is_per_serializer_instance(self):
        class DummyObj:
            def __init__(self, id_):
                self.id = id_

        class DummySerializer:
            def __init__(self):
                self.calls = 0

            @cache_serializer_result_per_object("current_membership")
            def get_dummy(self, obj: DummyObj) -> Any:
                self.calls += 1
                return {"obj": obj.id, "plan": "gold"}

        # Ensure cache is bound to each serializer instance, not global
        ser1 = DummySerializer()
        ser2 = DummySerializer()
        obj = DummyObj(uuid.uuid4())

        _ = ser1.get_dummy(obj)  # compute in ser1
        assert ser1.calls == 1
        assert ser2.calls == 0

        _ = ser2.get_dummy(obj)  # compute again in ser2 (separate cache)
        assert ser2.calls == 1
