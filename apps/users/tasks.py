import structlog
from celery import shared_task
from django.utils import timezone

from apps.notifications.tasks import send_birthday_wish_task
from apps.organizations.models import Organization
from apps.users.choices import UserTypes
from apps.users.models import CustomerEnrollment
from apps.utils.exceptions import OperationException

logger = structlog.get_logger(__name__)


@shared_task
def send_birthday_wish_periodic_task(*organization_ids: list[str]):
    if not organization_ids:
        raise OperationException("No organization IDs provided for birthday wish task.")

    for organization in Organization.objects.filter(id__in=organization_ids):
        today = organization.date(timezone.now())
        customers = CustomerEnrollment.objects.filter(
            branch__organization=organization,
            is_active=True,
            user__user_type=UserTypes.CUSTOMER,
            user__date_of_birth__month=today.month,
            user__date_of_birth__day=today.day,
            user__is_active=True,
        )
        for customer in customers:
            send_birthday_wish_task.delay(str(customer.id))
            logger.info("sent a birthday wish", customer_id=customer.id, name=customer.user.get_full_name())
