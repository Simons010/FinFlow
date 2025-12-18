from django.urls import path
from . import views

app_name = 'finflow'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/update/<int:pk>/', views.update_transaction, name='update_transaction'),
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/update/<int:pk>/', views.update_category, name='update_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
    path('reports/export/csv/', views.export_report_csv, name='export_report_csv'),
    path('reports/export/excel/', views.export_report_excel, name='export_report_excel'),
    path('reports/export/pdf/', views.export_report_pdf, name='export_report_pdf'),

]
