from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from application.models import UserData, FriendRequest, FriendList

class TestViews(TestCase):

    def setUp(self):
        # Setting up for the test case
        self.client = Client()
        self.joinUrl = reverse('join')
        self.loginUrl = reverse('login')
        self.logoutUrl = reverse('logout')
        self.mapUrl = reverse('map')
        self.friendListUrl = reverse('friendList')
        self.homeUrl = reverse('home')
        self.distanceUrl = reverse('setDistancePreference')
        self.colorUrl = reverse('setColorPreference')
        self.iconUrl = reverse('setIconPreference')

        # Create test users and their respective data
        self.testUser1 = User.objects.create_user(username='testuser1', password='password')
        self.testUser1Data = UserData.objects.create(djangoUser=self.testUser1, latitude=1.0, longitude=1.0)
        _, _ = FriendList.objects.get_or_create(user=self.testUser1)

        self.testUser2 = User.objects.create_user(username='testuser2', password='password')
        self.testUser2Data = UserData.objects.create(djangoUser=self.testUser2, latitude=2.0, longitude=2.0)
        _, _ = FriendList.objects.get_or_create(user=self.testUser2)

    def testJoin(self):
        # Test to ensure the join page is accessible
        response = self.client.get(self.joinUrl)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'join.html')

    def testLogin(self):
        # Test to ensure the login page is accessible
        response = self.client.get(self.loginUrl)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def testMap(self):
        # Test to check if the map page is functioning when logged in
        self.client.login(username='testuser1', password='password')
        response = self.client.get(self.mapUrl)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'map.html')

    def testMapNotLoggedIn(self):
        # Test to ensure the map page redirects to login when not logged in
        response = self.client.get(self.mapUrl, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, 'login.html')

    def testFriendList(self):
        # Test to ensure the friend list page is accessible when logged in
        self.client.login(username='testuser1', password='password')
        response = self.client.get(self.friendListUrl)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'friendList.html')

    def testHomeNotLoggedIn(self):
        # Test to ensure home page redirects to login when not logged in
        response = self.client.get(self.homeUrl, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, 'login.html')

    def testLoginCorrect(self):
        # Test to validate the login functionality with correct credentials
        response = self.client.post(self.loginUrl, {'username': 'testuser1', 'password': 'password', 'lat': 3.0, 'lng': 3.0}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'map.html')

    def testLoginInvalid(self):
        # Test to validate the login functionality with incorrect credentials
        response = self.client.post(self.loginUrl, {'username': 'testuser1', 'password': 'wrongpassword'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.context['correct'])

    def testLogout(self):
        # Test to validate the logout functionality
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.logoutUrl, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

    def testSendFriendReq(self):
        # Test to validate sending a friend request
        self.client.login(username='testuser1', password='password')
        response = self.client.post(reverse('sendFriendRequest'), {'username1': 'testuser2'})
        self.assertEquals(response.status_code, 302)  # Expecting a successful redirection
        self.assertTrue(FriendRequest.objects.filter(sender=self.testUser1, receiver=self.testUser2).exists())

    def testAcceptFriendReq(self):
        # Test to validate accepting a friend request
        self.client.login(username='testuser1', password='password')
        friend_request = FriendRequest.objects.create(sender=self.testUser2, receiver=self.testUser1)
        response = self.client.get(reverse('acceptFriendRequest', args=[friend_request.id]))
        self.assertEquals(response.status_code, 302)  # Expecting a successful redirection
        self.assertTrue(self.testUser1.user.friends.filter(pk=self.testUser2.pk).exists())
        self.assertTrue(self.testUser2.friends.filter(pk=self.testUser1.user.pk).exists())

    def testDeclineFriendReq(self):
        # Test to validate declining a friend request
        self.client.login(username='testuser1', password='password')
        friend_request = FriendRequest.objects.create(sender=self.testUser2, receiver=self.testUser1)
        response = self.client.get(reverse('declineFriendRequest', args=[friend_request.id]))
        self.assertEquals(response.status_code, 302)  # Expecting a successful redirection
        self.assertFalse(FriendRequest.objects.filter(pk=friend_request.pk).exists())

    def testCancelFriendReq(self):
        # Test to validate the cancellation of a sent friend request
        self.client.login(username='testuser1', password='password')
        friend_request = FriendRequest.objects.create(sender=self.testUser1, receiver=self.testUser2)
        response = self.client.get(reverse('cancelFriendRequest', args=[friend_request.id]))
        self.assertEquals(response.status_code, 302)  # Expecting a successful redirection
        self.assertFalse(FriendRequest.objects.filter(pk=friend_request.pk).exists())

    def testRemoveFriend(self):
        # Test to validate the removal of a friend from the friend list
        self.client.login(username='testuser1', password='password')
        self.testUser1.user.friends.add(self.testUser2)
        self.testUser2.friends.add(self.testUser1.user)
        response = self.client.get(reverse('removeFriend', args=[self.testUser2.pk]))
        self.assertEquals(response.status_code, 302)  # Expecting a successful redirection
        self.assertFalse(self.testUser1.user.friends.filter(pk=self.testUser2.pk).exists())
        self.assertFalse(self.testUser2.friends.filter(pk=self.testUser1.user.pk).exists())

    def testSetDistanceForm(self):
        # Test to validate the distance preference form
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.distanceUrl, {'distance': 2})
        userD = UserData.objects.get(djangoUser=self.testUser1)
        self.assertEqual(userD.distancePreference, 2)
        self.assertEqual(response.status_code, 302)  # Expecting a successful redirection

    def testSetColorForm(self):
        # Test to validate the color preference form
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.colorUrl, {'color': 1})
        userD = UserData.objects.get(djangoUser=self.testUser1)
        self.assertEqual(userD.colorPreference, 1)
        self.assertEqual(response.status_code, 302)  # Expecting a successful redirection

    def testSetIconForm(self):
        # Test to validate the icon preference form
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.iconUrl, {'icon': 2})
        userD = UserData.objects.get(djangoUser=self.testUser1)
        self.assertEqual(userD.iconPreference, 2)
        self.assertEqual(response.status_code, 302)  # Expecting a successful redirection
