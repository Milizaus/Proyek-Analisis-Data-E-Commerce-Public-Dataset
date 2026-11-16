import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.ticker import FuncFormatter

sns.set_theme(style="whitegrid")

st.set_page_config(page_title="Dashboard E-Commerce", layout="wide")


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(path, parse_dates=["order_purchase_timestamp"])
    df["tahun"] = df["order_purchase_timestamp"].dt.year
    df["bulan"] = df["order_purchase_timestamp"].dt.month
    return df


main_df = load_data()

# ------------------------------------------------------------------ Sidebar
st.sidebar.header("Filter Data")

tanggal_min = main_df["order_purchase_timestamp"].min().date()
tanggal_maks = main_df["order_purchase_timestamp"].max().date()

rentang = st.sidebar.date_input(
    "Rentang tanggal pembelian (Pertanyaan 2)",
    value=(tanggal_min, tanggal_maks),
    min_value=tanggal_min,
    max_value=tanggal_maks,
)

semua_state = sorted(main_df["customer_state"].dropna().unique())
state_dipilih = st.sidebar.multiselect(
    "State pelanggan (berlaku untuk semua grafik)",
    options=semua_state,
    default=semua_state,
)

# Data hasil filter state
df_state = main_df[main_df["customer_state"].isin(state_dipilih)]

# ------------------------------------------------------------------ Header
st.title("Dashboard Analisis E-Commerce")
st.caption(
    "Data pesanan berstatus delivered, Januari 2017 sampai Agustus 2018. "
    "Nilai revenue dalam Real Brasil dan dihitung dari harga produk (tanpa ongkir)."
)

if df_state.empty:
    st.warning("Belum ada state yang dipilih. Pilih minimal satu state pada sidebar.")
    st.stop()

# ------------------------------------------------------------------ Pertanyaan 1
st.header("Pertanyaan 1: Revenue per Kategori Produk")
st.write(
    "Kategori apa saja yang menjadi 10 besar penyumbang revenue pada periode "
    "yang dipilih tahun 2018, dan bagaimana pertumbuhannya dibanding periode "
    "yang sama pada tahun 2017?"
)

bulan_awal, bulan_akhir = st.slider(
    "Rentang bulan yang dibandingkan (2017 vs 2018)",
    min_value=1,
    max_value=8,
    value=(1, 8),
    help="Data 2018 hanya tersedia sampai Agustus, sehingga perbandingan dibatasi sampai bulan 8.",
)

periode_df = df_state[
    (df_state["bulan"].between(bulan_awal, bulan_akhir))
    & (df_state["tahun"].isin([2017, 2018]))
]

revenue_kategori = periode_df.pivot_table(
    index="product_category_name_english",
    columns="tahun",
    values="price",
    aggfunc="sum",
    fill_value=0,
)
for tahun in (2017, 2018):
    if tahun not in revenue_kategori.columns:
        revenue_kategori[tahun] = 0

revenue_kategori["pertumbuhan_persen"] = (
    (revenue_kategori[2018] - revenue_kategori[2017])
    / revenue_kategori[2017].replace(0, np.nan)
    * 100
)

total_2017 = revenue_kategori[2017].sum()
total_2018 = revenue_kategori[2018].sum()
pertumbuhan_total = (total_2018 - total_2017) / total_2017 * 100 if total_2017 > 0 else np.nan

kol1, kol2, kol3 = st.columns(3)
kol1.metric("Total revenue 2017", f"{total_2017:,.0f}")
kol2.metric("Total revenue 2018", f"{total_2018:,.0f}")
kol3.metric(
    "Pertumbuhan total",
    "-" if np.isnan(pertumbuhan_total) else f"{pertumbuhan_total:,.1f}%",
)

top10 = revenue_kategori.sort_values(2018, ascending=False).head(10)
data_q1 = top10.reset_index().sort_values(2018, ascending=True)
data_q1["kategori"] = data_q1["product_category_name_english"].str.replace("_", " ").str.title()

if data_q1[2018].sum() == 0:
    st.info("Tidak ada data revenue 2018 untuk kombinasi filter ini.")
