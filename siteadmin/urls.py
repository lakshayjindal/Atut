from django.urls import path
from . import views

urlpatterns = [
    path('create-premium-plan/', views.create_premium_plan, name='siteadmin_create_plan'),
    path('pages/', views.page_list, name='custom_page_list'),
    path('pages/create/', views.page_create, name='custom_page_create'),
    path('pages/<int:pk>/edit/', views.page_edit, name='custom_page_edit'),
    path('email/test', views.email_test, name='email_test'),
    path("bulk-entry/", views.operator_bulk_entry_page, name="operator-bulk-entry"),
    path("bulk-create/", views.operator_bulk_create, name="operator-bulk-create"),
    path('<slug:slug>/', views.page_render, name='custom_page_render'),
]
