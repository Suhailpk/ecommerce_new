from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('store/', views.store, name='store'),
    path('store/<slug:category_slug>/', views.store, name='proudcts_slug'),
    path('store/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart_decrement/<int:product_id>/<int:cart_item_id>', views.decrement_cart_item, name='decrement_cart_item'),
    path('cart_remove/<int:product_id>/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('cart_items_number/', views.cart_items_number, name='cart_items_number'),
    path('search/', views.search, name='search'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('checkout/', views.checkout, name='checkout'),
]