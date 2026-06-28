import streamlit as st
import pandas as pd
import json
from google import genai

st.set_page_config(page_title="UCP ALPHA - Pro Perfumer Studio", layout="wide")

st.title("🧪 UCP ALPHA - Pro Perfumer Studio v15")
st.write("Studio Formulasi Parfum dengan Diagram Main Accords Otomatis Berbasis AI dan HPP Presisi.")

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
        ["Custom (Ikuti Persentase Tabel 100%)", "Eau de Cologne (EDC - Target Bibit 3%)", "Eau de Toilette (EDT - Target Bibit 10%)", "Eau de Parfum (EDP - Target Bibit 20%)", "Extrait de Parfum (Target Bibit 30%)"]
    )
    
    target_essential_oil = 0.0
    auto_scale = False
    
    if "EDC" in concentration_type:
        target_essential_oil = 3.0
        auto_scale = True
    elif "EDT" in concentration_type:
        target_essential_oil = 10.0
        auto_scale = True
    elif "EDP" in concentration_type:
        target_essential_oil = 20.0
        auto_scale = True
    elif "Extrait" in concentration_type:
        target_essential_oil = 30.0
        auto_scale = True

with col_g2:
    st.subheader("📂 Upload Data Bahan Baku (Opsional)")
    st.write("Anda bisa mengunggah file Excel (.xlsx) or .csv yang berisi data struktur bahan baku Anda.")
    uploaded_file = st.file_uploader("Pilih file data bahan Anda", type=["csv", "xlsx"])

# Data template awal bawaan aplikasi
initial_data = {
    "Nama Raw Material": ["Ambroxan", "Bergamot Oil", "Jasmine Absolute", "Cedarwood Oil", "Absolute/Pelarut", "Fixative/Pengikat"],
    "Kategori Notes (Manual/Bebas)": ["Base Notes", "Top Notes", "Heart Notes", "Base Notes", "Solvent / Pelarut", "Fixative / Pengikat"],
    "Volume Dibeli (ml)": [10.0, 50.0, 50.0, 50.0, 1000.0, 100.0],
    "Harga Beli (Rp)": [300000, 150000, 250000, 200000, 120000, 150000],
    "Rasio Racikan (%)": [5.0, 10.0, 10.0, 5.0, 68.0, 2.0]
}
df_template = pd.DataFrame(initial_data)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            uploaded_df = pd.read_csv(uploaded_file)
        else:
            uploaded_df = pd.read_excel(uploaded_file)
        
        rename_dict = {}
        for col in uploaded_df.columns:
            col_clean = str(col).strip().lower()
            if "nama" in col_clean or "material" in col_clean or "bahan" in col_clean:
                rename_dict[col] = "Nama Raw Material"
            elif "kategori" in col_clean or "notes" in col_clean or "jenis" in col_clean:
                rename_dict[col] = "Kategori Notes (Manual/Bebas)"
            elif "volume" in col_clean or "vol" in col_clean:
                rename_dict[col] = "Volume Dibeli (ml)"
            elif "harga" in col_clean or "beli" in col_clean or "modal" in col_clean:
                rename_dict[col] = "Harga Beli (Rp)"
            elif "rasio" in col_clean or "racikan" in col_clean or "persen" in col_clean or "%" in col_clean:
                rename_dict[col] = "Rasio Racikan (%)"
        
        uploaded_df = uploaded_df.rename(columns=rename_dict)
        for required_col in df_template.columns:
            if required_col not in uploaded_df.columns:
                uploaded_df[required_col] = df_template[required_col] if required_col == "Kategori Notes (Manual/Bebas)" else 0.0
        df_template = uploaded_df[df_template.columns]
        st.success("✅ Data berhasil dimuat!")
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")

st.subheader("📊 Tabel Formulasi Bahan Baku")
edited_df = st.data_editor(
    df_template, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Kategori Notes (Manual/Bebas)": st.column_config.SelectboxColumn(
            options=["Top Notes", "Heart Notes", "Base Notes", "Solvent / Pelarut", "Fixative / Pengikat"], required=True
        ),
        "Harga Beli (Rp)": st.column_config.NumberColumn(format="Rp %d"),
        "Volume Dibeli (ml)": st.column_config.NumberColumn(format="%.1f ml"),
        "Rasio Racikan (%)": st.column_config.NumberColumn(format="%.2f %%")
    }
)