else:
    fig, axes = plt.subplots(
        1, 2, figsize=(16, 6), gridspec_kw={"width_ratios": [1.6, 1]}, sharey=True
    )
    y = np.arange(len(data_q1))
    tinggi = 0.38

    axes[0].barh(y - tinggi / 2, data_q1[2017], height=tinggi, color="#B0BEC5", label="2017")
    axes[0].barh(y + tinggi / 2, data_q1[2018], height=tinggi, color="#1565C0", label="2018")
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(data_q1["kategori"])
    axes[0].xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1000:,.0f} rb"))
    axes[0].set_title("Revenue per Kategori", loc="left", fontsize=13, fontweight="bold")
    axes[0].set_xlabel("Total revenue (Real Brasil, ribu)")
    axes[0].legend(loc="lower right")
    for i, v in enumerate(data_q1[2018]):
        axes[0].text(v + data_q1[2018].max() * 0.01, i + tinggi / 2, f"{v / 1000:,.0f} rb", va="center", fontsize=9)

    pertumbuhan = data_q1["pertumbuhan_persen"].fillna(0)
    warna = ["#E65100" if g < 50 else "#2E7D32" for g in pertumbuhan]
    axes[1].barh(y, pertumbuhan, color=warna, height=0.55)
    axes[1].set_title("Pertumbuhan 2018 vs 2017", loc="left", fontsize=13, fontweight="bold")
    axes[1].set_xlabel("Pertumbuhan (%)")
    axes[1].set_xlim(0, max(pertumbuhan.max() * 1.18, 10))
    for i, g in enumerate(pertumbuhan):
        axes[1].text(g + pertumbuhan.max() * 0.015, i, f"{g:,.0f}%", va="center", fontsize=9)

    fig.suptitle(
        f"10 Kategori dengan Revenue Tertinggi, Bulan {bulan_awal} sampai {bulan_akhir} Tahun 2018",
        fontsize=15, fontweight="bold", x=0.01, ha="left",
    )
    plt.tight_layout()
    st.pyplot(fig)

    st.caption(
        "Batang oranye pada panel kanan menandai pertumbuhan di bawah 50%. "
        "Kategori yang tidak memiliki penjualan pada 2017 ditampilkan dengan pertumbuhan 0%."
    )

st.divider()

# ------------------------------------------------------------------ Pertanyaan 2
st.header("Pertanyaan 2: Keterlambatan Pengiriman dan Skor Review")
st.write(
    "Seberapa besar selisih rata-rata skor review antara pesanan terlambat dan "
    "tepat waktu, dan di state mana persentase keterlambatannya paling tinggi?"
)

if isinstance(rentang, (tuple, list)) and len(rentang) == 2:
    tanggal_awal, tanggal_akhir = rentang
else:
    tanggal_awal, tanggal_akhir = tanggal_min, tanggal_maks

# Satu baris per pesanan agar tidak terhitung ganda
pesanan_df = (
    df_state[
        (df_state["order_purchase_timestamp"].dt.date >= tanggal_awal)
        & (df_state["order_purchase_timestamp"].dt.date <= tanggal_akhir)
    ]
    .drop_duplicates(subset="order_id")
    .copy()
)

if pesanan_df.empty:
    st.info("Tidak ada pesanan pada rentang tanggal dan state yang dipilih.")
else:
    skor = pesanan_df.groupby("terlambat")["review_score"].mean()
    rata_terlambat = pesanan_df["terlambat"].mean() * 100

    skor_tepat = skor.get(False, np.nan)
    skor_telat = skor.get(True, np.nan)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Jumlah pesanan", f"{len(pesanan_df):,}")
    m2.metric("Pesanan terlambat", f"{rata_terlambat:.2f}%")
    m3.metric("Skor review tepat waktu", "-" if np.isnan(skor_tepat) else f"{skor_tepat:.2f}")
    m4.metric("Skor review terlambat", "-" if np.isnan(skor_telat) else f"{skor_telat:.2f}")

    state_df = (
        pesanan_df.groupby("customer_state")
        .agg(
            jumlah_pesanan=("order_id", "count"),
            persen_terlambat=("terlambat", lambda x: x.mean() * 100),
            rata_skor_review=("review_score", "mean"),
        )
        .sort_values("persen_terlambat", ascending=False)
    )
    top10_state = state_df.head(10).sort_values("persen_terlambat", ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={"width_ratios": [1, 1.5]})

    label = ["Tepat waktu", "Terlambat"]
    nilai = [0 if np.isnan(skor_tepat) else skor_tepat, 0 if np.isnan(skor_telat) else skor_telat]
    axes[0].bar(label, nilai, color=["#1565C0", "#E65100"], width=0.5)
    axes[0].set_ylim(0, 5)
    axes[0].set_ylabel("Rata-rata skor review (skala 1-5)")
    axes[0].set_title("Skor Review: Tepat Waktu vs Terlambat", loc="left", fontsize=13, fontweight="bold")
    for i, v in enumerate(nilai):
        axes[0].text(i, v + 0.08, f"{v:.2f}", ha="center", fontweight="bold")

    axes[1].barh(top10_state.index, top10_state["persen_terlambat"], color="#E65100", height=0.6)
    axes[1].axvline(
        rata_terlambat, color="#37474F", linestyle="--", linewidth=1.2,
        label=f"Rata-rata seluruh pesanan ({rata_terlambat:.1f}%)",
    )
    axes[1].legend(loc="lower right")
    axes[1].set_xlabel("Persentase pesanan terlambat (%)")
    axes[1].set_xlim(0, max(top10_state["persen_terlambat"].max() * 1.15, 1))
    axes[1].set_title("10 State dengan Keterlambatan Tertinggi", loc="left", fontsize=13, fontweight="bold")
    for i, v in enumerate(top10_state["persen_terlambat"]):
        axes[1].text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    st.pyplot(fig)

    with st.expander("Lihat tabel lengkap per state"):
        st.dataframe(state_df.round(2))

st.caption("Proyek Analisis Data: E-Commerce Public Dataset")
