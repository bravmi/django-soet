from django.contrib.auth.models import User


def fake_view(request):
    User.objects.get(pk=1)
