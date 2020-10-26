import contextlib
import io
import logging
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
    def test_user_not_found(self):

        with contextlib.redirect_stdout(io.StringIO()) as fake_stdout:
            with self.assertLogs(logging.getLogger('django.request'), level=logging.ERROR) as fake_log:
                with pytest.raises(User.DoesNotExist):
                    self.client.get(reverse('soet:fake_view'))
                assert 'Internal Server Error' in fake_log.output[0]
            assert 'Question:' in fake_stdout.getvalue()
            assert 'Best Answer:' in fake_stdout.getvalue()
