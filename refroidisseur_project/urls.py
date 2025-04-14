from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from refroidisseur_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('export_excel/', views.export_excel, name='export_excel'),  # ✅ n'oublie pas la virgule ici
    path('mesures/', views.mesures_list, name='mesures_list'),
    path('mesures/<int:pk>/', views.mesure_detail, name='mesure_detail'),
    path('mesures/<int:pk>/delete/', views.mesure_delete, name='mesure_delete'),
    path('mesures/<int:pk>/export_pdf/', views.export_pdf, name='export_pdf'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
