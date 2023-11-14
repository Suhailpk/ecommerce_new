from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # # path('verify_page/', views.verify_page, name='verify_page'),
    # # path('<auth_token>/', views.verify_user, name='verify_user'),

]