# Proyek Analisis Data: E-Commerce Public Dataset

Proyek ini menganalisis E-Commerce Public Dataset (pesanan Januari 2017 sampai Agustus 2018) untuk menjawab dua pertanyaan bisnis:

1. Kategori produk apa saja yang menjadi 10 besar penyumbang revenue pada Januari sampai Agustus 2018, dan bagaimana pertumbuhannya dibandingkan periode yang sama pada 2017?
2. Seberapa besar selisih rata-rata skor review antara pesanan terlambat dan tepat waktu, dan di state mana persentase keterlambatan pengiriman paling tinggi selama Januari 2017 sampai Agustus 2018?

## Struktur Direktori

```
Proyek_Analisis_Data_Himawan_Wisnu_Pramuditya
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   ├── sellers_dataset.csv
├── Notebook_Proyek_Analisis_Data_Himawanwp.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment - Shell/Terminal

```
cd Proyek_Analisis_Data_Himawan_Wisnu_Pramuditya
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Menjalankan Dashboard Streamlit 

```
cd dashboard
streamlit run dashboard.py
```

## Catatan

- `main_data.csv` dihasilkan dari `Notebook_Proyek_Analisis_Data_Himawanwp.ipynb` (bagian persiapan data untuk dashboard) dan hanya berisi pesanan berstatus delivered pada periode Januari 2017 sampai Agustus 2018.
- Revenue dihitung dari harga produk tanpa ongkos kirim, dalam Real Brasil.
- Pesanan dianggap terlambat jika tanggal diterima pelanggan melewati tanggal estimasi pengiriman.
