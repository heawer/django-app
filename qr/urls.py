from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from app import views

urlpatterns = [
    path('', include('app.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('accounts/register/', views.register, name='register'),
]
