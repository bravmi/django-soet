import io
import logging
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import path, reverse
from django.views.decorators.clickjacking import xframe_options_exempt

from . import urls
from .middleware import StackOverflowMiddleware


def exception_view(request):
    User.objects.get(pk=1)


def empty_view(request):
    return HttpResponse()


@xframe_options_exempt
def empty_view_no_xframe(request):
    return HttpResponse()


urls.urlpatterns.extend(
    [
        path('exception', exception_view, name='exception_view'),
        path('empty', empty_view, name='empty_view'),
        path('empty-no-xframe', empty_view_no_xframe, name='empty_view_no_xframe'),
    ]
)


class StackOverflowMiddlewareTests(TestCase):
    def test_init(self):
        middleware = StackOverflowMiddleware('response')
        assert middleware.get_response == 'response'

    @patch('django.conf.settings.DEBUG', new=True)
    @patch.object(logging.getLogger('django.request'), attribute='error')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_user_not_found(self, fake_stdout: io.StringIO, mock_log: MagicMock):

        with pytest.raises(User.DoesNotExist):
            self.client.get(reverse('soet:exception_view'))

        assert mock_log.call_args[0][1] == 'Internal Server Error'
        assert 'Question:' in fake_stdout.getvalue()
        assert 'Best Answer:' in fake_stdout.getvalue()


class XFrameOptionsMiddlewareTests(TestCase):
    def test_xframe_header_present(self):
        response = self.client.get(reverse('soet:empty_view'))
        assert response.get('X-Frame-Options') == 'DENY'

    def test_xframe_header_absent(self):
        response = self.client.get(reverse('soet:empty_view_no_xframe'))
        assert response.get('X-Frame-Options') is None
