from django.urls import path
from . import views


urlpatterns = [
    path('order_product/', views.order, name='order_product'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),

]