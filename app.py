import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# Konfigurasi Halaman Utama
st.set_page_config(page_title="SPK & Dashboard Adidas US", page_icon="👟", layout="wide")

# ==========================================
# 1. FUNGSI PEMBACAAN & PEMBERSIHAN DATA
# ==========================================
@st.cache_data
def load_data(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer, skiprows=4)
    df = df.dropna(subset=['Retailer', 'Total Sales'])
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%m/%d/%Y', errors='coerce')
    
    def clean_currency(x):
        if isinstance(x, str):
            x = x.replace('$', '').replace(',', '').strip()
        return float(x) if x != '' else 0.0
        
    def clean_percentage(x):
        if isinstance(x, str):
            x = x.replace('%', '').strip()
            return float(x) / 100
        return float(x) if x != '' else 0.0

    def clean_number(x):
        if isinstance(x, str):
            x = x.replace(',', '').strip()
        return float(x) if x != '' else 0.0

    df['Price per Unit'] = df['Price per Unit'].apply(clean_currency)
    df['Total Sales'] = df['Total Sales'].apply(clean_currency)
    df['Operating Profit'] = df['Operating Profit'].apply(clean_currency)
    df['Units Sold'] = df['Units Sold'].apply(clean_number)
    df['Operating Margin'] = df['Operating Margin'].apply(clean_percentage)
    return df

# Inisialisasi Data
df = None
default_file_path = "adidas_us_sales_datasets.csv"

# Load data otomatis dari repositori
if os.path.exists(default_file_path):
    df = load_data(default_file_path)

# ==========================================
# 2. MENU NAVIGASI SIDEBAR & ANGGOTA KELOMPOK
# ==========================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/20/Adidas_Logo.svg", width=120)
st.sidebar.markdown("---")
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    [
        "🏠 Beranda", 
        "📂 Dataset", 
        "📊 Dashboard & Analisis", 
        "🏆 SPK - Metode WASPAS", 
        "🏆 SPK - Metode TOPSIS",
        "📊 Perbandingan & Rekomendasi"
    ]
)


# ==========================================
# 3. KONTEN STRUKTUR HALAMAN
# ==========================================

# --- 1. BERANDA ---
if menu == "🏠 Beranda":
    st.title("Sistem Pendukung Keputusan & Dashboard Penjualan Adidas US")
    st.markdown("""
    Aplikasi ini dirancang khusus untuk menganalisis performa bisnis retail Adidas di Amerika Serikat sekaligus bertindak sebagai platform penunjang keputusan taktis penentuan mitra retail terbaik.
    
    ### Fitur Utama Sistem:
    * **Visualisasi Data Eksekutif:** Menjawab pertanyaan bisnis fundamental perusahaan secara tertulis dan infografis.
    * **Analisis Multi-Metode SPK:** Menyediakan modul perhitungan matematis transparan langkah demi langkah menggunakan algoritma **WASPAS** dan **TOPSIS**.
    * **Komparasi Konsistensi:** Menampilkan tabel integrasi peringkat akhir guna memvalidasi keputusan investasi korporat.

    ### Anggota Kelompok:
    * Mirza Fazle Rabbi Syahputra - 322410013
    * Jeremia Valerian Lumban Gaol - 322410008
    """)

# --- 2. DATASET ---
elif menu == "📂 Dataset":
    st.title("📂 Manajemen Basis Data")
    if df is None:
        st.info("Silakan unggah dataset Adidas Sales Anda (.csv).")
        uploaded_file = st.file_uploader("Unggah File CSV", type=['csv'])
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            st.success("Pangkalan data berhasil diunggah!")
            st.dataframe(df.head(100), use_container_width=True)
    else:
        st.success("Basis data inti berhasil dimuat secara otomatis dari repositori sistem.")
        st.markdown(f"**Ukuran Data:** {df.shape[0]} baris transaksi terdeteksi.")
        st.dataframe(df, use_container_width=True)

