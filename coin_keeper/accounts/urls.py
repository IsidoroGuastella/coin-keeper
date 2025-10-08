from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path("verify/<str:token>/", views.verify_view, name="verify"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("password-reset/", views.password_reset_request, name="password_reset_request"),
    path("password-reset-confirm/<str:token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("searching/", views.searching, name="searching"),

]
