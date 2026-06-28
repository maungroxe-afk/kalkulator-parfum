import streamlit as st
import pandas as pd
import json
from google import genai
import plotly.express as px

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro Perfumer Studio V.22", layout="wide")

# --- 2. SISTEM KEAMANAN (PASSWORD) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "UCP2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center; color: #d4af37; margin-top: 100px;'>Pro Perfumer Studio V.22</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Sistem Formulasi Eksklusif</p>", unsafe_allow_html=True)
        col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
        with col_login2:
            st.text_input("Kunci Akses", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        col_login1, col_login2, col_login3 = st.columns([1, 2, 1])
        with col_login2:
            st.error("Kunci akses tidak valid.")
            st.text_input("Kunci Akses", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password():
    st.stop()

# --- 3. ESTETIKA UI (CUSTOM CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #e4e4e7; }
    .note-box { padding: 18px 24px; border-radius: 6px; border-left: 3px solid #d4af37; background-color: #1a1c23; margin-bottom: 12px; }
    .note-title { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #d4af37; margin-bottom: 6px; }
    .note-content { font-size: 0.95rem; color: #e4e4e7; line-height: 1.5; }
    div[data-testid="stMetricValue"] { color: #d4af37 !important; }
    hr { border-top: 1px solid rgba(255, 255, 255, 0.1) !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. FUNGSI PENDUKUNG AI ---
def panggil_ai(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        return "SISTEM_OFF: API Key belum dikonfigurasi di Cloud Secrets."
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): return "ERROR_429"
        return f"KESALAHAN_SISTEM: {str(e)}"

@st.cache_data
def get_ai_complex_accords(materials_list):
    prompt = f"Klasifikasikan molekul raw material ini ke Main Accords (maks 3 per bahan): [{', '.join(materials_list)}]. Pilihan: [Citrus, Floral, Woody, Amber, Animalic, Green, Fruity, Musky, Spicy, Sweet, Powdery, Leather, Neutral]. Berikan HANYA JSON object bersih tanpa markdown: {{\"Bahan\": [\"Accord1\", \"Accord2\"]}}"
    hasil = panggil_ai(prompt)
    try:
        return json.loads(hasil.replace("```json", "").replace("```", "").strip())
    except:
        return {}

# --- 5. LOGIKA FORMULASI & DATA ---
st.title("Pro Perfumer Studio V.22")
st.write("Sistem formulasi presisi, pemetaan karakter aroma otomatis, dan manajemen biaya.")

col_a, col_b = st.columns(2)
with col_a:
    concentration_type = st.selectbox(
        "Konsentrasi Target",
        ["Custom (Ikuti Tabel)", "Eau de Cologne (3%)", "Eau de Toilette (10%)", "Eau de Parfum (20%)", "Extrait de Parfum (30%)"]
    )
with col_b:
    uploaded_file = st.file_uploader("Impor Data Formulasi", type=["csv", "xlsx"])

# Inisialisasi Data
initial_data = {
    "Nama Raw Material": ["Ambroxan", "Bergamot Oil", "Jasmine Absolute", "Cedarwood Oil", "Absolute Pelarut", "Fixative Agent"],
    "Kategori Notes": ["Base Notes", "Top Notes", "Heart Notes", "Base Notes", "Solvent", "Fixative"],
    "Volume Dibeli (ml)": [10.0, 50.0, 50.0, 50.0, 1000.0, 100.0],
    "Harga Beli (Rp)": [300000, 150000, 250000, 200000, 120000, 150000],
    "Rasio Racikan (%)": [5.0, 10.0, 15.0, 5.0, 63.0, 2.0]
}
df = pd.DataFrame(initial_data) if uploaded_file is None else (pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file))

edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Parsing & Kalkulasi
edited_df["Modal per ml"] = edited_df["Harga Beli (Rp)"] / edited_df["Volume Dibeli (ml)"]
target_eo = 0.0
if "3%" in concentration_type: target_eo = 3.0
elif "10%" in concentration_type: target_eo = 10.0
elif "20%" in concentration_type: target_eo = 20.0
elif "30%" in concentration_type: target_eo = 30.0

fragrance_mask = edited_df["Kategori Notes"].isin(["Top Notes", "Heart Notes", "Base Notes"])
total_fragrance_pct = edited_df.loc[fragrance_mask, "Rasio Racikan (%)"].sum()
bottle_size = st.sidebar.number_input("Ukuran Botol (ml)", value=50)

edited_df["Vol Aktual (ml)"] = 0.0
if target_eo > 0 and total_fragrance_pct > 0:
    # Auto-scaling bibit
    for idx, row in edited_df[fragrance_mask].iterrows():
        edited_df.at[idx, "Vol Aktual (ml)"] = ((row["Rasio Racikan (%)"] / total_fragrance_pct) * target_eo / 100) * bottle_size
    # Sisa untuk pelarut/fixative
    support_mask = edited_df["Kategori Notes"].isin(["Solvent", "Fixative"])
    total_support_pct = edited_df.loc[support_mask, "Rasio Racikan (%)"].sum()
    if total_support_pct > 0:
        for idx, row in edited_df[support_mask].iterrows():
            edited_df.at[idx, "Vol Aktual (ml)"] = ((row["Rasio Racikan (%)"] / total_support_pct) * (100 - target_eo) / 100) * bottle_size
else:
    edited_df["Vol Aktual (ml)"] = (edited_df["Rasio Racikan (%)"] / 100) * bottle_size

edited_df["HPP Bahan"] = edited_df["Vol Aktual (ml)"] * edited_df["Modal per ml"]
edited_df["Persentase Murni (%)"] = (edited_df["Vol Aktual (ml)"] / bottle_size) * 100

st.markdown("<hr>", unsafe_allow_html=True)

# --- 6. TABS APLIKASI ---
tab_chat, tab_acc, tab_enc, tab_hpp, tab_stok = st.tabs([
    "Copilot Cerita", "Analisis Accords", "Ensiklopedia Bahan", "Akuntansi Produksi", "Manajemen Stok"
])

# Ambil data aktif untuk AI
active_mat = edited_df[edited_df["Rasio Racikan (%)"] > 0]["Nama Raw Material"].tolist()
summary_formula = ", ".join([f"{r['Nama Raw Material']} ({r['Kategori Notes']} - {r['Persentase Murni (%)']:.1f}%)" for _, r in edited_df[edited_df["Vol Aktual (ml)"] > 0].iterrows()])

# TAB 1: COPILOT
with tab_chat:
    st.write("### Arsitektur Piramida Olfaktori")
    for cat in ["Top Notes", "Heart Notes", "Base Notes"]:
        items = edited_df[(edited_df["Vol Aktual (ml)"] > 0) & (edited_df["Kategori Notes"] == cat)]
        content = ", ".join([f"{r['Nama Raw Material']} ({r['Persentase Murni (%)']:.1f}%)" for _, r in items.iterrows()])
        st.markdown(f'<div class="note-box"><div class="note-title">{cat}</div><div class="note-content">{content if content else "Komponen belum ditentukan"}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("### Narasi Eksklusif AI")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    if st.button("Hasilkan Narasi Awal"):
        with st.spinner("Menganalisis profil olfaktori..."):
            prompt = f"Bertindaklah sebagai Senior Perfumer. Analisis formula: [{summary_formula}]. Buatkan 3 usulan nama mewah, filosofi 2 paragraf, dan breakdown aromanya."
            hasil = panggil_ai(prompt)
            if hasil == "ERROR_429": st.warning("AI sedang sibuk, mohon tunggu 1 menit.")
            else: st.session_state.chat_history.append({"role": "assistant", "content": hasil})
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    user_input = st.chat_input("Berikan instruksi revisi (misal: 'Ubah filosofi menjadi lebih maskulin')")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Menyusun ulang..."):
            prompt_chat = f"Formula: {summary_formula}. Riwayat: {st.session_state.chat_history}. Permintaan Baru: {user_input}"
            hasil = panggil_ai(prompt_chat)
            st.session_state.chat_history.append({"role": "assistant", "content": hasil})
            st.rerun()

# TAB 2: ACCORDS
with tab_acc:
    st.write("### Kluster Roda Aroma (100% Konsentrat)")
    if not active_mat: st.info("Masukkan data formulasi terlebih dahulu.")
    else:
        mapping = get_ai_complex_accords(active_mat)
        accord_data = []
        for _, r in edited_df[fragrance_mask].iterrows():
            accs = mapping.get(r["Nama Raw Material"], ["Neutral"])
            for a in accs:
                if a != "Neutral":
                    accord_data.append({"Accord": a, "Value": r["Vol Aktual (ml)"] / len(accs)})
        
        if accord_data:
            df_acc = pd.DataFrame(accord_data).groupby("Accord")["Value"].sum().reset_index()
            fig = px.pie(df_acc, values="Value", names="Accord", hole=0.5, color_discrete_sequence=px.colors.sequential.Burgyl)
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Sedang menyelaraskan data karakter aroma...")

# TAB 3: ENSIKLOPEDIA
with tab_enc:
    st.write("### Pencarian Karakteristik Raw Material")
    search_q = st.text_input("Nama Bahan (Kimia Aroma/Alami)")
    if st.button("Cari Detail"):
        with st.spinner("Mengakses database..."):
            hasil = panggil_ai(f"Jelaskan secara teknis bahan parfum: {search_q}. Berikan profil aroma, batas aman penggunaan kulit, dan risiko alergi.")
            if hasil == "ERROR_429": st.warning("AI sibuk, coba lagi nanti.")
            else: st.markdown(hasil)

# TAB 4: AKUNTANSI PRODUKSI
with tab1:
    st.write("### Kalkulasi Keuangan & Kapasitas Produksi")
    packing_cost = st.number_input("Biaya Kemasan & Botol (per pcs)", value=6500)
    markup = st.slider("Margin Keuntungan (%)", 50, 500, 200)
    
    hpp_liquid = edited_df["HPP Bahan"].sum()
    hpp_total = hpp_liquid + packing_cost
    harga_jual = hpp_total * (1 + markup/100)
    
    # Hitung Kapasitas Maksimal
    max_bots = []
    for _, r in edited_df[edited_df["Vol Aktual (ml)"] > 0].iterrows():
        max_bots.append(r["Volume Dibeli (ml)"] // r["Vol Aktual (ml)"])
    kapasitas = int(min(max_bots)) if max_bots else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("HPP per Botol", f"Rp {hpp_total:,.0f}")
    c2.metric("Saran Harga Jual", f"Rp {harga_jual:,.0f}")
    c3.metric("Kapasitas Produksi", f"{kapasitas} Pcs")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write(f"### Proyeksi Batch Maksimal ({kapasitas} Botol)")
    p1, p2, p3 = st.columns(3)
    investasi = hpp_total * kapasitas
    omzet = harga_jual * kapasitas
    p1.metric("Total Investasi", f"Rp {investasi:,.0f}")
    p2.metric("Estimasi Omzet", f"Rp {omzet:,.0f}")
    p3.metric("Potensi Net Laba", f"Rp {omzet - investasi:,.0f}")

# TAB 5: STOK GUDANG
with tab2:
    st.write("### Optimasi Bahan & Neraca Gudang")
    for _, r in edited_df[edited_df["Vol Aktual (ml)"] > 0].iterrows():
        col_s1, col_s2 = st.columns([2, 1])
        sisa = r["Volume Dibeli (ml)"] - (r["Vol Aktual (ml)"] * kapasitas)
        col_s1.write(f"**{r['Nama Raw Material']}**")
        col_s2.write(f"Sisa: {sisa:.1f} ml")
    st.success(f"Seluruh kalkulasi disesuaikan untuk target produksi {kapasitas} botol.")
