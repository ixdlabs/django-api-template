from django.db import models


class UserTypes(models.TextChoices):
    UNSET = "UNSET", "Unset"
    CUSTOMER = "CUSTOMER", "Customer"
    EMPLOYEE = "EMPLOYEE", "Employee"


class Genders(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


class EmployeeRoles(models.TextChoices):
    BRANCH_ADMIN = "BRANCH_ADMIN", "Branch Admin"
    ORG_ADMIN = "ORG_ADMIN", "Org Admin"


class ProfileHeadingChoices(models.TextChoices):
    PERSONAL_TRAINER = "PERSONAL_TRAINER", "Personal Trainer"
    FITNESS_COACH = "FITNESS_COACH", "Fitness Coach"
    STRENGTH_CONDITIONING_COACH = "STRENGTH_CONDITIONING_COACH", "Strength & Conditioning Coach"
    GYM_INSTRUCTOR = "GYM_INSTRUCTOR", "Gym Instructor"
    GROUP_FITNESS_INSTRUCTOR = "GROUP_FITNESS_INSTRUCTOR", "Group Fitness Instructor"
    EXERCISE_SPECIALIST = "EXERCISE_SPECIALIST", "Exercise Specialist"
