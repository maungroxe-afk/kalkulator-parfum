import streamlit as st
import pandas as pd
from google import genai

st.set_page_config(page_title="UCP ALPHA - Pro Perfumer Studio", layout="wide")

st.title("🧪 UCP ALPHA - Pro Perfumer Studio v9")
st.write("Formulasi tingkat lanjut dengan pembagian Top, Heart, Base Notes, Asisten AI, dan Visualisasi Piramida Aroma.")

# --- SIDEBAR: KONFIGURASI AI ---
st.sidebar.header("🔑 Konfigurasi AI")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="Masukkan API Key dari Google AI Studio")

st.markdown("---")

# --- 1. PANDUAN KONSENTRASI & UPLOAD DATA ---
st.header("📋 1. Panduan Konsentrasi & Upload Data")
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("✨ Pilih Target Konsentrasi")
    concentration_type = st.selectbox(
        "Kategori Parfum Target:",
        ["Custom (Isi Sendiri)", "Eau de Cologne (EDC - Bibit ~3%)", "Eau de Toilette (EDT - Bibit ~10%)", "Eau de Parfum (EDP - Bibit ~20%)", "Extrait de Parfum (Bibit ~30%)"]
    )
    if concentration_type == "Eau de Cologne (EDC - Bibit ~3%)":
        st.info("💡 **Rekomendasi Rencana:** Total bahan bibit wewangian (Top+Heart+Base) ±3%, Fixative ±2%, Pelarut/Absolute ±95%")
    elif concentration_type == "Eau de Toilette (EDT - Bibit ~10%)":
        st.info("💡 **Rekomendasi Rencana:** Total bahan bibit wewangian (Top+Heart+Base) ±10%, Fixative ±2%, Pelarut/Absolute ±88%")
    elif concentration_type == "Eau de Parfum (EDP - Bibit ~20%)":
        st.info("💡 **Rekomendasi Rencana:** Total bahan bibit wewangian (Top+Heart+Base) ±20%, Fixative ±2%, Pelarut/Absolute ±78%")
    elif concentration_type == "Extrait de Parfum (Bibit ~30%)":
        st.info("💡 **Rekomendasi Rencana:** Total bahan bibit wewangian (Top+Heart+Base) ±30%, Fixative ±3%, Pelarut/Absolute ±67%")

with col_g2:
    st.subheader("📂 Upload Data Bahan Baku (Opsional)")
    st.write("Anda bisa mengunggah file Excel (.xlsx) atau .csv yang berisi data struktur bahan baku Anda.")
    uploaded_file = st.file_uploader("Pilih file data bahan Anda", type=["csv", "xlsx"])

# Data awal / template default aplikasi
initial_data = {
    "Nama Raw Material": ["Bergamot Oil", "Jasmine Absolute", "Cedarwood Oil", "Absolute/Pelarut", "Fixative/Pengikat"],
    "Kategori Notes": ["Top Notes", "Heart Notes", "Base Notes", "Solvent / Pelarut", "Fixative / Pengikat"],
    "Volume Dibeli (ml)": [50.0, 50.0, 50.0, 1000.0, 100.0],
    "Harga Beli (Rp)": [150000, 250000, 200000, 120000, 150000],
    "Rasio Racikan (%)": [10.0, 10.0, 10.0, 68.0, 2.0]
}
df_template = pd.DataFrame(initial_data)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            uploaded_df = pd.read_csv(uploaded_file)
        else:
            uploaded_df = pd.read_excel(uploaded_file)
        
        # LOGIKA PERBAIKAN: Menyelaraskan nama kolom secara otomatis jika tidak pas
        rename_dict = {}
        for col in uploaded_df.columns:
            col_clean = str(col).strip().lower()
            if "nama" in col_clean or "material" in col_clean or "bahan" in col_clean:
                rename_dict[col] = "Nama Raw Material"
            elif "kategori" in col_clean or "notes" in col_clean or "jenis" in col_clean:
                rename_dict[col] = "Kategori Notes"
            elif "volume" in col_clean or "vol" in col_clean:
                rename_dict[col] = "Volume Dibeli (ml)"
            elif "harga" in col_clean or "beli" in col_clean or "modal" in col_clean:
                rename_dict[col] = "Harga Beli (Rp)"
            elif "rasio" in col_clean or "racikan" in col_clean or "persen" in col_clean or "%" in col_clean:
                rename_dict[col] = "Rasio Racikan (%)"
        
        uploaded_df = uploaded_df.rename(columns=rename_dict)
        
        # Memastikan kolom yang wajib ada tetap tersedia di dataframe
        for required_col in df_template.columns:
            if required_col not in uploaded_df.columns:
                uploaded_df[required_col] = df_template[required_col] if required_col == "Kategori Notes" else 0.0
                
        df_template = uploaded_df[df_template.columns]
        st.success("✅ Data berhasil dimuat dan disesuaikan secara otomatis!")
    except Exception as e:
        st.error(f"Gagal membaca file: {e}. Menggunakan template bawaan.")

