from django.urls import path, include
from django.contrib import admin
from .views import ocr_process
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from ingress.views import extract_details_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('process_ocr/', views.process_ocr, name='process_ocr'),
    path('extract-details/', extract_details_view, name='extract_details'),
    path('', views.home, name='home'),      # Home page route
    path('login/', views.login, name='login'),  # Login page route
    path('logout/', views.logout_view, name='logout'),
    path('', ocr_process, name='ocr-process'),
    path('upload/', views.upload_view, name='upload'),
    #path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)