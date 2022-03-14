"""Contains custom DRF permissions classes for the meals app
"""
from rest_framework import permissions
from meals.models import Meal


class IsOwner(permissions.BasePermission):
    """Checks whether the requesting user is also the owner of the existing object or the assigned athlete"""

    def has_object_permission(self, request, view, obj):
        return (obj.owner == request.user) or (obj.assigned_athlete == request.user)


class IsOwnerOfMeal(permissions.BasePermission):
    """Checks whether the requesting user is also the owner of the new or existing object or the assigned athlete"""

    def has_permission(self, request, view):
        if request.method == "POST":
            if request.data.get("meal"):
                meal_id = request.data["meal"].split("/")[-2]
                meal = Meal.objects.get(pk=meal_id)
                if meal:
                    return (meal.owner == request.user) or (meal.assigned_athlete == request.user)
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return obj.meal.owner == request.user

class IsReadOnly(permissions.BasePermission):
    """Checks whether the HTTP request verb is only for retrieving data (GET, HEAD, OPTIONS)"""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