# Parsing Tipe Data
edited_df["Volume Dibeli (ml)"] = pd.to_numeric(edited_df["Volume Dibeli (ml)"], errors='coerce').fillna(1.0)
edited_df["Harga Beli (Rp)"] = pd.to_numeric(edited_df["Harga Beli (Rp)"], errors='coerce').fillna(0.0)
edited_df["Rasio Racikan (%)"] = pd.to_numeric(edited_df["Rasio Racikan (%)"], errors='coerce').fillna(0.0)
edited_df["Modal per ml (Rp)"] = edited_df["Harga Beli (Rp)"] / edited_df["Volume Dibeli (ml)"]

total_percentage = edited_df["Rasio Racikan (%)"].sum()
st.markdown("---")

# --- 2. TABS UNTUK FITUR APLIKASI ---
tab_enc, tab_sec, tab0, tab1, tab2, tab3 = st.tabs(["📐 AI Analisis Piramida & Accords", "📚 AI Ensiklopedia & Keamanan Bahan", "🔍 AI Asisten Riset Harga", "📊 Perhitungan HPP & Laba", "🤖 Kontrol Sisa Stok"])

# --- ⚙️ LOGIKA UTAMA OTOMATISASI KONSENTRASI PARFUM ---
fragrance_mask = edited_df["Kategori Notes (Manual/Bebas)"].isin(["Top Notes", "Heart Notes", "Base Notes"])
solvent_mask = edited_df["Kategori Notes (Manual/Bebas)"] == "Solvent / Pelarut"
fixative_mask = edited_df["Kategori Notes (Manual/Bebas)"] == "Fixative / Pengikat"

total_fragrance_tabel_pct = edited_df.loc[fragrance_mask, "Rasio Racikan (%)"].sum()
total_solvent_tabel_pct = edited_df.loc[solvent_mask, "Rasio Racikan (%)"].sum()
total_fixative_tabel_pct = edited_df.loc[fixative_mask, "Rasio Racikan (%)"].sum()

# Inisialisasi kolom kalkulasi riil volume
edited_df["Vol Needed per Bottle (ml)"] = 0.0

# Memasukkan target botol dummy/default jika di tab HPP belum diinput
bottle_size_actual = 50.0

if auto_scale and total_fragrance_tabel_pct > 0:
    target_non_fragrance = 100.0 - target_essential_oil
    for idx, row in edited_df[fragrance_mask].iterrows():
        kontribusi_proporsional = row["Rasio Racikan (%)"] / total_fragrance_tabel_pct
        real_pct_in_bottle = kontribusi_proporsional * target_essential_oil
        edited_df.at[idx, "Vol Needed per Bottle (ml)"] = (real_pct_in_bottle / 100.0) * bottle_size_actual
        
    total_support_pct = total_solvent_tabel_pct + total_fixative_tabel_pct
    if total_support_pct > 0:
        for idx, row in edited_df[solvent_mask | fixative_mask].iterrows():
            kontribusi_proporsional = row["Rasio Racikan (%)"] / total_support_pct
            real_pct_in_bottle = kontribusi_proporsional * target_non_fragrance
            edited_df.at[idx, "Vol Needed per Bottle (ml)"] = (real_pct_in_bottle / 100.0) * bottle_size_actual
    else:
        if solvent_mask.any():
            first_solvent_idx = edited_df[solvent_mask].index[0]
            edited_df.at[first_solvent_idx, "Vol Needed per Bottle (ml)"] = (target_non_fragrance / 100.0) * bottle_size_actual
else:
    edited_df["Vol Needed per Bottle (ml)"] = (edited_df["Rasio Racikan (%)"] / 100.0) * bottle_size_actual

# Hitung bobot aktual relatif untuk diagram
edited_df["Persentase Aktual Di Botol (%)"] = (edited_df["Vol Needed per Bottle (ml)"] / bottle_size_actual) * 100

