from django.urls import path, include
from . import views
from .views import Register
from .models import Product, Category

app_name = 'main'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('shop/', views.product_list, name='product_list'),
    path('shop/<slug:slug>/', views.product_detail,
         name='product_detail'),
    path('shop/category/<slug:category_slug>/', views.product_list,
         name='product_list_by_category'),
]