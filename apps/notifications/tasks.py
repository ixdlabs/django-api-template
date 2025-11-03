import structlog
from celery import shared_task
from django.utils import timezone

from apps.dashboard.models import get_current_global_settings
from apps.memberships.models import Membership
from apps.notifications.choices import NotificationTypes, SmsCampaignStates
from apps.notifications.models import Notification, SmsCampaign
from apps.notifications.services.sms_service import get_sms_service
from apps.users.models import CustomerEnrollment, User
from apps.utils.exceptions import OperationException

logger = structlog.get_logger(__name__)


@shared_task
def send_login_otp_task(phone_number: str, otp: str):
    # We dont want the OTP stored as a notification in DB, so we will send directly
    sms_service = get_sms_service()
    sms_service.send_sms(
        phone_numbers=[str(phone_number)],
        message=f"Your Login OTP for Fitconnect is {otp}",
        sms_mask=None,
    )
    logger.info("login otp sent", phone_number=phone_number)


@shared_task
def send_phone_number_change_otp_task(phone_number: str, otp: str):
    # We dont want the OTP stored as a notification in DB, so we will send directly
    sms_service = get_sms_service()
    sms_service.send_sms(
        phone_numbers=[str(phone_number)],
        message=f"Your OTP for Fitconnect is {otp}",
        sms_mask=None,
    )
    logger.info("change phone number otp sent", phone_number=phone_number)


@shared_task
def send_birthday_wish_task(enrollment_id: str):
    enrollment = CustomerEnrollment.objects.get(id=enrollment_id)
    first_name = enrollment.user.first_name
    notification = Notification.objects.create(
        title=f"🎉 Happy Birthday, {first_name}!",
        message=f"Hi {first_name}, Happy Birthday!"
        f"\nWishing you a year of strength, joy, and success. Enjoy your special day!",
        sms_message=f"Hi {first_name}, Happy Birthday!"
        f"\nWishing you a year of strength, joy, and success. Enjoy your special day!",
        notification_type=NotificationTypes.BIRTHDAY_WISH,
        data={"user_id": str(enrollment.user_id)},
        organization_id=enrollment.branch.organization_id,
        mode_push=True,
        mode_sms=True,
    )
    notification.recipient_users.add(enrollment.user)
    notification.send()


@shared_task
def send_membership_renew_reminder_task(old_membership_id: str):
    old_membership = Membership.objects.get(id=old_membership_id)
    first_name = old_membership.customer.user.first_name
    expiry_date = old_membership.end_date.isoformat()
    notification = Notification.objects.create(
        title="⚠️ Membership Expires Today",
        message=f"Hi {first_name}, your membership expires today ({expiry_date})."
        f" Renew now to keep your access and benefits active.",
        sms_message=f"Hi {first_name}, your membership expires today ({expiry_date})."
        f" Renew now to keep your access and benefits active.",
        notification_type=NotificationTypes.MEMBERSHIP_RENEW_REMINDER,
        data={"user_id": str(old_membership.customer.user_id), "old_membership_id": str(old_membership_id)},
        organization=old_membership.customer.branch.organization,
        mode_push=True,
        mode_sms=True,
    )
    notification.recipient_users.add(old_membership.customer.user)
    notification.send()


@shared_task
def send_membership_expired_reminder_task(old_membership_id: str):
    old_membership = Membership.objects.select_related("customer__user").get(id=old_membership_id)
    first_name = old_membership.customer.user.first_name
    expiry_date = old_membership.end_date.isoformat()
    notification = Notification.objects.create(
        title="🚨 Membership Expired",
        message=f"Hi {first_name}, your membership expired on {expiry_date}. "
        "Renew now to restore access and continue your fitness journey.",
        sms_message=f"Hi {first_name}, your membership expired on {expiry_date}. "
        "Renew now to restore access and continue your fitness journey.",
        notification_type=NotificationTypes.MEMBERSHIP_EXPIRY,
        data={"user_id": str(old_membership.customer.user_id), "old_membership_id": str(old_membership_id)},
        organization=old_membership.customer.branch.organization,
        mode_push=True,
        mode_sms=True,
    )
    notification.recipient_users.add(old_membership.customer.user)
    notification.send()


@shared_task
def send_welcome_message_task(user_id: str):
    user = User.objects.get(id=user_id)
    notification = Notification.objects.create(
        title="🎉 Welcome to Fitconnect",
        message=f"Hi {user.first_name}, welcome to Fitconnect!"
        f"\nManage your membership, workouts, meals, track progress & reach your goals.",
        sms_message=f"Hi {user.first_name}, welcome to Fitconnect!"
        f"\nManage your membership, workouts, meals, track progress & reach your goals.",
        notification_type=NotificationTypes.WELCOME_TO_APP,
        mode_push=True,
        mode_email=True,
    )
    notification.recipient_users.add(user)
    notification.send()


@shared_task
def send_welcome_to_branch_notification_task(enrollment_id: str):
    enrollment = CustomerEnrollment.objects.get(id=enrollment_id)
    org_name = enrollment.branch.organization.name
    branch_name = enrollment.branch.name
    first_name = enrollment.user.first_name
    notification = Notification.objects.create(
        title=f"👋 Welcome to {org_name} - {branch_name}",
        message=f"Hi {first_name}, welcome to {org_name}!"
        f"\nWe’re excited to have you training with us. Let’s grow stronger together!",
        sms_message=f"Hi {first_name}, welcome to {org_name}!"
        f"\nWe’re excited to have you training with us. Let’s grow stronger together!",
        notification_type=NotificationTypes.WELCOME_TO_BRANCH,
        data={"user_id": str(enrollment.user_id), "branch_id": str(enrollment.branch_id)},
        organization=enrollment.branch.organization,
        mode_push=True,
        mode_sms=True,
    )
    notification.recipient_users.add(enrollment.user)
    notification.send()


@shared_task
def send_sms_campaign_message_task(campaign_id: str):
    campaign = SmsCampaign.objects.get(id=campaign_id)
    if (
        not campaign
        or not campaign.group.is_active
        or campaign.state not in [SmsCampaignStates.PENDING, SmsCampaignStates.SCHEDULED]
    ):
        logger.warn("sms campaign message not sent as the required states are not met", campaign=campaign)
        return
    recipient_users = [customer.user for customer in campaign.group.customers.select_related("user")]
    notification = Notification.objects.create(
        title=campaign.name,
        message=campaign.message,
        notification_type=NotificationTypes.CUSTOM,
        organization=campaign.group.branch.organization,
        mode_sms=True,
    )
    notification.recipient_users.set(recipient_users)
    try:
        notification.send()
        campaign.state = SmsCampaignStates.COMPLETED
        campaign.message_count = len(recipient_users)
        campaign.cost = get_current_global_settings().sms_cost * campaign.message_count
        logger.info("sms campaign message sent", campaign_id=str(campaign.id))
    except OperationException as e:
        logger.error("failed to send sms campaign message", campaign_id=str(campaign.id), error=str(e))
        campaign.state = SmsCampaignStates.FAILED
    campaign.attempted_at = timezone.now()
    campaign.save()


@shared_task
def send_notification_task(notification_id: str):
    notification = Notification.objects.get(id=notification_id)
    notification.send()