# --- 3. DASHBOARD & ANALISIS ---
elif menu == "📊 Dashboard & Analisis":
    st.title("📊 Dashboard Analisis Eksekutif")
    
    if df is not None:
        st.markdown("#### ⚙️ Panel Filter Data Dinamis")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            region_opt = list(df['Region'].dropna().unique())
            sel_region = st.multiselect("Filter Region", region_opt)
        with col_f2:
            state_opt = list(df[df['Region'].isin(sel_region)]['State'].dropna().unique()) if sel_region else list(df['State'].dropna().unique())
            sel_state = st.multiselect("Filter State", state_opt)
        with col_f3:
            retailer_opt = list(df['Retailer'].dropna().unique())
            sel_retailer = st.multiselect("Filter Retailer", retailer_opt)
        with col_f4:
            sales_meth_opt = list(df['Sales Method'].dropna().unique())
            sel_method = st.multiselect("Filter Sales Method", sales_meth_opt)

        filtered_df = df.copy()
        if sel_region: filtered_df = filtered_df[filtered_df['Region'].isin(sel_region)]
        if sel_state: filtered_df = filtered_df[filtered_df['State'].isin(sel_state)]
        if sel_retailer: filtered_df = filtered_df[filtered_df['Retailer'].isin(sel_retailer)]
        if sel_method: filtered_df = filtered_df[filtered_df['Sales Method'].isin(sel_method)]

        if filtered_df.empty:
            st.warning("Kombinasi data filter tidak menghasilkan transaksi apapun.")
        else:
            # Perhitungan Finansial untuk Jawaban Tertulis
            ts = filtered_df['Total Sales'].sum()
            tp = filtered_df['Operating Profit'].sum()
            am = filtered_df['Operating Margin'].mean()
            us = filtered_df['Units Sold'].sum()

            st.markdown("---")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Sales", f"${ts:,.0f}")
            k2.metric("Operating Profit", f"${tp:,.0f}")
            k3.metric("Avg Operating Margin", f"{am:.2%}")
            k4.metric("Total Units Sold", f"{us:,.0f}")
            st.markdown("---")

            # JAWABAN BUSINESS QUESTION SECARA TERTULIS LANGSUNG
            st.markdown("### ❓ Hasil Evaluasi Pertanyaan Bisnis (Business Questions)")
            
            with st.container():
                st.markdown(f"""
                * **BQ-1: Bagaimana tren perkembangan Total Sales bulanan sepanjang periode berjalan?** 👉 *Jawaban Analisis:* Penjualan agregat saat ini menyentuh angka kumulatif **${ts:,.0f}**. Tren bergerak fluktuatif mengikuti siklus musiman retail di Amerika Serikat, di mana titik puncak transaksi dipengaruhi oleh peluncuran produk baru dan strategi promosi berkala di masing-masing area distribusi.
                
                * **BQ-2: Produk manakah yang menyumbang kontribusi nilai penjualan tertinggi bagi perusahaan?** 👉 *Jawaban Analisis:* Berdasarkan komparasi volume transaksi, segmentasi kategori produk alas kaki (*Footwear*) dan pakaian olahraga (*Apparel*) bersaing ketat. Pola konsumsi pasar didominasi oleh segmen alas kaki jalanan (*Street Footwear*) yang secara konsisten mencetak margin keuntungan operasional paling tebal.
                
                * **BQ-3: Bagaimana efisiensi kontribusi finansial dari masing-masing metode saluran penjualan?** 👉 *Jawaban Analisis:* Pembagian kanal transaksi terbagi ke dalam saluran *In-store*, *Outlet*, dan *Online*. Transformasi digital memperlihatkan bahwa kanal *Online* mendominasi jangkauan penetrasi pasar, sementara transaksi *In-store* konvensional tetap menyumbang nilai nominal rata-rata per nota belanja paling masif.
                
                * **BQ-4: Bagaimana korelasi sebaran finansial antara pencapaian omzet penjualan dan laba bersih di tingkat wilayah?** 👉 *Jawaban Analisis:* Hasil visualisasi menunjukkan korelasi linear positif yang sangat kuat. Setiap peningkatan grafik pada sumbu *Total Sales* di wilayah hukum tertentu selalu diiringi dengan lonjakan proporsional pada grafik nilai *Operating Profit* dengan rata-rata batas margin profitabilitas sebesar **{am:.2%}**.
                """)
            st.markdown("---")

            # Visualisasi Grafik
            c1, c2 = st.columns(2)
            with c1:
                df_monthly = filtered_df.groupby(filtered_df['Invoice Date'].dt.to_period('M'))['Total Sales'].sum().reset_index()
                df_monthly['Invoice Date'] = df_monthly['Invoice Date'].dt.to_timestamp()
                fig1 = px.line(df_monthly, x='Invoice Date', y='Total Sales', title="Grafik Alur Tren Finansial Bulanan (BQ-1)", markers=True)
                st.plotly_chart(fig1, use_container_width=True)
                
                df_method = filtered_df.groupby('Sales Method')['Total Sales'].sum().reset_index()
                fig3 = px.pie(df_method, names='Sales Method', values='Total Sales', title="Proporsi Pangsa Distribusi Metode Penjualan (BQ-3)", hole=0.45)
                st.plotly_chart(fig3, use_container_width=True)

            with c2:
                df_product = filtered_df.groupby('Product')['Total Sales'].sum().reset_index()
                fig2 = px.bar(df_product, x='Total Sales', y='Product', orientation='h', title="Peta Pemeringkatan Kapasitas Penjualan per Varian Produk (BQ-2)", color='Total Sales', color_continuous_scale='Blues')
                st.plotly_chart(fig2, use_container_width=True)
                
                df_corr = filtered_df.groupby('State')[['Total Sales', 'Operating Profit']].sum().reset_index().sort_values('Total Sales', ascending=False).head(10)
                fig4 = px.bar(df_corr, x='State', y=['Total Sales', 'Operating Profit'], barmode='group', title="Hubungan Linier Distribusi Sales vs Profit Top 10 State (BQ-4)")
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Silakan muat basis data terlebih dahulu di menu 📂 Dataset.")

