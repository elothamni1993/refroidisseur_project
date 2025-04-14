from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('export_excel/', views.export_excel, name='export_excel'),  # ✅ nouvelle route

]
