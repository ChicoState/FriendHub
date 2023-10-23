from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from application.models import UserData, FriendRequest, FriendList
from .forms import DistancePreferenceForm, IconPreferenceForm, ColorPreferenceForm

class TestViews(TestCase):

    def setUp(self):
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

        # Create User 1
        self.testUser1 = User.objects.create_user(username='testuser1', password='password')
        self.testUser1Data = UserData.objects.create(
            djangoUser=self.testUser1,
            latitude=1.0,
            longitude=1.0
        )
        _, _ = FriendList.objects.get_or_create(user= self.testUser1)

        # Create User 2
        self.testUser2 = User.objects.create_user(username='testuser2', password='password')
        self.testUser2Data = UserData.objects.create(
            djangoUser=self.testUser2,
            latitude=2.0,
            longitude=2.0
        )
        _, _ = FriendList.objects.get_or_create(user= self.testUser2)

    # Test Join
    def testJoin(self):
        response = self.client.get(self.joinUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'join.html')
    # Test Login
    def testLogin(self):
        response = self.client.get(self.loginUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    # If Map Page Is Up
    def testMap(self):
        self.client.login(username='testuser1', password='password')  # Using the credentials of the test user
        response = self.client.get(self.mapUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'map.html')

    # Test Map Redirect
    def testMapNotLoggedIn(self):
        response = self.client.get(self.mapUrl, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, 'login.html')  # Expecting a redirect to the login page

    # If FriendList's Page Is Up
    def testFriendList(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.get(self.friendListUrl)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'friendList.html')

    # Test Redirect
    def testHomeNotLoggedIn(self):
        response = self.client.get(self.homeUrl, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.redirect_chain)
        self.assertTemplateUsed(response, 'login.html')  # Expecting a redirect to the login page

    # Test User Login
    def testLoginCorrect(self):
        response = self.client.post(self.loginUrl, {
            'username': 'testuser1',
            'password': 'password',
            'lat': 3.0,
            'lng': 3.0
        }, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'map.html')
    
    # Test's Login W/ Invalid Credentials
    def testLoginInvalid(self):
        response = self.client.post(self.loginUrl, {
            'username': 'testuser1',
            'password': 'wrongpassword'
        }, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.context['correct'])
    
    # Tests User Logout
    def testLogout(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.logoutUrl, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'login.html')

    # Send Friend Request
    def testSendFriendReq(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.post(reverse('sendFriendRequest'), {'username1': 'testuser2'})
        self.assertEquals(response.status_code, 302)  # Check for redirect, meaning the request was processed
        # Check if FriendRequest was created
        self.assertTrue(FriendRequest.objects.filter(sender=self.testUser1, receiver=self.testUser2).exists())

    # Test Accept Friend Request
    def testAcceptFriendReq(self):
        self.client.login(username='testuser1', password='password')
        friend_request = FriendRequest.objects.create(sender=self.testUser2, receiver=self.testUser1)  # Mock a friend request

        response = self.client.get(reverse('acceptFriendRequest', args=[friend_request.id]))
        self.assertEquals(response.status_code, 302)  # Check for redirect, meaning the request was processed

        # Check if users are now friends
        self.assertTrue(self.testUser1.user.friends.filter(pk=self.testUser2.pk).exists())
        self.assertTrue(self.testUser2.friends.filter(pk=self.testUser1.user.pk).exists())

    # Test Decline Friend Request
    def testDeclineFriendReq(self):
        self.client.login(username='testuser1', password='password')
        friend_request = FriendRequest.objects.create(sender=self.testUser2, receiver=self.testUser1)  # Mock a friend request

        response = self.client.get(reverse('declineFriendRequest', args=[friend_request.id]))
        self.assertEquals(response.status_code, 302)  # Check for redirect, meaning the request was processed

        # Check that the FriendRequest no longer exists
        self.assertFalse(FriendRequest.objects.filter(pk=friend_request.pk).exists())

    # Test Cancel Sent Friend Req
    def testCancelFriendReq(self):
        self.client.login(username='testuser1', password='password')
        friend_request = FriendRequest.objects.create(sender=self.testUser1, receiver=self.testUser2)  # Mock a friend request

        response = self.client.get(reverse('cancelFriendRequest', args=[friend_request.id]))
        self.assertEquals(response.status_code, 302)  # Check for redirect, meaning the request was processed

        # Check that the FriendRequest no longer exists
        self.assertFalse(FriendRequest.objects.filter(pk=friend_request.pk).exists())

    def testRemoveFriend(self):
        self.client.login(username='testuser1', password='password')

        # Mocking the users being friends initially
        self.testUser1.user.friends.add(self.testUser2)
        self.testUser2.friends.add(self.testUser1.user)

        response = self.client.get(reverse('removeFriend', args=[self.testUser2.pk]))
        self.assertEquals(response.status_code, 302)  # Check for redirect, meaning the request was processed

        # Check that the users are no longer friends
        self.assertFalse(self.testUser1.user.friends.filter(pk=self.testUser2.pk).exists())
        self.assertFalse(self.testUser2.friends.filter(pk=self.testUser1.user.pk).exists())        

    def testValidDistanceForm(self):
        form = DistancePreferenceForm(data={'distance': 2})
        self.assertTrue(form.is_valid())

    def testValidColorForm(self):
        form = ColorPreferenceForm(data={'color': 1})
        self.assertTrue(form.is_valid())

    def testValidIconForm(self):
        form = IconPreferenceForm(data={'icon': 2})
        self.assertTrue(form.is_valid())

    def testSetDistanceForm(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.distanceUrl, {'distance': 2})
        self.testUser1.refresh_from_db()
        self.assertEqual(self.testUser1.distancePreference, 2)
        self.assertEqual(response.status_code, 302)  # 302 is the status code for a successful redirect

    def testSetColorForm(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.colorUrl, {'color': 1})
        self.testUser1.refresh_from_db()
        self.assertEqual(self.testUser1.colorPreference, 1)
        self.assertEqual(response.status_code, 302)

    def testSetIconForm(self):
        self.client.login(username='testuser1', password='password')
        response = self.client.post(self.iconUrl, {'icon': 2})
        self.testUser1.refresh_from_db()
        self.assertEqual(self.testUser1.iconPreference, 2)
        self.assertEqual(response.status_code, 302)