import functools
from typing import Any, Callable, Optional, TypeVar
from uuid import UUID

from django.core.cache import cache
from django.http import HttpRequest

T = TypeVar("T")


def cache_global_property(
    cache_key: str, timeout: Optional[int] = None
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Decorator to cache the result of a global function using Django's cache.

    Usage:
        ```
        @cache_result("current_global_settings", timeout=60)
        def get_current_global_settings():
            return GlobalSettings.objects.first()
        ```

    On first call, result is cached and reused until timeout expires.

    Args:
        cache_key: Key used for Django cache backend.
        timeout: Cache expiration time in seconds.

    Returns:
        Decorated function with caching applied.
    """

    def decorator(fn: Callable[[], T]) -> Callable[[], T]:
        @functools.wraps(fn)
        def wrapped_fn():
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = fn()
            cache.set(cache_key, result, timeout=timeout)
            return result

        return wrapped_fn

    return decorator


def cache_current_request_property(
    cache_key: str,
) -> Callable[[Callable[[HttpRequest], Any]], Callable[[HttpRequest], Any]]:
    """
    Decorator that caches the result of a request-bound function for the duration
    of a single Django `HttpRequest` lifecycle, using the provided cache key.

    This avoids recomputing the same value multiple times during one request by
    storing the result as an attribute on the request object.

    Usage:
        ```
        @cache_current_request_property("current_permissions")
        def get_current_permissions(request):
            return expensive_permissions_computation()
        ```

    On first call, the result is cached under:
        ```
        self._cache_current_permissions = result
        ```

    Args:
        key: A unique key used to cache the result on the request.

    Returns:
        A decorator that wraps the function.
    """

    def decorator(fn: Callable[[HttpRequest], Any]) -> Callable[[HttpRequest], Any]:
        @functools.wraps(fn)
        def wrapped_fn(request: HttpRequest):
            attr_name = f"_cache_{cache_key}"

            if hasattr(request, attr_name):
                return getattr(request, attr_name)
            value = fn(request)
            setattr(request, attr_name, value)
            return value

        return wrapped_fn

    return decorator


def cache_serializer_result_per_object(cache_key: str) -> Callable[[Callable[[Any, T], Any]], Callable[[Any, T], Any]]:
    """
    Decorator for DRF serializers to cache the result of a method per object
    using a serializer instance-bound dictionary keyed by the object's ID.

    Example:
        ```
        @cache_serializer_result_per_object("current_membership")
        def _get_current_membership(self, obj):
            return expensive_lookup(obj)
        ```

    On first call per `obj.id`, the result is cached under:
        ```
        self._cache_current_membership[obj.id] = result
        ```

    Args:
        cache_key: Name of the per-object cache (e.g. "current_membership")

    Returns:
        Wrapped function that caches its result per object.
    """

    def decorator(fn: Callable[[Any, T], Any]) -> Callable[[Any, T], Any]:
        @functools.wraps(fn)
        def wrapped(self, obj: T) -> Any:
            attr_name = f"_cache_{cache_key}"

            if not hasattr(self, attr_name):
                setattr(self, attr_name, {})

            cache: dict[UUID, Any] = getattr(self, attr_name)
            obj_id = getattr(obj, "id")
            if obj_id in cache:
                return cache[obj_id]

            value = fn(self, obj)
            cache[obj_id] = value
            return value

        return wrapped

    return decorator
