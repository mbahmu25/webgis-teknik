from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import PeranFT, KategoriKegiatan
from .serializers import PeranFTGeoSerializer, KategoriSerializer

# 1. Filter Class Custom
class PeranFTFilter(filters.FilterSet):
    tahun = filters.NumberFilter(field_name='tahun')
    kategori = filters.ModelChoiceFilter(queryset=KategoriKegiatan.objects.all())
    
    # Filter rentang tahun (opsional, tapi berguna)
    tahun_min = filters.NumberFilter(field_name='tahun', lookup_expr='gte')
    tahun_max = filters.NumberFilter(field_name='tahun', lookup_expr='lte')

    class Meta:
        model = PeranFT
        fields = ['tahun', 'kategori']

# 2. ViewSet Utama
class PeranFTViewSet(viewsets.ModelViewSet):
    """
    API endpoint yang menyediakan data GeoJSON Peran FT UGM.
    Mendukung filtering:
    - ?tahun=2024 
    - ?kategori=1 
    - ?tahun=2024&kategori=1 
    """
    queryset = PeranFT.objects.all()
    serializer_class = PeranFTGeoSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PeranFTFilter

class KategoriViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API untuk mengisi dropdown kategori di frontend
    """
    queryset = KategoriKegiatan.objects.all()
    serializer_class = KategoriSerializer