# --- 🌟 TAB 1: DIAGRAM MAIN ACCORDS (OTOMATIS TANPA TOMBOL) ---
with tab_enc:
    st.header("📐 Analisis Sebaran Aroma Otomatis (AI Main Accords Map)")
    
    active_materials = edited_df[edited_df["Rasio Racikan (%)"] > 0]["Nama Raw Material"].tolist()
    
    if not api_key:
        st.warning("⚠️ Masukkan Google Gemini API Key di sidebar untuk memproses sebaran aroma secara otomatis.")
    elif not active_materials:
        st.info("Masukkan komponen bahan yang aktif di tabel di atas untuk memetakan diagram aroma.")
    else:
        # Menjalankan pemetaan AI secara otomatis menggunakan cache state agar tidak over-request
        try:
            client = genai.Client(api_key=api_key)
            materials_json_input = ", ".join(active_materials)
            
            # Request ke AI untuk memetakan rumpun aroma secara instan
            prompt = f"Kamu adalah sistem laboratorium parfum global. Tugasmu mengelompokkan bahan baku ke dalam rumpun aroma utama standar dunia. Daftar bahan baku: [{materials_json_input}]. Klasifikasikan SETIAP bahan di atas ke dalam SALAH SATU kategori berikut secara mutlak: [Citrus, Floral, Woody, Amber, Animalic, Green, Fruity, Musky, Spicy, Sweet / Vanilla, Powdery, Leather, Neutral]. Berikan output HANYA dalam format JSON object bersih seperti contoh berikut tanpa markdown codeblock dan tanpa penjelasan apapun: {{\"Ambroxan\": \"Amber\", \"Bergamot Oil\": \"Citrus\"}}"
            
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            ai_mapping = json.loads(clean_text)
            
            # Map hasil AI ke Dataframe utama
            edited_df["AI_Accords"] = edited_df["Nama Raw Material"].map(ai_mapping).fillna("Neutral")
            
            # Tampilkan Grafik Batang Fragrantica secara otomatis
            viz_df = edited_df[edited_df["AI_Accords"] != "Neutral"]
            if not viz_df.empty:
                chart_data = viz_df.groupby("AI_Accords")["Persentase Aktual Di Botol (%)"].sum().reset_index()
                chart_data = chart_data.sort_values(by="Persentase Aktual Di Botol (%)", ascending=False)
                st.bar_chart(data=chart_data, x="AI_Accords", y="Persentase Aktual Di Botol (%)", color="AI_Accords", use_container_width=True)
                
                st.write("**📌 Detail Klasifikasi Molekul Bahan Baku Anda:**")
                for k, v in ai_mapping.items():
                    if v != "Neutral":
                        st.caption(f"* **{k}** didefinisikan oleh sistem sebagai rumpun aroma **{v}**")
            else:
                st.info("Seluruh komponen saat ini dideteksi sebagai cairan netral/pelarut.")
        except Exception as e:
            st.error(f"AI sedang melakukan sinkronisasi data aroma: {e}")

