"""Serializers for the meals application
"""
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedRelatedField
from meals.models import Meal, MealFile

class MealFileSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a MealFile. Hyperlinks are used for relationships by default.

    Serialized fields: url, id, owner, file, meal

    Attributes:
        owner:      The owner (User) of the MealFile, represented by a username. ReadOnly
        meal:       The associate meal for this MealFile, represented by a hyperlink
    """

    owner = serializers.ReadOnlyField(source="owner.username")
    meal = HyperlinkedRelatedField(
        queryset=Meal.objects.all(), view_name="meal-detail", required=False
    )

    class Meta:
        model = MealFile
        fields = ["url", "id", "owner", "file", "meal"]

    def create(self, validated_data):
        return MealFile.objects.create(**validated_data)


class MealSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a Meal. Hyperlinks are used for relationships by default.

    This serializer specifies nested serialization since a meal consists of MealFiles.

    Serialized fields: url, id, name, date, notes, calories, owner, is_veg, owner_username, files

    Attributes:
        owner_username:     Username of the owning User
        files:              Serializer for MealFiles
    """

    owner_username = serializers.SerializerMethodField()
    files = MealFileSerializer(many=True, required=False)

    class Meta:
        model = Meal
        fields = [
            "url",
            "id",
            "name",
            "date",
            "notes",
            "calories",
            "is_veg",
            "owner",
            "owner_username",
            "files",
            "assigned_athlete",
        ]
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        """Custom logic for creating MealFiles, and a Meal.

        This is needed to iterate over the files, since this serializer is nested.

        Args:
            validated_data: Validated files

        Returns:
            Meal: A newly created Meal
        """
        files_data = []
        if "files" in validated_data:
            files_data = validated_data.pop("files")
        meal = Meal.objects.create(**validated_data)

        for file_data in files_data:
            MealFile.objects.create(
                meal=meal, owner=meal.owner, file=file_data.get("file")
            )

        return meal

    def update(self, instance, validated_data):
        """Custom logic for updating a Meal.

        This is needed because each object in files must be iterated
        over and handled individually.

        Args:
            instance (Meal): Current Meal object
            validated_data: Contains data for validated fields

        Returns:
            Meal: Updated Meal instance
        """

        instance.name = validated_data.get("name", instance.name)
        instance.date = validated_data.get("date", instance.date)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.is_veg = validated_data.get("is_veg", instance.is_veg)
        instance.calories = validated_data.get("calories", instance.calories)
        instance.save()

        # Handle MealFiles

        if "files" in validated_data:
            files_data = validated_data.pop("files")
            files = instance.files

            for file, file_data in zip(files.all(), files_data):
                file.file = file_data.get("file", file.file)

            # If new files have been added, creating new MealFiles
            if len(files_data) > len(files.all()):
                for i in range(len(files.all()), len(files_data)):
                    MealFile.objects.create(
                        meal=instance,
                        owner=instance.owner,
                        file=files_data[i].get("file"),
                    )
            # Else if files have been removed, delete MealFiles
            elif len(files_data) < len(files.all()):
                for i in range(len(files_data), len(files.all())):
                    files.all()[i].delete()

        return instance

    def get_owner_username(self, obj):
        """Returns the owning user's username

        Args:
            obj (Meal): Current Meal

        Returns:
            str: Username of owner
        """
        return obj.owner.username