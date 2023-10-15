from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from application.models import UserData, FriendRequest, FriendList
import json

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.joinUrl = reverse('join')
        self.loginUrl = reverse('login')
        self.logoutUrl = reverse('logout')
        self.mapUrl = reverse('map')
        self.friendListUrl = reverse('friendList')
        self.homeUrl = reverse('home')

        self.testUser1 = User.objects.create_user(username='testuser1', password='password')
        self.testUser1Data = UserData.objects.create(
            djangoUser=self.testUser1,
            latitude=1.0,
            longitude=1.0
        )

        self.testUser2 = User.objects.create_user(username='testuser2', password='password')
        self.testUser2Data = UserData.objects.create(
            djangoUser=self.testUser2,
            latitude=2.0,
            longitude=2.0
        )

    def testJoinGET(self):
        response = self.client.get(self.joinUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'join.html')

    def testLoginGET(self):
        response = self.client.get(self.loginUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def testMapGET_loggedIn(self):
        self.client.login(username='testuser1', password='password')  # Using the credentials of the test user
        response = self.client.get(self.mapUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'map.html')

    def testMapGET_notLoggedIn(self):
        response = self.client.get(self.mapUrl, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, 'login.html')  # Expecting a redirect to the login page

    def testFriendListGET(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.get(self.friendListUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'friendList.html')

    def testHomeGET(self):
        response = self.client.get(self.homeUrl, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, 'login.html')  # Expecting a redirect to the login page

    def testLoginPOST_logsInUser(self):
        response = self.client.post(self.loginUrl, {
            'username': 'testuser1',
            'password': 'password',
            'lat': 3.0,
            'lng': 3.0
        }, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'map.html')

    def testLoginPOST_badCredentials(self):
        response = self.client.post(self.loginUrl, {
            'username': 'testuser1',
            'password': 'wrongpassword'
        }, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.context['correct'])

    def testLogoutPOST(self):
        self.client.login(username='testuser1', password='password')

        response = self.client.post(self.logoutUrl, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'login.html')