# --- TAB: ENSIKLOPEDIA ---
with tab_sec:
    st.header("📚 AI Raw Material Encyclopedia")
    if not api_key: st.warning("Masukkan API Key di sidebar.")
    else:
        safety_search = st.text_input("Ketik nama bahan baku yang ingin diperiksa:")
        if st.button("📚 Bedah Karakteristik"):
            with st.spinner("AI memproses..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"Kamu adalah seorang perfumer senior ahli kimia wewangian. Jelaskan tentang bahan baku berikut: {safety_search}. Berikan output rapi format Markdown berisi: 1. Deskripsi Karakteristik Aroma, 2. Rekomendasi Persentase Penggunaan Aman untuk kulit, 3. Potensi Risiko Alergi."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.markdown(response.text)
                except Exception as e: st.error(f"Eror: {e}")

# --- TAB: RISET HARGA ---
with tab0:
    st.header("🔍 AI Market Price Researcher")
    if not api_key: st.warning("Masukkan API Key di sidebar.")
    else:
        search_material = st.text_input("Ketik nama bahan baku wewangian untuk riset harga:")
        if st.button("🔍 Cek Estimasi Pasar"):
            with st.spinner("AI meriset pasar..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"Kamu adalah konsultan pengadaan bahan baku parfum di Indonesia. Berikan analisis ringkas untuk bahan: {search_material}. Tampilkan dalam Markdown: 1. Estimasi Rentang Harga Pasaran di Indonesia, 2. Karakteristik Mutu, 3. Rekomendasi Pembelian lokal."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.markdown(response.text)
                except Exception as e: st.error(f"Eror: {e}")

# --- TAB 1: HPP ---
with tab1:
    st.header("Analisis HPP & Harga Jual")
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

    # Hitung ulang berdasarkan input dinamis user di Tab HPP
    edited_df["Vol Needed per Bottle (ml)"] = (edited_df["Persentase Aktual Di Botol (%)"] / 100.0) * bottle_size
    edited_df["Cost per Bottle (Rp)"] = edited_df["Vol Needed per Bottle (ml)"] * edited_df["Modal per ml (Rp)"]
    total_liquid_cost_per_bottle = edited_df["Cost per Bottle (Rp)"].sum()
    hpp_per_bottle = total_liquid_cost_per_bottle + price_bottle
    total_production_cost = hpp_per_bottle * target_bottles

    if pricing_method == "Target Markup (Kenaikan dari Modal)":
        suggested_price = hpp_per_bottle * (1 + (markup_pct / 100))
    else:
        suggested_price = hpp_per_bottle / (1 - (margin_pct / 100)) if margin_pct < 100 else hpp_per_bottle

    total_revenue = suggested_price * target_bottles
    st.markdown("---")
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.write("📋 **Rincian Takaran per Botol:**")
        for _, row in edited_df.iterrows():
            if row["Vol Needed per Bottle (ml)"] > 0:
                st.write(f"* **{row['Nama Raw Material']}** ({row['Kategori Notes (Manual/Bebas)']}): **{row['Vol Needed per Bottle (ml)']:.2f} ml** (Biaya: Rp {row['Cost per Bottle (Rp)']:,.0f})")
    with res_c2:
        st.metric(label="Harga Pokok Penjualan (HPP) per Botol", value=f"Rp {hpp_per_bottle:,.0f}")
        st.metric(label="💡 Saran Harga Jual Komersial", value=f"Rp {suggested_price:,.0f}")

# --- TAB 2: AI FILOSOFI ---
with tab2:
    st.header("🔮 AI Fragrance Storyteller")
    if not api_key: st.warning("⚠️ Masukkan API Key.")
    else:
        active_ingredients = edited_df[edited_df["Vol Needed per Bottle (ml)"] > 0]
        ingredients_string = ", ".join([f"{r.get('Nama Raw Material', 'Bahan')} ({r.get('Vol Needed per Bottle (ml)', 0):.2f}ml)" for _, r in active_ingredients.iterrows()])
        target_pasar = st.text_input("Spesifikasi Target Pasar:")
        catatan_tambahan = st.text_area("Nuansa / Kesan Emosional Varian:")
        if st.button("✨ Racik Cerita Varian"):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"Kamu adalah Master Perfumer mewah. Analisis formula komersial ini: {ingredients_string}. Jenis Konsentrasi: {concentration_type}. Target Pasar: {target_pasar}. Nuansa Impian: {catatan_tambahan}. Buatkan: 3 Opsi Nama Varian Menarik, 2 Paragraf Narasi Filosofi Produk Indah, dan Evaluasi Taktis mengenai kombinasi aroma tersebut. Output dalam Markdown."
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
        if row["Vol Needed per Bottle (ml)"] > 0:
            current_col = opt_cols[0] if count % 2 == 0 else opt_cols[1]
            material_name = row.get("Nama Raw Material", f"Bahan {idx}")
            vol_dibeli = row.get("Volume Dibeli (ml)", 100.0)
            vol_per_b = row.get("Vol Needed per Bottle (ml)", 0.0)
            user_stok = current_col.number_input(f"Stok: {material_name} (ml)", min_value=0.0, value=float(vol_dibeli), key=f"stok_v15_{idx}")
            stok_list.append((material_name, user_stok, vol_per_b))
            count += 1
    if stok_list:
        max_bottles_possible = [stok // vol if vol > 0 else float('inf') for _, stok, vol in stok_list]
        final_max_production = int(min(max_bottles_possible)) if max_bottles_possible else 0
        st.success(f"Batas maksimal produksi riil Anda saat ini adalah **{final_max_production} botol**.")
