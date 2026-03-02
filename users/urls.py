from django.urls import path
from .views import SignupView, LoginView, forgot_password, reset_password_page, profile_view, logout_view

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('profile/', profile_view),
    path('logout/', logout_view, name='logout'),
]