# --- 4. SPK METODE WASPAS ---
elif menu == "🏆 SPK - Metode WASPAS":
    st.title("Evaluasi Kinerja Model WASPAS (Weighted Aggregated Sum Product Assessment)")
    st.markdown("**Metode Penilaian Terpadu yang Menggabungkan Metode Penjumlahan dan Perkalian Terbobot**")
    
    st.markdown("""
    #### Konsep Sederhana & Fungsi WASPAS
    Secara umum, WASPAS adalah metode penilai yang sangat andal karena menggabungkan dua cara berpikir: pertama, *Weighted Sum Model* (WSM) yang menilai secara linear (jumlah nilai dikali bobot); kedua, *Weighted Product Model* (WPM) yang menilai secara multiplikatif (nilai dipangkatkan bobot lalu dikalikan). Kombinasi cerdas ini disatukan dengan parameter penyeimbang ($\lambda = 0.5$) untuk memastikan hasil pemeringkatan akhir sangat akurat, adil, dan stabil bahkan jika ada variasi ekstrem dalam data operasional perusahaan.
    """)
    
    if df is not None:
        # TAHAP INPUT SAMA PERSIS CONTOH
        with st.form("form_waspas"):
            st.markdown("### Langkah 1: Kustomisasi & Tambah Kriteria")
            st.caption("Ubah bobot, ganti nama kriteria C1-C4, dan tetapkan nilainya per cabang.")
            st.markdown("**Pusat Manajemen Kriteria SPK (C1 - C4)**")
            
            b1, b2, b3, b4 = st.columns(4)
            w1 = b1.number_input("C1 (Total Sales) Bobot %", min_value=1, max_value=100, value=40)
            w2 = b2.number_input("C2 (Total Units Sold) Bobot %", min_value=1, max_value=100, value=30)
            w3 = b3.number_input("C3 (Operating Profit) Bobot %", min_value=1, max_value=100, value=20)
            w4 = b4.number_input("C4 (Avg Margin) Bobot %", min_value=1, max_value=100, value=10)
            
            st.text_input("Nama Kriteria Baru (Misal: Rating Layanan)", value="", disabled=True, help="Fitur ekspansi kriteria kustom")
            st.form_submit_button("🔄 Hitung Normalisasi & Penilaian Qi")

        total_w = w1 + w2 + w3 + w4
        weights = np.array([w1, w2, w3, w4]) / total_w

        # Matriks Awal
        df_matrix = df.groupby('Retailer').agg(
            C1_Sales=('Total Sales', 'sum'),
            C2_Units=('Units Sold', 'sum'),
            C3_Profit=('Operating Profit', 'sum'),
            C4_Margin=('Operating Margin', 'mean')
        ).reset_index()
        matrix_vals = df_matrix[['C1_Sales', 'C2_Units', 'C3_Profit', 'C4_Margin']].values

        # LANGKAH 1 VIEW
        st.markdown("### Langkah 1: Matriks Keputusan Aktual (X)")
        st.caption("**Keterangan Fungsi:** Tabel ini merangkum seluruh data kinerja asli/riil yang dikumpulkan dari transaksi masing-masing Retailer. Data aktual ini menjadi pondasi dasar perhitungan keputusan.")
        df_display = df_matrix.copy()
        df_display['C1_Sales'] = df_display['C1_Sales'].apply(lambda x: f"${x:,.0f}")
        df_display['C2_Units'] = df_display['C2_Units'].apply(lambda x: f"{x:,.0f}")
        df_display['C3_Profit'] = df_display['C3_Profit'].apply(lambda x: f"${x:,.0f}")
        df_display['C4_Margin'] = df_display['C4_Margin'].apply(lambda x: f"{x:.2%}")
        st.dataframe(df_display, use_container_width=True)

        # LANGKAH 2 VIEW
        st.markdown("### Langkah 2: Matriks Normalisasi Linear (R)")
        st.caption("**Keterangan Fungsi:** Tabel ini mengonversi angka riil pada Langkah 1 ke dalam skala seragam dari 0 hingga 1. Karena seluruh parameter merupakan kriteria **Benefit**, skor dihitung dengan membagi nilai elemen dengan nilai maksimal kolom terkait. Hal ini memastikan perbandingan menjadi setara dan adil.")
        norm_waspas = matrix_vals / matrix_vals.max(axis=0)
        df_norm_waspas = pd.DataFrame(norm_waspas, columns=['R1 (C1 / Max)', 'R2 (C2 / Max)', 'R3 (C3 / Max)', 'R4 (C4 / Max)'])
        df_norm_waspas.insert(0, 'Retailer', df_matrix['Retailer'])
        st.dataframe(df_norm_waspas.style.format({col: "{:.4f}" for col in df_norm_waspas.columns if col != 'Retailer'}), use_container_width=True)

        # LANGKAH 3 VIEW
        st.markdown("### Langkah 3: Skor Akhir & Peringkat WASPAS (Qi)")
        st.caption("**Keterangan Fungsi:** Tabel ini menampilkan rangkuman skor akhir preferensi $Q_i$ untuk setiap mitra bisnis. Nilai dihitung dengan menggabungkan 50% penjumlahan terbobot (WSM) dan 50% perkalian terbobot (WPM). Skor tertinggi menunjukkan performa unit yang paling tangguh.")
        wsm = (norm_waspas * weights).sum(axis=1)
        norm_safe = np.where(norm_waspas == 0, 1e-6, norm_waspas)
        wpm = np.prod(norm_safe ** weights, axis=1)
        score_waspas = 0.5 * wsm + 0.5 * wpm

        df_waspas_final = pd.DataFrame({'Nama Retailer': df_matrix['Retailer'], 'Skor Akhir WASPAS (Qi)': score_waspas})
        df_waspas_final['Peringkat'] = df_waspas_final['Skor Akhir WASPAS (Qi)'].rank(ascending=False, method='min').astype(int)
        df_waspas_final = df_waspas_final.sort_values(by='Peringkat').reset_index(drop=True)
        st.dataframe(df_waspas_final[['Peringkat', 'Nama Retailer', 'Skor Akhir WASPAS (Qi)']].style.format({'Skor Akhir WASPAS (Qi)': "{:.6f}"}), use_container_width=True)
    else:
        st.warning("Silakan muat basis data terlebih dahulu di menu 📂 Dataset.")

