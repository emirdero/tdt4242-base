# creating and testing permissions and test groups in django tests.
from django.contrib.auth.models import User, Permission, Group
from django.test import TestCase
from django.test import Client
from django.utils import timezone
from rest_framework import generics, mixins
from rest_framework import permissions
from workouts.permissions import (
    IsOwner,
    IsCoachAndVisibleToCoach,
    IsOwnerOfWorkout,
    IsCoachOfWorkoutAndVisibleToCoach,
    IsReadOnly,
    IsPublic,
    IsWorkoutPublic,
)
from users.models import User
from workouts.models import Workout

class Owner():
    def __init__(self, owner, workout={}, visibility="PU"):
        self.owner = owner
        self.workout = workout
        self.visibility = visibility

class Requester():
    def __init__(self, user, method="GET", data={}):
        self.user = user
        self.method = method
        self.data = data


class TestPermissions(TestCase):

    def setUp(self):
        data = {
            "username": "emir",
            "password": "emir",
            "email": "emir@email.com",
            "phone_number": "1234",
            "country": "Norway",
            "city": "Trondheim",
            "street_address": "gløshaugen 1"
        }
        # Create users
        self.user1 = User(**data)
        self.user1.save()
        data["username"] = "juni"
        self.user2 = User(**data)
        self.user2.save()
        # Create coach
        data["username"] = "coach"
        self.coach = User(**data)
        self.coach.save()
        # Assign coach to user1
        self.user1.coach = self.coach
        self.user1.save()

        # Create workout
        self.workout = Workout(date=timezone.now(), owner_id=self.user1.id, visibility="PU")
        self.workout.save()


    def test_owner(self):
        obj = Owner(self.user1)
        request = Requester(self.user1)

        # check that the owner has permission
        has_permission = IsOwner().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, True, u'Requester is the owner of the object')
        
        # check that other users do not have permission
        request = Requester(self.user2)
        has_permission = IsOwner().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, False, u'Requester is not the owner of the object')
    
    def test_owner_of_workout(self):

        # Check that owner has access
        request = Requester(self.user1, method="POST", data={"workout": "http://test.com/api/workouts/" + str(self.workout.id) + "/"})
        has_permission = IsOwnerOfWorkout().has_permission(request, {})
        self.assertEqual(has_permission,True)

        # Check that owner has object permission
        has_object_permission = IsOwnerOfWorkout().has_object_permission(request, {}, Owner(self.user1, workout=self.workout))
        self.assertEqual(has_object_permission, True)

        # Check that other users do not have access
        request = Requester(self.user2, method="POST", data={"workout": "http://test.com/api/workouts/" + str(self.workout.id) + "/"})
        has_permission = IsOwnerOfWorkout().has_permission(request, {})
        self.assertEqual(has_permission,False)

        # Check that other users have GET access
        request = Requester(self.user2, method="GET", data={"workout": "http://test.com/api/workouts/" + str(self.workout.id) + "/"})
        has_permission = IsOwnerOfWorkout().has_permission(request, {})
        self.assertEqual(has_permission,True)

        # Check that it fails with no workout
        request = Requester(self.user2, method="POST", data={"workout": None})
        has_permission = IsOwnerOfWorkout().has_permission(request, {})
        self.assertEqual(has_permission,False)

    def test_coach(self):
        obj = Owner(self.user1)
        request = Requester(self.coach)

        # check that the owner has permission
        has_permission = IsCoachAndVisibleToCoach().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, True, u'Requester is the coach of user')
        
        # check that other users do not have permission
        request = Requester(self.user2)
        has_permission = IsCoachAndVisibleToCoach().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, False, u'Requester is not the coach of user')
    
    def test_coach_workout(self):
        obj = Owner(self.user1, workout=self.workout)
        request = Requester(self.coach)

        # check that the owner has permission
        has_permission = IsCoachOfWorkoutAndVisibleToCoach().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, True, u'Requester is the coach of user')
        
        # check that other users do not have permission
        request = Requester(self.user2)
        has_permission = IsCoachOfWorkoutAndVisibleToCoach().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, False, u'Requester is not the coach of user')

    def test_public(self):
        obj = Owner(self.user1)
        request = Requester(self.user2)

        # check that it is public
        has_permission = IsPublic().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, True, u'The object is public')

        # Check that it is not public
        obj.visibility = "private"
        has_permission = IsPublic().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, False, u'The object is not public')

    def test_public_workout(self):
        obj = Owner(self.user1, workout=self.workout)
        request = Requester(self.user2)

        # check that it is public
        has_permission = IsWorkoutPublic().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, True, u'The object is public')

        # Check that it is not public
        obj.workout.visibility = "private"
        has_permission = IsWorkoutPublic().has_object_permission(request, {}, obj)
        self.assertEqual(has_permission, False, u'The object is not public')
    
    def test_read_only(self):
        request = Requester(self.user2, method="POST")
        has_permission = IsReadOnly().has_object_permission(request, {}, {})
        self.assertEqual(has_permission, False, u'POST is not read only')
        request.method = "GET"
        has_permission = IsReadOnly().has_object_permission(request, {}, {})
        self.assertEqual(has_permission, True, u'GET is read only')


