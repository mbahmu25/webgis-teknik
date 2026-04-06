# WebGIS Teknik

Dokumentasi ini menjelaskan cara menjalankan proyek WebGIS Teknik yang terdiri dari:
- Backend Django REST API dengan PostGIS
- Frontend Vue 3 + Vite
- Orkestrasi menggunakan Docker Compose

## Fitur Utama
- Backend Django dengan REST API
- Basis data PostgreSQL + PostGIS
- Frontend Vue 3 dengan Leaflet untuk peta
- Konfigurasi development cepat via Docker

## Prasyarat
- Docker
- Docker Compose
- Git

> Proyek ini sudah dikonfigurasi untuk dijalankan secara lengkap menggunakan `docker-compose`.

## Struktur Proyek
- `backend/` - aplikasi Django
- `frontend/` - aplikasi Vue 3
- `docker-compose.yml` - definisi layanan backend, frontend, dan database

## Menjalankan Proyek di Server
1. Clone repositori ke server:
   ```bash
   git clone https://github.com/mbahmu25/webgis-teknik.git
   cd webgis-teknik
   ```

2. Bangun dan jalankan semua layanan:
   ```bash
   docker-compose up --build
   ```

3. Tunggu hingga kontainer selesai memulai.
   - Backend akan tersedia di `http://localhost:8000`
   - Frontend akan tersedia di `http://localhost:8081`

4. Buka browser atau gunakan proxy/nginx untuk akses aplikasi frontend:
   ```
   http://localhost:8081
   ```

3. Tunggu hingga kontainer selesai memulai.
   - Backend akan tersedia di `http://localhost:8000`
   - Frontend akan tersedia di `http://localhost:8081`

4. Buka browser dan akses aplikasi frontend:
   ```
   http://localhost:8081
   ```

## Layanan yang Dijelaskan
- `db`: PostgreSQL dengan PostGIS
- `backend`: Django API, menjalankan migrasi otomatis lalu runserver
- `frontend`: Vue 3 + Vite, melayani aplikasi di port 8081

## Default Credentials Database
Konfigurasi awal pada `docker-compose.yml`:
- User: `postgres`
- Password: `postgres`
- Database: `teknik`

> Ubah `POSTGRES_PASSWORD` di `docker-compose.yml` untuk penggunaan lain atau production.

## Scripts Frontend
Jika perlu menjalankan frontend secara lokal tanpa Docker, masuk ke folder frontend dan jalankan:
```bash
cd frontend
npm install
npm run dev
```

## Dependencies Backend
Backend menggunakan paket utama berikut (lihat `backend/requirements.txt`):
- Django
- djangorestframework
- djangorestframework-gis
- django-filter
- psycopg2-binary
- Pillow
- django-cors-headers
- gunicorn

## Pengembangan dan Perubahan
- Untuk menambahkan model atau API baru, ubah di `backend/api/`
- Untuk mengubah tampilan antarmuka, ubah di `frontend/src/`
- Untuk konfigurasi rute Vue, lihat `frontend/src/router/index.js`

## Hentikan Proyek
Untuk menghentikan layanan, tekan `CTRL+C` pada terminal `docker-compose` lalu jalankan:
```bash
docker-compose down
```

## Catatan Tambahan
- `docker-compose.yml` saat ini menggunakan `DEBUG=1` untuk development.
- Volume `postgres_data` menyimpan data PostgreSQL secara persisten.

Jika ingin bantuan tambahan untuk konfigurasi atau deployment, tambahkan pertanyaan baru di dokumentasi ini.