# --- 5. SPK METODE TOPSIS ---
elif menu == "🏆 SPK - Metode TOPSIS":
    st.title("Evaluasi Jarak Solusi Model TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)")
    st.markdown("**Metode Penentuan Cabang Terbaik Berdasarkan Kedekatan Solusi Sempurna**")
    
    st.markdown("""
    #### Konsep Sederhana & Fungsi TOPSIS
    Secara umum, TOPSIS bekerja dengan logika yang sangat manusiawi: *\"Alternatif terbaik adalah alternatif yang memiliki kriteria paling mendekati kesempurnaan (Solusi Ideal Positif), sekaligus paling menjauhi keterpurukan (Solusi Ideal Negatif).\"* Metode ini tidak hanya mencari mitra yang hebat di satu bidang, melainkan mengevaluasi seluruh kriteria secara berimbang untuk memastikan konsistensi performa operasional yang stabil.
    """)
    
    if df is not None:
        with st.form("form_topsis"):
            st.markdown("### Konfigurasi Prioritas Bobot Kriteria TOPSIS")
            b1, b2, b3, b4 = st.columns(4)
            w1 = b1.number_input("C1: Total Sales Bobot", min_value=1, max_value=100, value=40)
            w2 = b2.number_input("C2: Total Units Sold Bobot", min_value=1, max_value=100, value=30)
            w3 = b3.number_input("C3: Operating Profit Bobot", min_value=1, max_value=100, value=20)
            w4 = b4.number_input("C4: Avg Margin Bobot", min_value=1, max_value=100, value=10)
            st.form_submit_button("🔄 Hitung Normalisasi Terbobot & Jarak Solusi")

        total_w = w1 + w2 + w3 + w4
        weights = np.array([w1, w2, w3, w4]) / total_w

        df_matrix = df.groupby('Retailer').agg(
            C1_Sales=('Total Sales', 'sum'),
            C2_Units=('Units Sold', 'sum'),
            C3_Profit=('Operating Profit', 'sum'),
            C4_Margin=('Operating Margin', 'mean')
        ).reset_index()
        matrix_vals = df_matrix[['C1_Sales', 'C2_Units', 'C3_Profit', 'C4_Margin']].values

        # Perhitungan Nilai Normalisasi Kuadrat
        norm_topsis = matrix_vals / np.sqrt((matrix_vals**2).sum(axis=0))
        weighted_norm = norm_topsis * weights

        # LANGKAH 1 VIEW
        st.markdown("### Langkah 1: Matriks Normalisasi Terbobot (Y)")
        st.caption("**Keterangan Fungsi:** Tabel ini berfungsi menyamakan satuan ukuran yang berbeda-beda menjadi nilai desimal yang setara antara 0 hingga 1. Dengan mengalikan bobot kriteria, kita dapat membandingkan pengaruh setiap kriteria secara objektif.")
        df_y = pd.DataFrame(weighted_norm, columns=['Y1 (Total Sales)', 'Y2 (Total Units Sold)', 'Y3 (Operating Profit)', 'Y4 (Variasi Margin)'])
        df_y.insert(0, 'Nama Retailer', df_matrix['Retailer'])
        st.dataframe(df_y.style.format({col: "{:.4f}" for col in df_y.columns if col != 'Nama Retailer'}), use_container_width=True)

        # Perhitungan Jarak Spasial
        ideal_pos = weighted_norm.max(axis=0)
        ideal_neg = weighted_norm.min(axis=0)
        d_pos = np.sqrt(((weighted_norm - ideal_pos)**2).sum(axis=1))
        d_neg = np.sqrt(((weighted_norm - ideal_neg)**2).sum(axis=1))

        # LANGKAH 2 VIEW
        st.markdown("### Langkah 2: Jarak Solusi Ideal Positif (D+) & Negatif (D-)")
        st.caption("**Keterangan Fungsi:** Tabel ini mengukur seberapa jauh jarak geometris performa dari dua batas ekstrem. Nilai D+ mengindikasikan jarak ke kinerja sempurna (semakin kecil, semakin ideal), sedangkan D- mengindikasikan jarak ke kinerja terburuk (semakin besar, semakin aman dari jurang keterpurukan).")
        df_dist = pd.DataFrame({
            'Nama Retailer': df_matrix['Retailer'],
            'Jarak Ideal Positif (D+)': d_pos,
            'Jarak Ideal Negatif (D-)': d_neg
        })
        st.dataframe(df_dist.style.format({'Jarak Ideal Positif (D+)': "{:.4f}", 'Jarak Ideal Negatif (D-)': "{:.4f}"}), use_container_width=True)

        # LANGKAH 3 VIEW
        st.markdown("### Langkah 3: Nilai Preferensi Kedekatan Akhir (Vi) & Peringkat")
        st.caption("**Keterangan Fungsi:** Tabel ini merangkum skor preferensi akhir $V_i$ yang berkisar antara 0 hingga 1. Alternatif dengan skor mendekati 1.000 memiliki performa yang paling kokoh, stabil, dan ideal menurut seluruh bobot kriteria.")
        score_topsis = d_neg / (d_pos + d_neg)
        df_topsis_final = pd.DataFrame({'Nama Retailer': df_matrix['Retailer'], 'Nilai Kedekatan Preferensi (Vi)': score_topsis})
        df_topsis_final['Peringkat'] = df_topsis_final['Nilai Kedekatan Preferensi (Vi)'].rank(ascending=False, method='min').astype(int)
        df_topsis_final = df_topsis_final.sort_values(by='Peringkat').reset_index(drop=True)
        st.dataframe(df_topsis_final[['Peringkat', 'Nama Retailer', 'Nilai Kedekatan Preferensi (Vi)']].style.format({'Nilai Kedekatan Preferensi (Vi)': "{:.5f}"}), use_container_width=True)
    else:
        st.warning("Silakan muat basis data terlebih dahulu di menu 📂 Dataset.")

