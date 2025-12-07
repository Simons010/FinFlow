from django.urls import path
from . import views

app_name = 'finflow'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
]
