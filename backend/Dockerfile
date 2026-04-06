# Menggunakan image Python versi slim agar lebih ringan
FROM python:3.10-slim

# Menentukan direktori kerja di dalam container
WORKDIR /app

# Mencegah Python menulis file .pyc ke disk dan mem-bypass buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# UPDATE: Install GDAL dan bersihkan cache agar image tetap ringan
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Mengcopy requirements dan menginstall dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Mengcopy seluruh kode Django ke dalam container
COPY . .

# Mengekspos port 8000
EXPOSE 8000

# Menjalankan server Django (Gunakan Gunicorn untuk production nantinya)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]