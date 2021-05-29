from django.urls import path

from . import views

app_name = "drf_auth"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("logout/", views.logout, name="logout"),
    path("user/", views.get_user, name="get_user"),
    path("users/", views.get_all_users, name="get_all_users"),
    path("update-user/", views.update_user, name="update_user"),
    path("change-password/", views.change_password, name="change_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("reset_password_confirmation/<uidb64>/<token>/",
         views.reset_password_confirmation,
         name="reset_password_confirmation"),
]
