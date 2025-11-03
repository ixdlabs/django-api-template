from decimal import Decimal

from django.db.models import DecimalField, F, Sum

from apps.meal_plans.services.meal_scanner_service import get_meal_scanner_service
from apps.notifications.services.email_service import get_email_service
from apps.notifications.services.push_service import get_push_service
from apps.notifications.services.sms_service import get_sms_service
from apps.payments.choices import PaymentMethods, PaymentStates
from apps.payments.models import Payment, Payout
from apps.payments.services.payment_service import get_payment_service
from apps.utils.services import get_cache_info, get_celery_info, get_storage_info

ZERO = Decimal("0")


def dashboard_callback(request, context):
    context["celery_info"] = get_celery_info()
    context["cache_info"] = get_cache_info()
    context["storage_info"] = get_storage_info()
    context["sms_info"] = get_sms_service().get_service_info()
    context["email_info"] = get_email_service().get_service_info()
    context["payment_info"] = get_payment_service().get_service_info()
    context["push_info"] = get_push_service().get_service_info()
    context["meal_scanner_info"] = get_meal_scanner_service().get_service_info()

    payments_qs = (
        Payment.objects.filter(method=PaymentMethods.PAYHERE, state=PaymentStates.SUCCESS)
        .values("branch__organization__id", "branch__organization__name")
        .annotate(
            total_payments=Sum(
                F("original_amount") - F("discount_amount") + F("pg_fee_amount"),
                output_field=DecimalField(),
            ),
            total_pg_fee_payments=Sum(
                F("pg_fee_amount"),
                output_field=DecimalField(),
            ),
        )
    )
    payouts_map = {
        payout["organization__id"]: payout["total_completed_payouts"] or ZERO
        for payout in Payout.objects.values("organization__id").annotate(
            total_completed_payouts=Sum("paid_amount", output_field=DecimalField())
        )
    }
    org_payout_stats = []
    for payment in payments_qs:
        org_id = payment["branch__organization__id"]
        total_payments = payment["total_payments"] or ZERO
        total_pg_fee = payment["total_pg_fee_payments"] or ZERO
        total_payouts = total_payments - total_pg_fee
        total_completed_payouts = payouts_map.get(org_id, ZERO)
        total_pending_payouts = total_payouts - total_completed_payouts

        org_payout_stats.append(
            {
                "organization_name": payment["branch__organization__name"],
                "total_payments": total_payments,
                "total_pg_fee": total_pg_fee,
                "total_payouts": total_payouts,
                "total_completed_payouts": total_completed_payouts,
                "total_pending_payouts": total_pending_payouts,
            }
        )
    context["org_payout_stats"] = org_payout_stats
    return context
