from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular import views as spec_views
from rest_framework.routers import DefaultRouter

from apps.achievements.apis.coach.views import (
    AchievementCoachViewSet,
    AchievementPhotoCoachViewSet,
)
from apps.advertisements.apis.customer.views import AdvertisementCustomerViewSet
from apps.advertisements.apis.employee.views import AdvertisementEmployeeViewSet
from apps.api_auth.apis.coach.views import AuthCoachViewSet
from apps.api_auth.apis.common.views import MeCommonViewSet, TokenCommonViewSet
from apps.api_auth.apis.customer.views import (
    AuthCustomerChangePhoneNumberViewSet,
    AuthCustomerViewSet,
)
from apps.api_auth.apis.employee.views import AuthEmployeeViewSet
from apps.attendances.apis.customer.views import AttendanceCustomerViewSet
from apps.attendances.apis.device.views import AttendanceDeviceViewSet
from apps.attendances.apis.employee.views import AttendanceEmployeeViewSet
from apps.attendances.views import (
    AttendanceQrGeneratorDemoView,
    AttendanceQrScanDemoView,
)
from apps.dashboard.apis.common.views import GlobalSettingsCommonViewSet
from apps.dashboard.apis.employee.views import DashboardEmployeeViewSet
from apps.feedbacks.apis.customer.views import FeedbackCustomerViewSet
from apps.feedbacks.apis.employee.views import FeedbackEmployeeViewSet
from apps.health_metrics.apis.customer.views import (
    HealthMetricChartsCustomerViewSet,
    HealthMetricsCustomerViewSet,
)
from apps.meal_plans.apis.coach.views import (
    FoodCoachViewSet,
    MealCoachViewSet,
    MealPlanCoachViewSet,
    MealPlanGoalCoachViewSet,
)
from apps.meal_plans.apis.customer.views import (
    MealCompletionCustomerViewSet,
    MealPlanAssignmentCustomerViewSet,
    MealPlanGoalCustomerViewSet,
    MealPlanRequestCustomerViewSet,
)
from apps.meal_plans.apis.employee.views import (
    FoodCategoryEmployeeViewSet,
    FoodEmployeeViewSet,
    MealEmployeeViewSet,
    MealEntryEmployeeViewSet,
    MealPlanAssignmentListEmployeeViewSet,
    MealPlanEmployeeViewSet,
    MealPlanGoalEmployeeViewSet,
    MealPlanRequestEmployeeViewSet,
)
from apps.memberships.apis.customer.views import (
    MembershipCustomerViewSet,
    MembershipPackageCustomerViewSet,
)
from apps.memberships.apis.employee.views import (
    MembershipEmployeeViewSet,
    MembershipPackageEmployeeViewSet,
)
from apps.notifications.apis.customer.views import (
    NotificationCustomerViewSet,
    NotificationFcmDeviceViewSet,
)
from apps.notifications.apis.employee.views import (
    SmsCampaignEmployeeViewSet,
    SmsGroupCustomerAssignmentEmployeeViewSet,
    SmsGroupEmployeeViewSet,
)
from apps.notifications.views import (
    FcmNotificationsDemoServiceWorkerView,
    FcmNotificationsDemoView,
)
from apps.organizations.apis.customer.views import BranchCustomerViewSet
from apps.organizations.apis.employee.views import (
    BranchEmployeeViewSet,
    OrganizationEmployeeViewSet,
)
from apps.payments.apis.customer.views import PaymentCustomerViewSet
from apps.payments.apis.employee.views import PaymentEmployeeViewSet
from apps.payments.apis.webhooks.views import PaymentWebhookViewSet
from apps.payments.views import PayherePaymentDemoView
from apps.products.apis.customer.views import (
    ProductCategoryCustomerViewSet,
    ProductCustomerViewSet,
    ProductOrderCustomerViewSet,
)
from apps.products.apis.employee.views import (
    ProductCategoryViewSet,
    ProductImageViewSet,
    ProductOrderEmployeeViewSet,
    ProductVariantViewSet,
    ProductViewSet,
)
from apps.users.apis.coach.views import CoachViewSet
from apps.users.apis.customer.views import CustomerViewSet
from apps.users.apis.employee.views import CustomerEnrollmentEmployeeViewSet
from apps.utils.views import PrefixedDefaultRouter
from apps.workouts.apis.customer.views import (
    WorkoutCompletionCustomerViewSet,
    WorkoutScheduleAssignmentCustomerViewSet,
    WorkoutScheduleGoalCustomerViewSet,
    WorkoutScheduleRequestCustomerViewSet,
)
from apps.workouts.apis.employee.views import (
    WorkoutCategoryEmployeeViewSet,
    WorkoutEmployeeViewSet,
    WorkoutGoalEmployeeViewSet,
    WorkoutScheduleAssignmentListEmployeeViewSet,
    WorkoutScheduleDayEmployeeViewSet,
    WorkoutScheduleDayEntryEmployeeViewSet,
    WorkoutScheduleEmployeeViewSet,
    WorkoutScheduleRequestEmployeeViewSet,
)
from config.schema import SpectacularRapiDocView

