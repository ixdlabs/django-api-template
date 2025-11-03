from typing import Optional

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, UUIDModel
from phonenumber_field.modelfields import PhoneNumberField

from apps.organizations.models import Branch, Organization
from apps.users.choices import EmployeeRoles, Genders, ProfileHeadingChoices, UserTypes

# User
# ----------------------------------------------------------------------------------------------------------------------


class User(UUIDModel, AbstractUser):
    user_type = models.CharField(max_length=15, choices=UserTypes.choices, default=UserTypes.UNSET)
    username = models.CharField(max_length=63, unique=True)

    photo = models.ImageField(null=True, blank=True)
    first_name = models.CharField(max_length=31, blank=True)
    last_name = models.CharField(max_length=31, blank=True)
    email = models.EmailField(blank=True, null=True)  # type: ignore
    phone_number = PhoneNumberField(null=True, blank=True, help_text="This is required for customers.")
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=7, choices=Genders.choices, default=Genders.MALE)
    nic_number = models.CharField(verbose_name="NIC/ID number", max_length=31, blank=True)

    address_line1 = models.CharField(verbose_name="address line 1", max_length=127, blank=True)
    address_line2 = models.CharField(verbose_name="address line 2", max_length=127, blank=True)
    address_city = models.CharField(verbose_name="city", max_length=127, blank=True)
    address_state = models.CharField(verbose_name="state/province", max_length=127, blank=True)
    address_zip = models.CharField(verbose_name="zip/postal code", max_length=31, blank=True)

    emergency_contact_name = models.CharField(verbose_name="emergency contact name", max_length=127, blank=True)
    emergency_contact_phone_number = PhoneNumberField(verbose_name="emergency contact phone", null=True, blank=True)
    recent_surgery = models.BooleanField(verbose_name="recent surgery", default=False)
    recent_surgery_notes = models.TextField(verbose_name="recent surgery notes", blank=True)
    health_complications = models.BooleanField(verbose_name="health complications", default=False)
    health_complications_notes = models.TextField(verbose_name="health complications notes", blank=True)

    emp_organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name="employees",
        help_text="This is only required for employees.",
        null=True,
        blank=True,
    )
    emp_role = models.CharField(
        max_length=15,
        choices=EmployeeRoles.choices,
        help_text="This is only required for employees.",
        default=EmployeeRoles.BRANCH_ADMIN,
    )
    emp_permission = models.ForeignKey(
        "EmployeePermission",
        models.SET_NULL,
        related_name="users",
        help_text="This is only required for employees.",
        null=True,
        blank=True,
    )

    cover_photo = models.ImageField(upload_to="user_cover_photos/", null=True, blank=True)
    profile_bio = models.TextField(blank=True)
    profile_heading = models.CharField(max_length=30, blank=True, choices=ProfileHeadingChoices.choices)

    class Meta:
        ordering = ["-date_joined"]

    def clean(self):
        if self.user_type == UserTypes.CUSTOMER and self.phone_number is None:
            raise ValidationError({"phone_number": [_("Phone number must be set for a customer")]})
        if self.user_type == UserTypes.EMPLOYEE and self.emp_organization is None:
            raise ValidationError({"emp_organization": [_("Organization must be set for an employee")]})
        if self.user_type == UserTypes.EMPLOYEE and self.emp_permission is not None:
            if self.emp_permission.organization != self.emp_organization:
                raise ValidationError(
                    {"emp_permission": [_("Permission must belong to the same organization as the employee")]}
                )
        if self.user_type == UserTypes.CUSTOMER:
            if User.objects.filter(username=self.phone_number).exclude(pk=self.pk).exists():
                raise ValidationError({"phone_number": [_("This phone number is already registered.")]})

    def save(self, *args, **kwargs):
        if self.user_type == UserTypes.CUSTOMER:
            self.username = str(self.phone_number)
            self.emp_organization = None
            self.is_staff = False
            self.set_unusable_password()
        if self.user_type == UserTypes.EMPLOYEE:
            self.is_staff = False
        if self.user_type == UserTypes.UNSET:
            self.emp_organization = None
        self.full_clean()
        super().save(*args, **kwargs)

    @cached_property
    def cus_enrollment(self) -> Optional["CustomerEnrollment"]:
        if self.user_type != UserTypes.CUSTOMER:
            return None

        # Currently we assume there is one and only one branch enrollment for a customer.
        # If they have no branch enrollments, then the user setup is incomplete.
        # If they have more than one, the latest enrolled one is selected.
        return self.branch_enrollments_cus.filter(is_active=True).first()

    @cached_property
    def organization(self) -> Optional["Organization"]:
        if self.user_type == UserTypes.EMPLOYEE:
            return self.emp_organization
        if self.user_type == UserTypes.CUSTOMER and self.cus_enrollment:
            return self.cus_enrollment.branch.organization
        return None

    def __str__(self):
        return self.get_full_name()


