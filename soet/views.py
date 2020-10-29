from django.contrib.auth.models import User


def index(request):
    User.objects.get(pk=1)
