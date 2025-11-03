import django_filters
from django.utils import timezone

from apps.memberships.choices import CustomerMembershipStatus
from apps.memberships.models import Membership, MembershipQuerySet
from apps.users.models import CustomerEnrollment
from apps.utils.permissions import get_current_emp_organization


class CustomerEnrollmentEmployeeFilterSet(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=CustomerMembershipStatus.choices, method="membership_status_filter")
    branch = django_filters.UUIDFilter(field_name="branch_id")
    workout_schedule = django_filters.UUIDFilter(method="workout_schedule_filter")
    meal_plan = django_filters.UUIDFilter(method="meal_plan_filter")

    def membership_status_filter(self, queryset, name, value):
        if not value:
            return queryset

        organization = get_current_emp_organization(self.request)
        mem_qs = Membership.objects.get_queryset()
        assert isinstance(mem_qs, MembershipQuerySet)
        active_mem_ids = mem_qs.payment_active().time_active(organization, timezone.now()).values_list("id", flat=True)
        future_mem_ids = mem_qs.payment_active().time_future(organization, timezone.now()).values_list("id", flat=True)
        if value == "ACTIVE":
            return queryset.filter(memberships__id__in=active_mem_ids)
        if value == "INACTIVE":
            return queryset.exclude(memberships__id__in=active_mem_ids).exclude(memberships__id__in=future_mem_ids)
        if value == "FUTURE":
            return queryset.exclude(memberships__id__in=active_mem_ids).filter(memberships__id__in=future_mem_ids)
        return CustomerEnrollment.objects.none()

    def workout_schedule_filter(self, queryset, _, value):
        return queryset.filter(
            workout_schedule_assignments__workout_schedule_id=value, workout_schedule_assignments__is_active=True
        ).distinct()

    def meal_plan_filter(self, queryset, _, value):
        return queryset.filter(
            meal_plan_assignments__meal_plan_id=value, meal_plan_assignments__is_active=True
        ).distinct()

    class Meta:
        model = CustomerEnrollment
        fields = ["status", "branch"]
