from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import PeranFT, KategoriKegiatan

class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriKegiatan
        fields = ['id', 'nama']

class PeranFTGeoSerializer(GeoFeatureModelSerializer):
    """
    Serializer ini mengubah data menjadi format GeoJSON.
    Frontend mapping library akan sangat mudah membacanya.
    """
    kategori_nama = serializers.ReadOnlyField(source='kategori.nama')
    # foto_url = serializers.SerializerMethodField()

    class Meta:
        model = PeranFT
        geo_field = "koordinat" # Field yang berisi geometri
        fields = [
            'id', 'kategori', 'kategori_nama', 'nama_kegiatan', 
            'abstrak', 'nama_mitra', 'lokasi_administratif', 
            'kategori_sdgs', 'foto', 'url', 'tahun'
        ]

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if obj.foto and request:
            return request.build_absolute_uri(obj.foto.url)
        return None