st.subheader("📊 Tabel Formulasi Bahan Baku")
st.write("Klik dua kali pada kolom 'Kategori Notes' untuk memilih peran bahan wewangian Anda.")

edited_df = st.data_editor(
    df_template, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Kategori Notes": st.column_config.SelectboxColumn(
            options=["Top Notes", "Heart Notes", "Base Notes", "Solvent / Pelarut", "Fixative / Pengikat"], 
            required=True
        ),
        "Harga Beli (Rp)": st.column_config.NumberColumn(format="Rp %d"),
        "Volume Dibeli (ml)": st.column_config.NumberColumn(format="%.1f ml"),
        "Rasio Racikan (%)": st.column_config.NumberColumn(format="%.2f %%")
    }
)

# Menghitung modal dasar per ml
edited_df["Volume Dibeli (ml)"] = pd.to_numeric(edited_df["Volume Dibeli (ml)"], errors='coerce').fillna(1.0)
edited_df["Harga Beli (Rp)"] = pd.to_numeric(edited_df["Harga Beli (Rp)"], errors='coerce').fillna(0.0)
edited_df["Rasio Racikan (%)"] = pd.to_numeric(edited_df["Rasio Racikan (%)"], errors='coerce').fillna(0.0)

edited_df["Modal per ml (Rp)"] = edited_df["Harga Beli (Rp)"] / edited_df["Volume Dibeli (ml)"]
edited_df["Modal per ml (Rp)"] = edited_df["Modal per ml (Rp)"].fillna(0)
total_percentage = edited_df["Rasio Racikan (%)"].sum()

col_p1, col_p2 = st.columns(2)
with col_p1:
    st.metric(label="Total Akumulasi Rasio Bahan Saat Ini", value=f"{total_percentage:.2f} %")
with col_p2:
    if total_percentage != 100.0:
        st.warning("⚠️ Total akumulasi seluruh bahan harus tepat 100% untuk kalkulasi HPP yang akurat.")
    else:
        st.success("✅ Formulasi klop! Total akumulasi tepat 100%.")

st.markdown("---")

# --- 2. TABS UNTUK FITUR APLIKASI ---
tab0, tab1, tab2, tab3 = st.tabs(["🔍 🤖 AI Asisten Riset Harga", "📊 Perhitungan HPP & Laba", "🔮 AI Filosofi & Storytelling", "🤖 Kontrol Sisa Stok"])

