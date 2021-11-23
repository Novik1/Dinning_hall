from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    # path('tables/', views.table_status, name='tables'),
    # path('', views.generate_order, name='generate_order'),
    # path('orders/', views.index, name='index'),
    path('waiter/', views.waiter, name='waiter'),
    path('', views.main, name='main'),
]