spectacular_api_view = spec_views.SpectacularAPIView.as_view()
spectacular_api_docs_view = SpectacularRapiDocView.as_view(url_name="schema")


customer_router = PrefixedDefaultRouter("customer")
customer_router.register("auth", AuthCustomerViewSet, basename="auth")
customer_router.register("change-phone", AuthCustomerChangePhoneNumberViewSet, basename="changephone")
customer_router.register("branches", BranchCustomerViewSet, basename="branches")
customer_router.register("customers", CustomerViewSet, basename="customers")
customer_router.register("notifications/fcm", NotificationFcmDeviceViewSet, basename="notificationsfcm")
customer_router.register("notifications", NotificationCustomerViewSet, basename="notifications")
customer_router.register("memberships/packages", MembershipPackageCustomerViewSet, basename="membershippackages")
customer_router.register("memberships", MembershipCustomerViewSet, basename="memberships")
customer_router.register("workouts/goals", WorkoutScheduleGoalCustomerViewSet, basename="workoutgoals")
customer_router.register("workouts/requests", WorkoutScheduleRequestCustomerViewSet, basename="workoutrequests")
customer_router.register("workouts/completions", WorkoutCompletionCustomerViewSet, basename="workoutcompletions")
customer_router.register("workouts", WorkoutScheduleAssignmentCustomerViewSet, basename="workouts")
customer_router.register("health-metrics", HealthMetricsCustomerViewSet, basename="healthmetrics")
customer_router.register("health-metrics/charts", HealthMetricChartsCustomerViewSet, basename="healthmetriccharts")
customer_router.register("feedbacks", FeedbackCustomerViewSet, basename="feedbacks")
customer_router.register("meal-plans/goals", MealPlanGoalCustomerViewSet, basename="mealplangoals")
customer_router.register("meal-plans/requests", MealPlanRequestCustomerViewSet, basename="mealplanrequests")
customer_router.register("meal-plans/completions", MealCompletionCustomerViewSet, basename="mealcompletions")
customer_router.register("meal-plans", MealPlanAssignmentCustomerViewSet, basename="mealplans")
customer_router.register("attendances", AttendanceCustomerViewSet, basename="attendances")
customer_router.register("advertisements", AdvertisementCustomerViewSet, basename="advertisements")
customer_router.register("payments", PaymentCustomerViewSet, basename="payments")
customer_router.register("products/categories", ProductCategoryCustomerViewSet, basename="product-categories")
customer_router.register("products/orders", ProductOrderCustomerViewSet, basename="product-orders")
customer_router.register("products", ProductCustomerViewSet, basename="products")


