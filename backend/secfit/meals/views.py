"""Contains views for the meals application. These are mostly class-based views.
"""
from rest_framework import generics, mixins
from rest_framework import permissions

from rest_framework.parsers import (
    JSONParser,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.db.models import Q
from rest_framework import filters
from meals.parsers import MultipartJsonParser
from meals.permissions import (
    IsOwner,
    IsOwnerOfMeal,
    IsReadOnly,
)
from meals.mixins import CreateListModelMixin
from meals.models import Meal, MealFile
from meals.serializers import MealSerializer
from meals.serializers import MealFileSerializer
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
import json
from collections import namedtuple
import base64, pickle
from django.core.signing import Signer


@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
            "meals": reverse("meal-list", request=request, format=format),
            "meal-files": reverse(
                "meal-file-list", request=request, format=format
            ),
        }
    )

class MealList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """Class defining the web response for the creation of a Meal, or displaying a list
    of Meals

    HTTP methods: GET, POST
    """

    serializer_class = MealSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]  # User must be authenticated to create/view meals
    parser_classes = [
        MultipartJsonParser,
        JSONParser,
    ]  # For parsing JSON and Multi-part requests
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["name", "date", "owner__username"]

    def get(self, request, *args, **kwargs):
        print(request)
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = Meal.objects.none()
        if self.request.user:
            qs = Meal.objects.filter(Q(owner=self.request.user) | Q(assigned_athlete=self.request.user)).distinct()
        return qs

class MealDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """Class defining the web response for the details of an individual Meal.

    HTTP methods: GET, PUT, DELETE
    """

    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [
        permissions.IsAuthenticated
        & IsOwner
    ]
    parser_classes = [MultipartJsonParser, JSONParser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class MealFileList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    CreateListModelMixin,
    generics.GenericAPIView,
):

    queryset = MealFile.objects.all()
    serializer_class = MealFileSerializer
    permission_classes = [permissions.IsAuthenticated & IsOwnerOfMeal]
    parser_classes = [MultipartJsonParser, JSONParser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = MealFile.objects.none()
        if self.request.user:
            qs = MealFile.objects.filter(
                Q(owner=self.request.user)).distinct()
        return qs


class MealFileDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):

    queryset = MealFile.objects.all()
    serializer_class = MealFileSerializer
    permission_classes = [
        permissions.IsAuthenticated
        & IsOwner 
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
