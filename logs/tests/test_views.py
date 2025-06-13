import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from logs.models import UserActivityLog
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from datetime import datetime, timedelta
import pytz

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def token(user):
    return Token.objects.get_or_create(user=user)[0]

@pytest.fixture
def auth_client(token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client

@pytest.mark.django_db
def test_user_activity_log_model_creation(user):
    log = UserActivityLog.objects.create(
        user=user,
        action='LOGIN',
        metadata={'ip': '127.0.0.1'}
    )
    assert log.id is not None
    assert log.action == 'LOGIN'
    assert log.metadata['ip'] == '127.0.0.1'

@pytest.mark.django_db
def test_post_user_activity_log(auth_client, user):
    url = '/logs/'
    data = {
        "action": "UPLOAD_FILE",
        "metadata": {"file_name": "test.pdf"}
    }
    response = auth_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['action'] == 'UPLOAD_FILE'

@pytest.mark.django_db
def test_get_user_logs(auth_client, user):
    UserActivityLog.objects.create(user=user, action='LOGIN')
    url = f'/logs/{user.id}/'
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 1
    assert response.data[0]['action'] == 'LOGIN'

@pytest.mark.django_db
def test_filter_logs_by_action(auth_client, user):
    UserActivityLog.objects.create(user=user, action='LOGIN')
    UserActivityLog.objects.create(user=user, action='LOGOUT')
    url = f'/logs/{user.id}/?action=LOGIN'
    response = auth_client.get(url)
    assert response.status_code == 200
    for log in response.data:
        assert log['action'] == 'LOGIN'

@pytest.mark.django_db
def test_filter_logs_by_timestamp_range(auth_client, user):
    tz = pytz.UTC
    now = datetime.now(tz)
    past = now - timedelta(days=2)
    future = now + timedelta(days=2)

    UserActivityLog.objects.create(user=user, action='LOGIN', timestamp=now)
    url = f'/logs/{user.id}/?timestamp_start={past.isoformat()}&timestamp_end={future.isoformat()}'
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 1

@pytest.mark.django_db
def test_patch_log_status(auth_client, user):
    log = UserActivityLog.objects.create(user=user, action='LOGIN')
    url = f'/logs/{log.id}/status/'
    response = auth_client.patch(url, {"status": "IN_PROGRESS"}, format='json')
    assert response.status_code == 200
    log.refresh_from_db()
    assert log.status == 'IN_PROGRESS'

@pytest.mark.django_db
def test_unauthenticated_access_denied(user):
    client = APIClient()
    url = f'/logs/{user.id}/'
    response = client.get(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_cache_sets_data(auth_client, user):
    cache.clear()
    key = f"user_logs_{user.id}"
    assert cache.get(key) is None

    UserActivityLog.objects.create(user=user, action='LOGIN')
    url = f'/logs/{user.id}/'
    response = auth_client.get(url)
    assert response.status_code == 200
    assert cache.get(key) is not None
