# 🏨 Hotel Revenue Studio: Analisis Pendapatan & Pembatalan Booking

🔗 **Dashboard:** https://hotel-anggaditas.streamlit.app/

<img width="1915" height="942" alt="image" src="https://github.com/user-attachments/assets/33ec23aa-1e96-48b1-bb6f-b0ca9d70ae16" />


## Latar Belakang (Studi Kasus)
**Skenario:** Manajemen sebuah hotel memiliki data booking kamar selama 6 bulan. Mereka ingin tahu seberapa besar pendapatan yang hilang akibat pembatalan, kombinasi kamar dan channel mana yang paling menguntungkan, dan apakah harga serta paket menginap sudah optimal.

**Deliverable:**
1. Data booking yang sudah dibersihkan dan divalidasi
2. Analisis pendapatan dan pembatalan beserta rekomendasi
3. Dashboard interaktif 4 halaman yang bisa dipantau secara mandiri

> Catatan: project ini adalah studi kasus portofolio dengan dataset simulasi.

## Pertanyaan Bisnis
1. Berapa pendapatan yang hilang akibat pembatalan, dan dari channel mana?
2. Kombinasi tipe kamar × channel mana yang paling untung dan paling berisiko?
3. Apakah tamu yang menginap lebih lama lebih bernilai?
4. Kapan tamu paling banyak check-in dan apakah harga akhir pekan sudah optimal?

## Pembersihan Data
Dataset: 3.520 baris booking (check-in Januari–Juni 2026).
- 20 booking dobel dihapus (3.520 → 3.500 booking)
- Data kosong di `booking_channel`, `payment_method`, dan `customer_type` diisi `Unknown`
- Divalidasi: malam menginap sesuai tanggal, revenue = malam × tarif, booking batal tidak punya revenue
- Ditambah fitur: bulan, hari check-in, dan potensi pendapatan hilang

## Temuan Utama
- Pendapatan booking selesai **Rp4,85 miliar**; tingkat pembatalan **9,8%**
- Potensi pendapatan hilang akibat pembatalan **±Rp525 juta**
- **Deluxe** menyumbang pendapatan terbesar (±Rp1,19 miliar)
- **Online Travel Agent** ±41% pendapatan, tetapi pembatalannya tertinggi (±13,7% vs Corporate ±6,0%)
- **Suite via Website** hampir tidak pernah dibatalkan (±1,7%), sedangkan Suite via OTA ±12,7%
- Metode pembayaran tidak membedakan pembatalan (±9–10% di semua metode)
- Menginap **5 malam atau lebih** hanya ±12,6% dari booking, tetapi menyumbang ±27,8% pendapatan
- Check-in memuncak di Jumat–Sabtu, tetapi tarif akhir pekan hanya ±4% lebih tinggi

## Rekomendasi
- Terapkan deposit atau kebijakan pembatalan khusus untuk channel OTA
- Dorong booking langsung lewat Website (pembatalan jauh lebih rendah)
- Tawarkan paket menginap panjang (5 malam atau lebih)
- Terapkan harga akhir pekan yang lebih dinamis
- Siapkan promo last-minute untuk mengisi kamar dari pembatalan

## Dashboard
Empat halaman: Kebocoran Pendapatan, Kamar × Channel, Lama Menginap, dan Kalender Check-in, lengkap dengan filter bulan.

## Tools
Python · Pandas · Matplotlib · Seaborn · Plotly · Streamlit · Google Colab

## Isi Repository
- `app.py`: dashboard Streamlit
- `Analisis_Hotel_Booking.ipynb`: notebook analisis (cleaning, EDA, insight)
- `data/`: dataset
- `.streamlit/config.toml`: tema dashboard

---
Dibuat oleh **Ihsan Amiruddin**. Terbuka untuk jasa analisis data dan dashboard.
