import streamlit as st
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

# 1. Konfigurasi Halaman & Tema UI
st.set_page_config(
    page_title="Ren'Py Turbo Translator V8.0",
    page_icon="⚡",
    layout="centered"
)

# Custom CSS untuk mempercantik tampilan di HP & PC
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #334155;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.6rem;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 700;
        padding: 0.6rem 1rem;
    }
    .stDownloadButton>button {
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        font-weight: 700;
        width: 100%;
        padding: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚡ Ren'Py Turbo Translator V8.0</h1>
    <p>Terjemah skrip .rpy super cepat tanpa API Key • Tag { } [ ] \\n aman 100%</p>
</div>
""", unsafe_allow_html=True)

# 2. Fungsi Pelindung Tag & Variabel
TAG_PATTERN = re.compile(r'\{[^}]*\}|\[[^\]]*\]|\\[nrt"\\]|\.{2,3}|~|\bnone\b', flags=re.IGNORECASE)

def protect(text):
    tags = TAG_PATTERN.findall(text)
    temp = text
    for i, t in enumerate(tags):
        temp = temp.replace(t, f'[[[{i}]]]', 1)
    return temp, tags

def unprotect(text, tags):
    for i, t in enumerate(tags):
        # Tangani jika Google menambahkan spasi di sekitar penanda
        text = re.sub(rf'\[\[\[\s*{i}\s*\]\]\]', lambda _: t, text)
    return text

def translate_chunk(chunk_id, chunk_texts):
    translator = GoogleTranslator(source='auto', target='id')
    for attempt in range(3):
        try:
            results = translator.translate_batch(chunk_texts)
            return chunk_id, results
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return chunk_id, chunk_texts

# 3. Antarmuka Pengguna (UI)
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("📂 Pilih file skrip (.rpy)", type=["rpy", "txt"])
with col2:
    workers = st.selectbox("🚀 Kecepatan", options=[3, 5, 8], index=1, format_func=lambda x: f"{x}x Turbo")

# Inisialisasi Session State agar hasil tidak hilang saat diklik
if "translated_data" not in st.session_state:
    st.session_state.translated_data = None
if "output_filename" not in st.session_state:
    st.session_state.output_filename = ""
if "stats" not in st.session_state:
    st.session_state.stats = {}

# Regex menangkap dialog karakter (e "teks") maupun narator ("teks"), kecuali baris 'old'
DIALOG_PATTERN = re.compile(r'^(\s*(?!old\b|image\b|define\b|default\b)(?:\w+\s+)?)(")((?:[^"\\]|\\.)*)(")(.*)$')

if uploaded_file:
    if st.button("🚀 TERJEMAHKAN SEKARANG", type="primary", use_container_width=True):
        start_time = time.time()
        content = uploaded_file.read().decode('utf-8', errors='ignore')
        lines = content.split('\n')
        
        batch_texts = []
        batch_meta = []

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            m = DIALOG_PATTERN.match(line)
            if m:
                prefix, q1, text, q2, suffix = m.groups()
                if text.strip() and text.strip().lower() != "none":
                    clean_text, tags = protect(text)
                    if clean_text.strip() and not re.fullmatch(r'(\[\[\[\d+\]\]\]|\s)+', clean_text):
                        batch_texts.append(clean_text)
                        batch_meta.append((idx, prefix, tags, suffix))

        total_lines = len(batch_texts)
        if total_lines == 0:
            st.warning("Tidak ditemukan baris dialog yang perlu diterjemahkan di file ini.")
        else:
            progress_bar = st.progress(0, text="Memulai mesin penerjemah...")
            chunk_size = 120
            chunks = [
                (i // chunk_size, batch_texts[i:i + chunk_size])
                for i in range(0, total_lines, chunk_size)
            ]
            
            translated_chunks = {}
            completed = 0

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(translate_chunk, cid, ctexts): len(ctexts) for cid, ctexts in chunks}
                for future in as_completed(futures):
                    cid, res = future.result()
                    translated_chunks[cid] = res
                    completed += futures[future]
                    pct = min(1.0, completed / total_lines)
                    progress_bar.progress(pct, text=f"⚡ Menerjemahkan: {completed} / {total_lines} baris ({int(pct*100)}%)")

            # Gabungkan kembali hasil ke baris asli
            flat_results = []
            for cid in sorted(translated_chunks.keys()):
                flat_results.extend(translated_chunks[cid])

            for (idx, prefix, tags, suffix), result in zip(batch_meta, flat_results):
                safe_res = result if result else ""
                final_text = unprotect(safe_res, tags)
                # Pastikan tanda kutip ganda di dalam dialog tetap aman
                final_text = re.sub(r'(?<!\\)"', r'\"', final_text)
                lines[idx] = f'{prefix}"{final_text}"{suffix}'

            elapsed = round(time.time() - start_time, 1)
            st.session_state.translated_data = '\n'.join(lines)
            st.session_state.output_filename = "ID_V8_" + uploaded_file.name
            st.session_state.stats = {"lines": total_lines, "time": elapsed}
            progress_bar.empty()

# 4. Tampilan Hasil & Tombol Unduh Permanen
if st.session_state.translated_data:
    st.success(f"🎉 Selesai! **{st.session_state.stats['lines']} baris** diterjemahkan dalam **{st.session_state.stats['time']} detik**.")
    
    st.download_button(
        label=f"⬇️ UNDUH FILE ({st.session_state.output_filename})",
        data=st.session_state.translated_data.encode('utf-8'),
        file_name=st.session_state.output_filename,
        mime="text/plain",
        use_container_width=True
    )

    with st.expander("👀 Pratinjau & Salin Manual (Jika Browser HP Memblokir Unduhan)"):
        st.text_area(
            "Hasil Skrip (.rpy):",
            value=st.session_state.translated_data[:15000],
            height=200,
            help="Menampilkan 15.000 karakter pertama. Gunakan tombol Unduh di atas untuk file utuh."
        )

st.caption("🛡️ Perlindungan otomatis untuk tag {i}, {b}, [variabel], \\n, dan tanda kutip.")
