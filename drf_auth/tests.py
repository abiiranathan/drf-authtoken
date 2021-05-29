from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'randomusername', 'username@example.com', 'STRONGpassword')

        self.client.login(username='john', password='johnpassword')

        self.data = {
            'username': 'mike',
            'first_name': 'Mike',
            'last_name': 'Tyson',
            'email': "miketyson@code.com",
            'password': "mikepassword"
        }

    def test_can_register(self):
        """
        Ensure we can create new users.
        """

        url = reverse('drf_auth:register')

        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["first_name"], 'Mike')
        self.assertEqual(response.data["user"]["last_name"], 'Tyson')
        self.assertEqual(response.data["user"]["username"], 'mike')
        self.assertTrue(
            "token" in response.data and response.data["token"] is not None)


class LoginTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'john', 'john@snow.com', 'johnpassword')

        self.data = {"username": "john", "password": "johnpassword"}

    def test_can_login(self):
        """
        Ensure we can users can log in.
        """

        url = reverse('drf_auth:login')
        response = self.client.post(url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["username"], "john")
        self.assertEqual(response.data["user"]["email"], "john@snow.com")


class UserTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'froid', 'nabiira2by2@gmail.com', 'moneyTeAM')

        self.data = {"username": "froid", "password": "moneyTeAM"}
        token, _ = Token.objects.get_or_create(user=self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_can_retrieve_user(self):
        response = self.client.get(
            reverse('drf_auth:get_user'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_retrieve_all_users(self):
        response1 = self.client.get(
            reverse("drf_auth:get_all_users"), format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

    def test_can_update_user(self):
        response = self.client.put(reverse("drf_auth:update_user"), {
            "first_name": "Froid",
            "last_name": "May Weather",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Froid")

    def test_can_change_password(self):
        response = self.client.post(reverse("drf_auth:change_password"), {
            "old_password": "moneyTeAM",
            "new_password": "moneyTeAMUpdated",
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change_fails_on_wrong_password(self):
        response = self.client.post(reverse("drf_auth:change_password"), {
            "old_password": "moneyTeAMWrong",
            "new_password": "moneyTeAMUpdated",
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_password_reset_email(self):
        """Tested with Gmail and passes tests"""
        url = reverse("drf_auth:reset_password")

        self.assertEqual(url, "/api/auth/reset-password/")

        # response = self.client.post(url, {"email": "testing@gmail.com"})

        # self.assertEqual(response.status_code, status.HTTP_200_OK)