# --- TAB 0: ASISTEN RISET HARGA ---
with tab0:
    st.header("🔍 AI Market Price Researcher")
    st.write("Cari tahu estimasi kisaran harga raw material parfum di pasar lokal Indonesia secara cepat.")
    
    if not api_key:
        st.warning("⚠️ Masukkan Google Gemini API Key di sidebar untuk mengaktifkan fitur riset harga ini.")
    else:
        search_material = st.text_input("Ketik nama bahan baku wewangian (Contoh: Iso E Super, Galaxolide, Lavender Oil murni):")
        
        if st.button("🔍 Cek Estimasi Pasar & Sumber"):
            if not search_material:
                st.error("Silakan masukkan nama bahan baku terlebih dahulu.")
            else:
                with st.spinner(f"AI sedang meriset estimasi pasaran untuk {search_material}..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = f"""
                        Kamu adalah konsultan pengadaan bahan baku industri kosmetik dan wewangian di Indonesia.
                        Berikan analisis ringkas untuk bahan baku berikut: '{search_material}'
                        
                        Tampilkan output dalam format Markdown:
                        1. **Estimasi Rentang Harga Pasaran di Indonesia** (Per ml/gram/kg di supplier lokal).
                        2. **Karakteristik Mutu** (Cara membedakan barang berkualitas/murni vs oplosan).
                        3. **Rekomendasi Pembelian** (Tips mencari seller tepercaya di marketplace lokal).
                        """
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                        st.markdown("---")
                        st.info(f"💡 **Hasil Analisis Pasar AI untuk: {search_material}**")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Gagal memanggil layanan AI: {e}")

# --- TAB 1: HPP & DIAGRAM ---
with tab1:
    st.header("Analisis HPP & Harga Jual")
    
    if total_percentage > 0:
        st.write("📐 **Struktur Piramida Aroma Terpeta (Diagram Batang):**")
        notes_summary = edited_df.groupby("Kategori Notes")["Rasio Racikan (%)"].sum().reset_index()
        st.bar_chart(data=notes_summary, x="Kategori Notes", y="Rasio Racikan (%)", color="Kategori Notes", use_container_width=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        target_bottles = st.number_input("Target Produksi (Botol)", min_value=1, value=50, key="tb")
        bottle_size = st.number_input("Ukuran Botol (ml)", min_value=5, value=50, key="bs")
        price_bottle = st.number_input("Biaya Kemasan + Stiker (per pcs)", min_value=0, value=6000, key="pb")
    with col_f2:
        pricing_method = st.radio("Metode Penentuan Harga Jual:", ["Target Markup (Kenaikan dari Modal)", "Target Margin Laba Kotor (%)"], key="pm")
        if pricing_method == "Target Markup (Kenaikan dari Modal)":
            markup_pct = st.slider("Persentase Kenaikan Harga (%)", 50, 500, 200, step=10, key="mp")
        else:
            margin_pct = st.slider("Target Margin Laba Kotor (%)", 10, 90, 60, step=5, key="map")

    edited_df["Vol Needed per Bottle (ml)"] = (edited_df["Rasio Racikan (%)"] / 100) * bottle_size
    edited_df["Cost per Bottle (Rp)"] = edited_df["Vol Needed per Bottle (ml)"] * edited_df["Modal per ml (Rp)"]
    total_liquid_cost_per_bottle = edited_df["Cost per Bottle (Rp)"].sum()
    hpp_per_bottle = total_liquid_cost_per_bottle + price_bottle
    total_production_cost = hpp_per_bottle * target_bottles

    if pricing_method == "Target Markup (Kenaikan dari Modal)":
        suggested_price = hpp_per_bottle * (1 + (markup_pct / 100))
    else:
        suggested_price = hpp_per_bottle / (1 - (margin_pct / 100)) if margin_pct < 100 else hpp_per_bottle

    total_revenue = suggested_price * target_bottles
    total_profit = total_revenue - total_production_cost

    st.markdown("---")
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.write("📋 **Rincian Takaran Racikan per Botol:**")
        # Perbaikan proteksi pembacaan baris yang aman
        for _, row in edited_df.iterrows():
            if "Rasio Racikan (%)" in row and row["Rasio Racikan (%)"] > 0:
                material_name = row.get("Nama Raw Material", "Bahan Tanpa Nama")
                note_cat = row.get("Kategori Notes", "Uncategorized")
                vol_needed = row.get("Vol Needed per Bottle (ml)", 0.0)
                cost_b = row.get("Cost per Bottle (Rp)", 0.0)
                st.write(f"* **{material_name}** ({note_cat}): {vol_needed:.2f} ml (Biaya: Rp {cost_b:,.0f})")
    with res_c2:
        st.metric(label="Harga Pokok Penjualan (HPP) per Botol", value=f"Rp {hpp_per_bottle:,.0f}")
        st.metric(label="💡 Saran Harga Jual Komersial", value=f"Rp {suggested_price:,.0f}", delta=f"Laba Kotor/Botol: Rp {suggested_price - hpp_per_bottle:,.0f}")

# --- TAB 2: AI FILOSOFI ---
with tab2:
    st.header("🔮 AI Fragrance Storyteller")
    if not api_key:
        st.warning("⚠️ Masukkan API Key.")
    else:
        active_ingredients = edited_df[edited_df["Rasio Racikan (%)"] > 0]
        ingredients_string = ", ".join([f"{r.get('Nama Raw Material', 'Bahan')} ({r.get('Kategori Notes', 'Note')} - {r.get('Rasio Racikan (%)', 0)}% )" for _, r in active_ingredients.iterrows()])
        target_pasar = st.text_input("Spesifikasi Target Pasar:")
        catatan_tambahan = st.text_area("Nuansa / Kesan Emosional Varian:")
        if st.button("✨ Racik Cerita Varian"):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Kamu adalah Master Perfumer. Analisis formula komersial ini:
                Struktur Komponen: {ingredients_string}
                Target Pasar: {target_pasar}
                Nuansa Impian: {catatan_tambahan}
                
                Buatkan: 3 Opsi Nama Varian Menarik, 2 Paragraf Narasi Filosofi Produk Indah, dan Evaluasi Taktis apakah proporsi kombinasi Top, Heart, dan Base Notes yang diisi user sudah harmonis atau butuh penyesuaian fiksasi. Output dalam Markdown.
                """
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                st.markdown(response.text)
            except Exception as e: st.error(f"Eror: {e}")

# --- TAB 3: KONTROL STOK ---
with tab3:
    st.header("🤖 Smart Stock Optimizer")
    stok_list = []
    opt_cols = st.columns(2)
    count = 0
    for idx, row in edited_df.iterrows():
        if row["Rasio Racikan (%)"] > 0:
            current_col = opt_cols[0] if count % 2 == 0 else opt_cols[1]
            material_name = row.get("Nama Raw Material", f"Bahan {idx}")
            vol_dibeli = row.get("Volume Dibeli (ml)", 100.0)
            vol_per_b = row.get("Vol Needed per Bottle (ml)", 0.0)
            
            user_stok = current_col.number_input(f"Stok: {material_name} (ml)", min_value=0.0, value=float(vol_dibeli), key=f"stok_v9_{idx}")
            stok_list.append((material_name, user_stok, vol_per_b))
            count += 1
    if stok_list:
        max_bottles_possible = [stok // vol if vol > 0 else float('inf') for _, stok, vol in stok_list]
        final_max_production = int(min(max_bottles_possible)) if max_bottles_possible else 0
        st.success(f"Batas maksimal produksi riil Anda saat ini adalah **{final_max_production} botol**.")
