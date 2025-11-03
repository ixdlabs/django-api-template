from apps.utils.services import get_cache_info, get_celery_info, get_storage_info


def dashboard_callback(request, context):
    context["celery_info"] = get_celery_info()
    context["cache_info"] = get_cache_info()
    context["storage_info"] = get_storage_info()
    return context
