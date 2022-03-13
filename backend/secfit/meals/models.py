"""Contains the models for the meals Django application. Users
log meals (Meal). The user can also upload files (MealFile) .
"""
import os
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import get_user_model


class OverwriteStorage(FileSystemStorage):
    """Filesystem storage for overwriting files. Currently unused."""

    def get_available_name(self, name, max_length=None):
        """https://djangosnippets.org/snippets/976/
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Args:
            name (str): Name of the file
            max_length (int, optional): Maximum length of a file name. Defaults to None.
        """
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))


# Create your models here.
class Meal(models.Model):
    """Django model for a meal that users can log.

    A meal has several attributes, and files uploaded by the user.

    Attributes:
        name:        Name of the meal
        date:        Date and time the meal was consumed
        notes:       Notes about the meal
        calories:    Total amount of calories in the meal
        is_veg:      Whether the meal was vegetarian or not
        owner:       User that logged the meal
    """

    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    notes = models.TextField()
    calories = models.IntegerField()
    is_veg = models.BooleanField(default=False)
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="meals"
    )
    assigned_athlete = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="coach_meals", null=True, default=None
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.name

def meal_directory_path(instance, filename):
    """Return path for which meal files should be uploaded on the web server

    Args:
        instance (MealFile): MealFile instance
        filename (str): Name of the file

    Returns:
        str: Path where workout file is stored
    """
    return f"meals/{instance.meal.id}/{filename}"

class MealFile(models.Model):
    """Django model for file associated with a meal. Basically a wrapper.

    Attributes:
        meal:    The meal for which this file has been uploaded
        owner:   The user who uploaded the file
        file:    The actual file that's being uploaded
    """

    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="files")
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="meal_files"
    )
    file = models.FileField(upload_to=meal_directory_path)
