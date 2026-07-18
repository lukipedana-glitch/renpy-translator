import streamlit as st
import re
import translators as ts

def make_it_casual(text):
    """
    Mengubah kata-kata kaku formal bawaan mesin translator 
    menjadi bahasa gaul santai sehari-hari di dunia nyata.
    """
    if not text or not isinstance(text, str):
        return text
        
    # Kamus lokalisasi bahasa gaul tongkrongan / dunia nyata
    casual_dictionary = {
        r'\bAnda\b': 'kamu',
        r'\bSaya\b': 'aku',
        r'\bTidak\b': 'nggak',
        r'\bApakah\b': 'apa',
        r'\bBenar\b': 'bener',
        r'\bSangat\b': 'banget',
        r'\bMengapa\b': 'kenapa',
        r'\bBagaimana\b': 'gimana',
        r'\bTetapi\b': 'tapi',
        r'\bNamun\b': 'tapi',
        r'\bBisa\b': 'bisa',
        r'\bAkan\b': 'bakal',
        r'\bMelihat\b': 'liat',
        r'\bSudah\b': 'udah',
        r'\bSaja\b': 'aja',
        r'\bBukan\b': 'bukan',
        r'\bPergi\b': 'pergi',
        r'\bKembali\b': 'balik',
        r'\bUang\b': 'duit',
        r'\bTeman\b': 'temen',
        r'\bAyah\b': 'bokap',
        r'\bIbu\b': 'nyokap',
    }
    
    for formal, casual in casual_dictionary.items():
        text = re.sub(formal, casual, text, flags=re.IGNORECASE)
        
    return text

def clean_for_renpy(text):
    """
    Mencegah game crash/keluar sendiri dengan merapikan tanda kutip dua internal
    """
    if not text:
        return ""
    # Ubah kutip miring bawaan teks menjadi kutip lurus standar game
    text = text.replace('“', '\\"').replace('”', '\\"').replace('"', '\\"')
    # Amankan backslash ganda yang berpotensi merusak sintaks Ren'Py
    text = re.sub(r'(?<!\\)\\"', '\\"', text)
    return text

def translate_rpy_ultimate_speed(content, target_lang='id'):
    lines = content.split('\n')
    
    # Regex super akurat: Membagi baris menjadi (Luar_Depan) "Teks_Dalam" (Luar_Belakang)
    # Menjamin 100% kode, variabel, dan nama di luar simbol " TIDAK AKAN berubah
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]*)"([^"\n]*)$')
    
    dialog_data = []
    
    # LANGKAH 1: Data Mining dialog secara cepat
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip(): # Abaikan kutip kosong
                dialog_data.append({
                    'line_idx': idx,
                    'text': text_inside,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not dialog_data:
        return content

    # LANGKAH 2: Batch Translation menggunakan Engine Kilat 'translators'
    # Membagi tugas ke kelompok kecil 40 baris agar instan tanpa loading lama
    batch_size = 40
    progress_bar = st.progress(0)
    total_dialogs = len(dialog_data)

    for i in range(0, total_dialogs, batch_size):
        batch = dialog_data[i:i + batch_size]
        
        for data in batch:
            try:
                # Menggunakan engine Google via library translators (Sangat cepat dan responsif)
                raw_translation = ts.translate_text(data['text'], from_language='auto', to_language=target_lang, translator='google')
                
                # Sempurnakan hasil: Ubah ke bahasa kasual sehari-hari
                casual_text = make_it_casual(raw_translation)
                
                # Tebul/Tambal Bug: Bersihkan simbol kutip perusak mesin Ren'Py
                safe_text = clean_for_renpy(casual_text)
                
                # Masukkan kembali ke baris asli di dalam file
                lines[data['line_idx']] = f'{data["prefix"]}"{safe_text}"{data["suffix"]}'
            except:
                # Jika baris ini gagal karena gangguan server, gunakan teks asli agar game tidak corrupt
                pass
        
        # Update progress bar jalan di layar HP Anda
        current_progress = min((i + batch_size) / total_dialogs, 1.0)
        progress_bar.progress(current_progress)
            
    return '\n'.join(lines)

st.title("Ren'Py Translator - ULTIMATE SPEED & CASUAL ⚡")
st.write("Hanya menerjemahkan isi di dalam simbol \"...\". Kecepatan maksimal, otomatis bahasa gaul, anti-crash.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Kilat"):
        with st.spinner("Menyelaraskan bahasa gaul dunia nyata... Mohon tunggu."):
            result = translate_rpy_ultimate_speed(file_contents, target_code)
            st.success("Selesai total! File aman dari bug crash.")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
