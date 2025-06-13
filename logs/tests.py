from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserActivityLog
from rest_framework.test import APIClient

class UserActivityLogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass123')
        self.client = APIClient()
        self.client.login(username='tester', password='pass123')

    def test_create_log(self):
        response = self.client.post('/logs/', {'action': 'LOGIN', 'metadata': {'ip': '127.0.0.1'}}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UserActivityLog.objects.count(), 1)

    def test_get_logs(self):
        UserActivityLog.objects.create(user=self.user, action='LOGIN')
        response = self.client.get(f'/logs/{self.user.id}/')
        self.assertEqual(response.status_code, 200)

    def test_patch_status(self):
        log = UserActivityLog.objects.create(user=self.user, action='LOGIN')
        response = self.client.patch(f'/logs/{log.id}/status/', {'status': 'DONE'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'DONE')
