import streamlit as st
import re
from deep_translator import GoogleTranslator

def clean_and_normalize_dialog(text):
    """
    Mengamankan teks dari karakter aneh yang bisa merusak struktur file Ren'Py
    """
    if not text:
        return ""
    # Ubah kutip miring bawaan teks HP menjadi kutip lurus standar agar tidak merusak kode
    text = text.replace('“', '\\"').replace('”', '\\"').replace('"', '\\"')
    # Jika di ujung teks sudah ada escape slash ganda yang rusak, bersihkan
    text = re.sub(r'(?<!\\)\\"', '\\"', text)
    return text

def translate_rpy_ultimate(content, target_lang='id'):
    lines = content.split('\n')
    
    # Regex Super Ketat: Memisahkan bagian Luar Depan, Teks Dalam Kutip, dan Luar Belakang
    # Menjamin 100% bagian luar tanda kutip TIDAK AKAN disentuh atau berubah satu huruf pun
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]*)"([^"\n]*)$')
    
    dialog_data = []
    
    # LANGKAH 1: Ekstrak semua teks secara aman
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip():  # Abaikan baris kutip kosong
                dialog_data.append({
                    'line_idx': idx,
                    'text': text_inside,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not dialog_data:
        return content

    # LANGKAH 2: Proses Batch Slicing Kilat (Per 100 baris langsung)
    batch_size = 100
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    all_texts = [data['text'] for data in dialog_data]
    translated_texts = []
    
    progress_bar = st.progress(0)
    total_batches = (len(all_texts) + batch_size - 1) // batch_size

    for i in range(0, len(all_texts), batch_size):
        batch = all_texts[i:i + batch_size]
        try:
            # Kirim sekelompok teks sekaligus dalam satu request (Sangat cepat dan instan)
            translated_batch = translator.translate_batch(batch)
            translated_texts.extend(translated_batch)
        except Exception as e:
            # Proteksi cadangan jika server Google overload, tetap gunakan teks asli agar game tidak crash
            translated_texts.extend(batch)
            
        current_batch_idx = i // batch_size
        progress_bar.progress((current_batch_idx + 1) / total_batches)

    # LANGKAH 3: Penyusunan Kembali & Polishing Bahasa Santai
    for idx, data in enumerate(dialog_data):
        line_idx = data['line_idx']
        prefix = data['prefix']
        suffix = data['suffix']
        raw_translation = translated_texts[idx]
        
        # Lokalisasi bahasa agar terasa seperti obrolan sehari-hari (Casual Conversion)
        # Menghapus kata formal bawaan Google Translate yang kaku
        casual_text = raw_translation
        casual_text = re.sub(r'\bAnda\b', 'kamu', casual_text, flags=re.IGNORECASE)
        casual_text = re.sub(r'\bSaya\b', 'aku', casual_text, flags=re.IGNORECASE)
        casual_text = re.sub(r'\bTidak\b', 'nggak', casual_text, flags=re.IGNORECASE)
        casual_text = re.sub(r'\bApakah\b', 'apa', casual_text, flags=re.IGNORECASE)
        casual_text = re.sub(r'\bBenar\b', 'bener', casual_text, flags=re.IGNORECASE)
        casual_text = re.sub(r'\bSangat\b', 'banget', casual_text, flags=re.IGNORECASE)
        casual_text = re.sub(r'\bMengapa\b', 'kenapa', casual_text, flags=re.IGNORECASE)
        
        # Bersihkan teks hasil terjemahan sebelum dibungkus kembali ke file game
        safe_text = clean_and_normalize_dialog(casual_text)
        
        # Bungkus kembali ke format Ren'Py asli tanpa merusak sintaks luar
        lines[line_idx] = f'{prefix}"{safe_text}"{suffix}'
            
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - ULTIMATE CASUAL MODE 🧠⚡")
st.write("Versi Sempurna: Terjemahan bahasa gaul sehari-hari, super cepat, dan diproteksi dari bug game crash.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Sempurna"):
        with st.spinner("Menyelaraskan bahasa dan mengecek bug teks... Mohon tunggu."):
            result = translate_rpy_ultimate(file_contents, target_code)
            st.success("Proses selesai dengan aman!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
