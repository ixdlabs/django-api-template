from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import parsers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.meal_plans.models import MealPlanAssignment
from apps.memberships.models import Membership, MembershipQuerySet
from apps.payments.choices import PaymentStates
from apps.payments.models import Payment
from apps.users.apis.employee.filters import CustomerEnrollmentEmployeeFilterSet
from apps.users.apis.employee.serializers import (
    CustomerEnrollmentDetailCombinedEmployeeSerializer,
    CustomerEnrollmentDetailEmployeeSerializer,
    CustomerEnrollmentListEmployeeSerializer,
    PhoneNumberCheckResponseSerializer,
    PhoneNumberCheckSerializer,
    UserCreateEmployeeSerializer,
    UserDetailEmployeeSerializer,
    UserPrivateMealPlanAssignmentEmployeeSerializer,
    UserPrivateMembershipEmployeeSerializer,
    UserPrivateWorkoutScheduleAssignmentEmployeeSerializer,
)
from apps.users.choices import UserTypes
from apps.users.models import CustomerEnrollment, User
from apps.utils.permissions import BranchAdmin, get_current_emp_branch_ids
from apps.workouts.models import WorkoutScheduleAssignment


class CustomerEnrollmentEmployeeViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet
):
    queryset = CustomerEnrollment.objects.select_related("user", "branch", "branch__organization")
    serializer_class = CustomerEnrollmentListEmployeeSerializer
    permission_classes = [BranchAdmin]
    parser_classes = [parsers.MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CustomerEnrollmentEmployeeFilterSet
    search_fields = ["user__first_name", "user__last_name", "user__email", "user__phone_number", "customer_sn"]

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerEnrollmentListEmployeeSerializer
        if self.action == "retrieve":
            return CustomerEnrollmentDetailCombinedEmployeeSerializer
        if self.action == "update":
            return UserDetailEmployeeSerializer
        if self.action == "partial_update":
            return UserDetailEmployeeSerializer
        if self.action == "create":
            return UserCreateEmployeeSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        branch_ids = get_current_emp_branch_ids(self.request)
        return qs.filter(branch__in=branch_ids)

    @extend_schema(responses={201: CustomerEnrollmentDetailEmployeeSerializer})
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create a new customer with a active membership."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        branch = serializer.validated_data.pop("branch")
        package = serializer.validated_data.pop("package")
        start_date = serializer.validated_data.pop("start_date")
        discount_amount = serializer.validated_data.pop("discount_amount")
        payment_method = serializer.validated_data.pop("payment_method")
        branch_ids = get_current_emp_branch_ids(self.request)
        if branch.id not in branch_ids:
            raise ValidationError({"branch": _("You don't have permission to assign this branch.")})
        if package.branch.id not in branch_ids:
            raise ValidationError({"package": _("You don't have permission to assign this package.")})
        if discount_amount > package.price:
            raise ValidationError({"discount_amount": _("Discount amount cannot be greater than package price.")})

        user = serializer.save(user_type=UserTypes.CUSTOMER)
        customer = CustomerEnrollment.objects.create(user=user, branch=branch)
        membership = Membership.objects.create(customer=customer, package=package, start_date=start_date)
        Payment.objects.create(
            source_membership=membership,
            method=payment_method,
            original_amount=package.price,
            discount_amount=discount_amount,
            currency="LKR",
            paid_date=timezone.now(),
            state=PaymentStates.SUCCESS,
        )

        res_serializer = CustomerEnrollmentDetailEmployeeSerializer(customer)
        headers = self.get_success_headers(serializer.data)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        """List all the customers of the system."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Return the requested customer."""
        customer = self.get_object()
        mem_qs = Membership.objects.get_queryset()
        assert isinstance(mem_qs, MembershipQuerySet)
        customer_data = CustomerEnrollmentDetailEmployeeSerializer(customer).data
        current = mem_qs.current_membership(customer)
        current_data = UserPrivateMembershipEmployeeSerializer(current).data if current else None
        others_qs = mem_qs.other_not_expired_memberships(customer)[:3]
        others_data = UserPrivateMembershipEmployeeSerializer(others_qs, many=True).data
        workout_qs = WorkoutScheduleAssignment.objects.get_queryset().filter(customer=customer).order_by("-created")[:3]
        workout_data = UserPrivateWorkoutScheduleAssignmentEmployeeSerializer(workout_qs, many=True).data
        # Limit to 3 most recent meal plan assignments for summary view
        # Full list available at /api/v1/employee/meal-plans/assignments/
        meal_plan_qs = (
            MealPlanAssignment.objects.get_queryset()
            .filter(customer=customer)
            .select_related("meal_plan", "meal_plan__goal")
            .annotate(meals_count=Count("meal_plan__meals"))
            .order_by("-created")[:3]
        )
        meal_plan_data = UserPrivateMealPlanAssignmentEmployeeSerializer(meal_plan_qs, many=True).data
        return Response(
            {
                "customer": customer_data,
                "current_membership": current_data,
                "other_memberships": others_data,
                "workout_schedules": workout_data,
                "meal_plans": meal_plan_data,
            }
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update the customer details."""
        partial = kwargs.pop("partial", False)
        customer = self.get_object()
        serializer = self.get_serializer(customer.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """Partially update the customer details."""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["post"])
    @transaction.atomic
    def unbind(self, request, *args, **kwargs):
        """Unbind the customer's device by clearing the access_secret of their current membership."""
        customer = self.get_object()
        mem_qs = Membership.objects.get_queryset()
        assert isinstance(mem_qs, MembershipQuerySet)
        membership = mem_qs.current_membership(customer)
        if membership is not None:
            membership.access_secret = ""
            membership.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=PhoneNumberCheckSerializer, responses={200: PhoneNumberCheckResponseSerializer})
    @action(detail=False, methods=["post"], url_path="check-phone-number")
    @transaction.atomic
    def check_phone_number(self, request, *args, **kwargs):
        """Check if a phone number is already used by a customer."""
        serializer = PhoneNumberCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        already_used = User.objects.filter(user_type=UserTypes.CUSTOMER, phone_number=phone_number).exists()
        res_serializer = PhoneNumberCheckResponseSerializer(instance={"already_used": already_used})
        return Response(res_serializer.data)