# Enrollments
# ----------------------------------------------------------------------------------------------------------------------


class CustomerEnrollment(UUIDModel, TimeStampedModel, models.Model):
    sn = models.PositiveIntegerField(editable=False)
    customer_sn = models.CharField(max_length=255, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="branch_enrollments_cus")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="customer_enrollments")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "enrolled branch (customer)"
        verbose_name_plural = "enrolled branches (customer)"
        constraints = [
            models.UniqueConstraint(fields=["user", "branch"], name="unique_branch_user_customer"),
            models.UniqueConstraint(fields=["branch", "sn"], name="unique_branch_customer_sn"),
        ]

    def clean(self):
        if not hasattr(self, "user"):
            return
        if self.user.user_type != UserTypes.CUSTOMER:
            raise ValidationError({"user": "User must be a customer to be added to a branch."})

    def save(self, *args, **kwargs):
        if hasattr(self, "user") and hasattr(self, "branch"):
            # Current logic is to remove make all previous enrollments disabled.
            # This will ensure that there is only one active enrollment at all times.
            if self.is_active:
                CustomerEnrollment.objects.filter(user=self.user).exclude(pk=self.pk).update(is_active=False)
            # If SN is not set, calculate the next SN for the branch
            if self._state.adding or self.sn is None:
                max_sn_qs = CustomerEnrollment.objects.filter(branch=self.branch).aggregate(max_sn=models.Max("sn"))
                self.sn = (max_sn_qs.get("max_sn") or 0) + 1
            # Update the calculated field of customer sn in the specified format
            # We don not handle the case of organization/branch code changing after the sn is calculated yet
            self.customer_sn = f"{self.branch.organization.code}/{self.branch.code}/{self.sn:04d}"

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.branch} / {self.user}"


class EmployeeEnrollment(UUIDModel, TimeStampedModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="branch_enrollments_emp")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="employee_enrollments")

    class Meta:
        ordering = ["-created"]
        verbose_name = "enrolled branch (employee)"
        verbose_name_plural = "enrolled branches (employee)"
        constraints = [
            models.UniqueConstraint(fields=["user", "branch"], name="unique_branch_user_employee"),
        ]

    def clean(self):
        if not hasattr(self, "user"):
            return
        if self.user.user_type != UserTypes.EMPLOYEE:
            raise ValidationError({"user": _("User must be an employee to be added to a branch.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.branch} / {self.user}"


class EmployeePermission(UUIDModel, TimeStampedModel, models.Model):
    organization = models.ForeignKey(
        Organization,
        models.CASCADE,
        related_name="employee_permissions",
        help_text="Organization this permission belongs to.",
    )
    name = models.CharField(max_length=100, help_text="Name of the permission level")
    coach_access = models.BooleanField(default=False, help_text="Grants access to coach-specific features")
    dashboard_financial_access = models.BooleanField(
        default=False, help_text="Grants access to financial dashboard features"
    )

    class Meta:
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_organization_permission_name"),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.organization.name} / {self.name}"
