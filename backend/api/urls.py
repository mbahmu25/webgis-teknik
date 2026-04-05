# File: peta/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeranFTViewSet, KategoriViewSet

# Router otomatis membuat URL untuk CRUD (Create, Read, Update, Delete)
router = DefaultRouter()
router.register(r'peran-ft', PeranFTViewSet, basename='peran-ft')
router.register(r'kategori', KategoriViewSet, basename='kategori')

urlpatterns = [
    # Semua URL dari router akan masuk ke sini
    path('', include(router.urls)),
]