import io
import logging
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import path, reverse

from .middleware import StackOverflowMiddleware


def exception_view(request):
    User.objects.get(pk=1)


class StackOverflowMiddlewareTests(TestCase):
    def test_init(self):
        middleware = StackOverflowMiddleware('response')
        assert middleware.get_response == 'response'

    @patch('soet.urls.urlpatterns', new=[path('', exception_view, name='exception_view')])
    @patch('django.conf.settings.DEBUG', new=True)
    @patch.object(logging.getLogger('django.request'), attribute='error')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_user_not_found(self, fake_stdout: io.StringIO, mock_log: MagicMock):

        with pytest.raises(User.DoesNotExist):
            self.client.get(reverse('soet:exception_view'))

        assert mock_log.call_args[0][1] == 'Internal Server Error'
        assert 'Question:' in fake_stdout.getvalue()
        assert 'Best Answer:' in fake_stdout.getvalue()
