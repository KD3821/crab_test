from datetime import timedelta
import time
from django.utils import timezone
import pytest

from accounts.models import User


@pytest.mark.django_db
def test_create_user():
    date = timezone.now()
    user = User.objects.create(email='name@testing.com', name='Test123', password='TestPass00')
    delta = timedelta(seconds=0.5)
    time.sleep(5)
    assert user.timestamp - date < delta
