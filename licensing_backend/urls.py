"""
URL configuration for licensing_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import home, auth_me, auth_register, auth_users_list

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include("licensing.urls")),
    path("api/auth/token/", obtain_auth_token, name="api-token-auth"),
    path("api/auth/register/", auth_register, name="api-auth-register"),
    path("api/auth/me/", auth_me, name="api-auth-me"),
    path("api/auth/users/", auth_users_list, name="api-auth-users"),
]
