from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('soet/', permanent=False)),
    path('soet/', include('soet.urls')),
]
