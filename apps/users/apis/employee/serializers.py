from typing import Optional

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from apps.meal_plans.models import MealPlan, MealPlanAssignment
from apps.memberships.choices import MembershipTimeStates
from apps.memberships.models import Membership, MembershipPackage, MembershipQuerySet
from apps.organizations.apis.employee.serializers import BranchEmployeeSerializer
from apps.organizations.models import Branch
from apps.payments.models import PaymentMethods
from apps.users.models import CustomerEnrollment, User
from apps.utils.cache import cache_serializer_result_per_object
from apps.workouts.choices import WorkoutLevelAssignments
from apps.workouts.models import WorkoutScheduleAssignment, WorkoutScheduleDayEntry

# User
# ----------------------------------------------------------------------------------------------------------------------


class UserDetailEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "photo",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "nic_number",
            "address_line1",
            "address_line2",
            "address_city",
            "address_state",
            "address_zip",
            "emergency_contact_name",
            "emergency_contact_phone_number",
            "recent_surgery",
            "recent_surgery_notes",
            "health_complications",
            "health_complications_notes",
            "last_login",
            "date_joined",
        ]
        read_only_fields = ["id", "last_login", "date_joined"]


class UserCreateEmployeeSerializer(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), write_only=True)
    package = serializers.PrimaryKeyRelatedField(queryset=MembershipPackage.objects.all(), write_only=True)
    start_date = serializers.DateField(write_only=True)
    payment_method = serializers.ChoiceField(choices=PaymentMethods.choices, write_only=True)
    discount_amount = serializers.DecimalField(min_value=0, max_digits=8, decimal_places=2, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "photo",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
            "nic_number",
            "address_line1",
            "address_line2",
            "address_city",
            "address_state",
            "address_zip",
            "emergency_contact_name",
            "emergency_contact_phone_number",
            "recent_surgery",
            "recent_surgery_notes",
            "health_complications",
            "health_complications_notes",
            "branch",
            "package",
            "start_date",
            "payment_method",
            "last_login",
            "date_joined",
            "discount_amount",
        ]
        read_only_fields = ["id", "last_login", "date_joined"]


class UserListEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "photo",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "last_login",
            "date_joined",
        ]


class PhoneNumberCheckSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)


class PhoneNumberCheckResponseSerializer(serializers.Serializer):
    already_used = serializers.BooleanField()


# Membership
# ----------------------------------------------------------------------------------------------------------------------


class UserPrivateMembershipEmployeeSerializer(serializers.ModelSerializer):
    package_name = serializers.SerializerMethodField()
    is_bound = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ["id", "start_date", "end_date", "package_name", "membership_state", "created", "modified", "is_bound"]

    def get_package_name(self, obj) -> str:
        return obj.package.name

    def get_is_bound(self, obj) -> bool:
        return bool(obj.access_secret)


# Workout Plans
# ----------------------------------------------------------------------------------------------------------------------


class UserPrivateWorkoutScheduleAssignmentEmployeeSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField()
    workout_schedule_id = serializers.UUIDField(source="workout_schedule.id", read_only=True)

    class Meta:
        model = WorkoutScheduleAssignment
        fields = [
            "id",
            "title",
            "start_date",
            "is_active",
            "duration_days",
            "level",
            "exercises",
            "workout_schedule_id",
            "created",
            "modified",
        ]

    def get_title(self, obj) -> str:
        return obj.workout_schedule.title

    def get_duration_days(self, obj) -> int:
        return obj.workout_schedule.duration_days

    def get_level(self, obj) -> WorkoutLevelAssignments:
        return obj.workout_schedule.level

    def get_exercises(self, obj) -> int:
        return WorkoutScheduleDayEntry.objects.filter(
            workout_schedule_day__workout_schedule=obj.workout_schedule
        ).count()


# Meal Plans
# ----------------------------------------------------------------------------------------------------------------------


class MealPlanPrivateEmployeeSerializer(serializers.ModelSerializer):
    goal_name = serializers.CharField(source="goal.name", read_only=True)

    class Meta:
        model = MealPlan
        fields = [
            "id",
            "title",
            "duration_days",
            "goal_name",
        ]


class UserPrivateMealPlanAssignmentEmployeeSerializer(serializers.ModelSerializer):
    meal_plan = MealPlanPrivateEmployeeSerializer(read_only=True)
    meals = serializers.IntegerField(source="meals_count", read_only=True)

    class Meta:
        model = MealPlanAssignment
        fields = [
            "id",
            "meal_plan",
            "start_date",
            "is_active",
            "meals",
            "created",
            "modified",
        ]


# Customer Enrollment
# ----------------------------------------------------------------------------------------------------------------------


class CustomerEnrollmentListEmployeeSerializer(serializers.ModelSerializer):
    customer_sn = serializers.CharField()
    user = UserListEmployeeSerializer()
    branch = BranchEmployeeSerializer()
    current_membership_name = serializers.SerializerMethodField()
    current_membership_time_state = serializers.SerializerMethodField()

    class Meta:
        model = CustomerEnrollment
        fields = [
            "id",
            "sn",
            "customer_sn",
            "user",
            "branch",
            "current_membership_name",
            "current_membership_time_state",
            "is_active",
            "created",
            "modified",
        ]

    def get_current_membership_name(self, obj) -> Optional[str]:
        current_membership = self._get_current_relevant_membership(obj)
        if current_membership is not None:
            return current_membership.package.name
        return None

    def get_current_membership_time_state(self, obj) -> Optional[MembershipTimeStates]:
        current_membership = self._get_current_relevant_membership(obj)
        if current_membership is not None:
            return current_membership.time_state
        return None

    @cache_serializer_result_per_object("current_relevant_membership")
    def _get_current_relevant_membership(self, obj):
        qs = Membership.objects.get_queryset()
        assert isinstance(qs, MembershipQuerySet)
        return qs.select_related("customer__branch__organization", "package").current_relevant_membership(obj)


class CustomerEnrollmentDetailEmployeeSerializer(serializers.ModelSerializer):
    customer_sn = serializers.CharField()
    user = UserDetailEmployeeSerializer()
    branch = BranchEmployeeSerializer()

    class Meta:
        model = CustomerEnrollment
        fields = ["id", "sn", "customer_sn", "user", "branch", "is_active", "created", "modified"]


class CustomerEnrollmentDetailCombinedEmployeeSerializer(serializers.Serializer):
    customer = CustomerEnrollmentDetailEmployeeSerializer()
    current_membership = UserPrivateMembershipEmployeeSerializer(allow_null=True)
    other_memberships = UserPrivateMembershipEmployeeSerializer(many=True)
    workout_schedules = UserPrivateWorkoutScheduleAssignmentEmployeeSerializer(many=True)
    meal_plans = UserPrivateMealPlanAssignmentEmployeeSerializer(many=True)
