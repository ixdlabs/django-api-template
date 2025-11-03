from django.core.exceptions import ValidationError as CoreValidationError
from drf_standardized_errors.handler import ExceptionHandler
from rest_framework.exceptions import ValidationError


class CustomExceptionHandler(ExceptionHandler):
    def convert_known_exceptions(self, exc: Exception) -> Exception:
        if isinstance(exc, CoreValidationError):
            if hasattr(exc, "message_dict"):
                return ValidationError(detail=exc.message_dict)
            return ValidationError(detail=exc.messages)
        return super().convert_known_exceptions(exc)