employee_router = PrefixedDefaultRouter("employee")
employee_router.register("auth", AuthEmployeeViewSet, basename="auth")
employee_router.register("attendances", AttendanceEmployeeViewSet, basename="attendances")
employee_router.register("branches", BranchEmployeeViewSet, basename="branches")
employee_router.register("organizations", OrganizationEmployeeViewSet, basename="organizations")
employee_router.register("customers", CustomerEnrollmentEmployeeViewSet, basename="customerenrollments")
employee_router.register("memberships/packages", MembershipPackageEmployeeViewSet, basename="membershippackages")
employee_router.register("memberships", MembershipEmployeeViewSet, basename="memberships")
employee_router.register("payments", PaymentEmployeeViewSet, basename="payments")
employee_router.register(
    "workouts/assignments", WorkoutScheduleAssignmentListEmployeeViewSet, basename="workoutassignments"
)
employee_router.register("workouts/requests", WorkoutScheduleRequestEmployeeViewSet, basename="workoutrequests")
employee_router.register("workouts/schedules", WorkoutScheduleEmployeeViewSet, basename="workout-schedules")
employee_router.register("workouts/days/entries", WorkoutScheduleDayEntryEmployeeViewSet, basename="workoutdayentries")
employee_router.register("workouts/days", WorkoutScheduleDayEmployeeViewSet, basename="workoutdays")
employee_router.register("workouts/goals", WorkoutGoalEmployeeViewSet, basename="workoutgoals")
employee_router.register("workouts/categories", WorkoutCategoryEmployeeViewSet, basename="workoutcategories")
employee_router.register("workouts", WorkoutEmployeeViewSet, basename="workouts")
employee_router.register(
    "meal-plans/assignments", MealPlanAssignmentListEmployeeViewSet, basename="mealplanassignments"
)
employee_router.register("meal-plans/requests", MealPlanRequestEmployeeViewSet, basename="mealplanrequests")
employee_router.register("meal-plans/plans", MealPlanEmployeeViewSet, basename="meal-plans")
employee_router.register("meal-plans/meals/entries", MealEntryEmployeeViewSet, basename="mealentries")
employee_router.register("meal-plans/meals", MealEmployeeViewSet, basename="meals")
employee_router.register("meal-plans/goals", MealPlanGoalEmployeeViewSet, basename="mealplangoals")
employee_router.register("meal-plans/foods/categories", FoodCategoryEmployeeViewSet, basename="foodcategories")
employee_router.register("meal-plans/foods", FoodEmployeeViewSet, basename="foods")
employee_router.register("feedbacks", FeedbackEmployeeViewSet, basename="feedbacks")
employee_router.register("dashboard", DashboardEmployeeViewSet, basename="dashboard")
employee_router.register("advertisements", AdvertisementEmployeeViewSet, basename="advertisements")
employee_router.register(
    "sms-groups/customers", SmsGroupCustomerAssignmentEmployeeViewSet, basename="smsgroupcustomers"
)
employee_router.register("sms-groups", SmsGroupEmployeeViewSet, basename="smsgroups")
employee_router.register("sms-campaigns", SmsCampaignEmployeeViewSet, basename="smscampaigns")
employee_router.register("products/categories", ProductCategoryViewSet, basename="product-categories")
employee_router.register("products/images", ProductImageViewSet, basename="product-images")
employee_router.register("products/variants", ProductVariantViewSet, basename="product-variants")
employee_router.register("products/orders", ProductOrderEmployeeViewSet, basename="product-orders")
employee_router.register("products", ProductViewSet, basename="products")

coach_router = PrefixedDefaultRouter("coach")
coach_router.register("auth", AuthCoachViewSet, basename="auth")
coach_router.register("coaches", CoachViewSet, basename="coaches")
coach_router.register("achievements/photos", AchievementPhotoCoachViewSet, basename="achievementphotos")
coach_router.register("achievements", AchievementCoachViewSet, basename="achievements")
coach_router.register("meal-plans/goals", MealPlanGoalCoachViewSet, basename="mealplangoals")
coach_router.register("meal-plans/foods", FoodCoachViewSet, basename="foods")
coach_router.register("meal-plans/meals", MealCoachViewSet, basename="meals")
coach_router.register("meal-plans", MealPlanCoachViewSet, basename="mealplans")

device_router = PrefixedDefaultRouter("device")
device_router.register("attendance", AttendanceDeviceViewSet, basename="attendance")

webhooks_router = PrefixedDefaultRouter("webhooks")
webhooks_router.register("payments", PaymentWebhookViewSet, basename="payment")

common_router = DefaultRouter()
common_router.register("auth/token", TokenCommonViewSet, basename="common-auth-token")
common_router.register("auth", MeCommonViewSet, basename="common-auth")
common_router.register("settings", GlobalSettingsCommonViewSet, basename="common-settings")

urlpatterns = [
    path("api/v1/", include(customer_router.urls)),
    path("api/v1/", include(employee_router.urls)),
    path("api/v1/", include(coach_router.urls)),
    path("api/v1/", include(device_router.urls)),
    path("api/v1/", include(webhooks_router.urls)),
    path("api/v1/", include(common_router.urls)),
    path("api/schema/", spectacular_api_view, name="schema"),
    path("api/docs/", spectacular_api_docs_view, name="api_docs"),
    # Admin site URLs
    path("admin/demo/payment/payhere", PayherePaymentDemoView.as_view(), name="paymentpayhere_demo"),
    path("admin/demo/qr-gen", AttendanceQrGeneratorDemoView.as_view(), name="attendance_qrgen_demo"),
    path("admin/demo/qr-scan", AttendanceQrScanDemoView.as_view(), name="attendance_qrscan_demo"),
    path("admin/demo/fcm", FcmNotificationsDemoView.as_view(), name="notification_fcm_demo"),
    path("firebase-messaging-sw.js", FcmNotificationsDemoServiceWorkerView.as_view(), name="notification_fcm_demo_sw"),
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="admin:index")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.USE_DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
