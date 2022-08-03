import functools
import json
import logging
from typing import List

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.utils.exceptions import OperationException


class ErrorHandledModelAdmin(admin.ModelAdmin):
    """
    Mixin to catch all errors in the Django Admin and map them to user-visible errors.
    https://stackoverflow.com/questions/26554069/catch-exception-on-save-in-django-admin
    """

    def change_view(self, request, object_id, form_url="", extra_context=None):
        try:
            return super().change_view(request, object_id, form_url, extra_context)
        except Exception as e:
            self.message_user(request, "Error changing model: %s" % e, level=logging.ERROR)
            # This logic was cribbed from the `change_view()` handling here:
            # django/contrib/admin/options.py:response_post_save_add()
            # There might be a simpler way to do this, but it seems to do the job.
            return HttpResponseRedirect(request.path)

    def add_view(self, request, form_url="", extra_context=None):
        try:
            return super().add_view(request, form_url, extra_context)
        except Exception as e:
            self.message_user(request, "Error adding model: %s" % e, level=logging.ERROR)
            return HttpResponseRedirect(request.path)


class ObjectIdFieldMixin:
    """
    Adds an Upper-cased ID field.
    """

    @admin.display(description="ID")
    def full_object_id(self, obj):
        return mark_safe("%s" % str(obj.id).upper())

    @admin.display(description="Short ID")
    def object_id(self, obj):
        # Only first 8 characters are shown
        return mark_safe("%s" % str(obj.id)[:8].upper())


class CreateUpdateReadOnlyFieldsMixin:
    """
    Changes read only fields depending on update/create.
    """

    readonly_fields_create: List[str] = []
    readonly_fields_update: List[str] = []

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return self.readonly_fields_update
        return self.readonly_fields_create


def status_field(func):
    """
    Decorate to wrap with color coded status field.
    Return values as (COLOR, LABEL) to show colored status label.
    Return values as (LABEL,) to show the uncolored label.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        values = func(*args, **kwargs)
        if isinstance(values, str):
            return values
        return mark_safe('<span style="background: %s; padding: 4px; color: white">%s</span>' % values)

    return wrapper


def admin_image_tag(width=50, height=50):
    """
    Decorator to wrap with image field on admin panel.
    Renders an image thumbnail of given size or renders a empty box.
    The decorated function should return the image source URL/path.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            image_src = func(self, *args, **kwargs)
            if not image_src:
                return None
            if hasattr(image_src, "url"):
                image_src = getattr(image_src, "url")
            image_tag = '<img src="%s" width="%s" height="%s" style="object-fit: contain;" />'
            return mark_safe(image_tag % (image_src, width, height))

        return wrapper

    return decorator


def admin_fk_link_tag():
    """
    Decorator to wrap with foreign key field on admin panel.
    Renders a link to visit fields change page.
    The decorated function should return foreign key object.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            obj = func(self, *args, **kwargs)
            link = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id])
            link_text = str(obj)
            if len(link_text.strip()) == 0:
                link_text = _("Link")
            return mark_safe('<a href="%s">%s</a>' % (link, link_text))

        return wrapper

    return decorator


def admin_filter_link_tag(link_text, list_model):
    """
    Decorator to wrap with a button to view filtered results on admin panel.
    Renders a button to visit a specific model changelist, filtered.
    The decorated function should return the filter query parameter.

    :param link_text: Text on the button
    :param list_model: Model to show the changelist of
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            query_params = func(self, *args, **kwargs)
            link = reverse(f"admin:{list_model._meta.app_label}_{list_model._meta.model_name}_changelist")
            return mark_safe('<button><a href="%s?%s">%s</a></button>' % (link, query_params, link_text))

        return wrapper

    return decorator


def admin_pretty_print_json():
    """
    Decorator to wrap with a json field on admin panel.
    Renders a pretty printed json field.
    The decorated function should return the json field value.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            pretty_result = json.dumps(result, indent=4, sort_keys=True)
            return mark_safe("<pre>%s</pre>" % pretty_result)

        return wrapper

    return decorator


def admin_bulk_action():
    """
    Decorator to wrap with a queryset bulk action on admin panel.
    Creates an action that will perform an operation on each object in the queryset.
    The decorated function should perform the operation and return the success message.
    If None is returned, the default success message will be shown.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, queryset):
            for obj in queryset.iterator():
                try:
                    response = func(self, request=request, queryset=queryset, obj=obj)
                    if response is None:
                        response = _("Operation successful")
                    messages.add_message(request, messages.SUCCESS, _("[%s] %s") % (obj, response))
                except OperationException as e:
                    messages.add_message(request, messages.ERROR, _("[%s] %s") % (obj, e.message))

        return wrapper

    return decorator
