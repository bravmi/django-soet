from io import StringIO
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import path, reverse

from .middleware import StackOverflowMiddleware


def fake_view(request):
    User.objects.get(pk=1)


class StackOverflowMiddlewareTests(TestCase):
    def test_init(self):
        middleware = StackOverflowMiddleware('response')
        assert middleware.get_response == 'response'

    @patch('soet.urls.urlpatterns', new=[path('', fake_view, name='fake_view')])
    @patch('django.conf.settings.DEBUG', new=True)
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_not_found(self, mock_stdout):

        with pytest.raises(User.DoesNotExist):
            self.client.get(reverse('soet:fake_view'))
        output = mock_stdout.getvalue()
        assert 'Question:' in output
        assert 'Best Answer:' in output