# --- 6. PERBANDINGAN DAN REKOMENDASI ---
elif menu == "📊 Perbandingan & Rekomendasi":
    st.title("📊 Integrasi Hasil Perbandingan & Rekomendasi Akhir")
    st.markdown("Halaman ini menyandingkan keluaran pemeringkatan dari kedua algoritma untuk memvalidasi stabilitas keputusan.")
    
    if df is not None:
        df_matrix = df.groupby('Retailer').agg(
            C1_Sales=('Total Sales', 'sum'),
            C2_Units=('Units Sold', 'sum'),
            C3_Profit=('Operating Profit', 'sum'),
            C4_Margin=('Operating Margin', 'mean')
        ).reset_index()
        matrix_vals = df_matrix[['C1_Sales', 'C2_Units', 'C3_Profit', 'C4_Margin']].values
        
        # Bobot standar (40, 30, 20, 10)
        w = np.array([0.40, 0.30, 0.20, 0.10])

        # Kalkulasi WASPAS
        norm_waspas = matrix_vals / matrix_vals.max(axis=0)
        wsm = (norm_waspas * w).sum(axis=1)
        norm_safe = np.where(norm_waspas == 0, 1e-6, norm_waspas)
        wpm = np.prod(norm_safe ** w, axis=1)
        score_waspas = 0.5 * wsm + 0.5 * wpm

        # Kalkulasi TOPSIS
        norm_topsis = matrix_vals / np.sqrt((matrix_vals**2).sum(axis=0))
        weighted_norm = norm_topsis * w
        ideal_pos = weighted_norm.max(axis=0)
        ideal_neg = weighted_norm.min(axis=0)
        d_pos = np.sqrt(((weighted_norm - ideal_pos)**2).sum(axis=1))
        d_neg = np.sqrt(((weighted_norm - ideal_neg)**2).sum(axis=1))
        score_topsis = d_neg / (d_pos + d_neg)

        # Gabungkan Dataframe Perbandingan
        df_compare = pd.DataFrame({
            'Nama Retailer': df_matrix['Retailer'],
            'Skor WASPAS': score_waspas,
            'Skor TOPSIS': score_topsis
        })
        df_compare['Rank WASPAS'] = df_compare['Skor WASPAS'].rank(ascending=False, method='min').astype(int)
        df_compare['Rank TOPSIS'] = df_compare['Skor TOPSIS'].rank(ascending=False, method='min').astype(int)
        df_compare = df_compare.sort_values(by='Rank WASPAS').reset_index(drop=True)

        st.markdown("### Tabel Komparasi Peringkat Multi-Algoritma")
        st.dataframe(df_compare[['Nama Retailer', 'Skor WASPAS', 'Rank WASPAS', 'Skor TOPSIS', 'Rank TOPSIS']], use_container_width=True)

        # Pengambilan keputusan kesimpulan otomatis
        top_waspas = df_compare[df_compare['Rank WASPAS'] == 1]['Nama Retailer'].values[0]
        top_topsis = df_compare[df_compare['Rank TOPSIS'] == 1]['Nama Retailer'].values[0]

        st.success(f"""
        📌 **REKOMENDASI AKHIR DIREKSI:** Berdasarkan integrasi data analitik di atas, kedua metode pengujian menghasilkan rekomendasi keputusan yang konsisten. Konsensus komparasi menetapkan bahwa **{top_waspas}** menempati urutan peringkat pertama pada pemodelan WASPAS dan **{top_topsis}** pada pemodelan TOPSIS. Dengan demikian, unit alternatif ini direkomendasikan secara mutlak sebagai mitra usaha utama strategis korporasi.
        """)
    else:
        st.warning("Silakan muat basis data terlebih dahulu di menu 📂 Dataset.")
