# CodeQuiz Project Documentation

## Overview
CodeQuiz adalah aplikasi berbasis Django yang menyediakan platform kuis pemrograman dengan eksekusi kode otomatis menggunakan Judge0. Proyek ini menggunakan Docker untuk memudahkan setup dan deployment.

## Struktur Folder Penting

- `CodeQuiz/` : Konfigurasi utama Django (settings, urls, wsgi, dll)
- `quiz/` : Aplikasi utama untuk fitur kuis (models, views, admin, API, dsb)
- `manage.py` : Entry point untuk perintah Django
- `requirements.txt` : Daftar dependensi Python
- `docker-compose.yml` : Konfigurasi layanan Docker (web, db, redis, judge0)
- `dockerfile` : Instruksi build image Django
- `entrypoint.sh` : Script entrypoint untuk container web
- `db.sqlite3` : Database SQLite (default, tidak digunakan saat menggunakan Postgres di Docker)
- `tmp/judge0/` : Volume untuk data Judge0

## Setup & Menjalankan dengan Docker

### 1. Prasyarat
- Sudah terinstall Docker dan Docker Compose

### 2. Build & Jalankan Seluruh Layanan
Jalankan perintah berikut di root folder proyek:

```bash
docker-compose up --build
```

Layanan yang akan berjalan:
- **web**: Django app (port 8000)
- **db**: PostgreSQL untuk Django (port internal 5432)
- **redis**: Redis untuk cache/antrian
- **judge0**: API eksekusi kode (port 2358)
- **judge0-db**: PostgreSQL untuk Judge0

### 3. Akses Aplikasi
- Django: http://localhost:8000
- Judge0 API: http://localhost:2358

### 4. Migrasi Database & Superuser
Jika pertama kali setup, lakukan migrasi dan buat superuser:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 5. (Opsional) Load Sample Data
Jika tersedia perintah custom untuk sample data:

```bash
docker-compose exec web python manage.py create_sample_data
```

## Environment Variables Penting
- `DATABASE_URL` (web): Koneksi ke database Postgres
- `DEBUG` (web): Mode debug Django
- `POSTGRES_*` (db, judge0-db): Konfigurasi database
- `REDIS_HOST`, `REDIS_PORT` (judge0): Koneksi ke Redis

## Catatan
- Semua data database akan disimpan di volume Docker (`postgres_data`, `judge0_db_data`).
- Untuk development, kode di host akan otomatis ter-mount ke container web.

---

Untuk pertanyaan lebih lanjut, silakan cek file konfigurasi masing-masing layanan atau hubungi maintainer proyek.
