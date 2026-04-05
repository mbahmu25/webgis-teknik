from django.contrib.gis.db import models # Gunakan modul GIS
from django.utils.translation import gettext_lazy as _

class KategoriKegiatan(models.Model):
    """
    Kategori bersifat dinamis, dapat ditambah via admin.
    Contoh: Pengabdian Masyarakat, Kerja Sama, Penelitian.
    """
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nama

class PeranFT(models.Model):
    # Pilihan SDGs 1-17 sesuai dokumen [cite: 4]
    SDG_CHOICES = [(i, f'SDG {i}') for i in range(1, 18)]

    # Relasi ke Kategori
    kategori = models.ForeignKey(
        KategoriKegiatan, 
        on_delete=models.CASCADE,
        related_name='kegiatan'
    )

    # Data Dasar 
    nama_kegiatan = models.CharField(max_length=255)
    abstrak = models.TextField(help_text="Keterangan singkat kegiatan")
    
    # Data Mitra & Lokasi 
    nama_mitra = models.CharField(max_length=200)
    # Lokasi hierarkis (disimpan sebagai string atau JSON jika tidak butuh query spasial area)
    lokasi_administratif = models.CharField(
        max_length=255, 
        help_text="Format: Negara | Propinsi | Kabupaten | Desa"
    )
    
    # Inti WebGIS: Koordinat (Point)
    koordinat = models.PointField(srid=4326, help_text="Titik koordinat lokasi mitra")

    # Atribut Tambahan [cite: 4]
    kategori_sdgs = models.IntegerField(choices=SDG_CHOICES, verbose_name="Kategori SDGs")
    foto = models.ImageField(upload_to='kegiatan_photos/', blank=True, null=True)
    url = models.URLField(blank=True, null=True, verbose_name="URL Berita")
    tahun = models.IntegerField(help_text="Tahun kegiatan dilakukan")

    class Meta:
        ordering = ['-tahun']
        verbose_name = "Peran FT UGM"

    def __str__(self):
        return f"{self.nama_kegiatan} ({self.tahun})"