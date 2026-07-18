import streamlit as st
import re
from google_translator import GoogleTranslator

def make_it_casual(text):
    """
    Mengubah kata kaku formal bawaan Google Translate menjadi bahasa gaul sehari-hari di dunia nyata
    """
    if not text or not isinstance(text, str):
        return text
        
    # Daftar kamus konversi kata formal ke bahasa santai
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
        r'\bDatang\b': 'datang',
        r'\bKembali\b': 'balik',
        r'\bUang\b': 'duit',
        r'\bTeman\b': 'temen',
    }
    
    # Proses penggantian kata gaul otomatis
    for formal, casual in casual_dictionary.items():
        text = re.sub(formal, casual, text, flags=re.IGNORECASE)
        
    return text

def clean_for_renpy(text):
    """
    Mengamankan tanda kutip di dalam kalimat agar mesin game Ren'Py tidak crash/keluar sendiri
    """
    if not text:
        return ""
    # Ubah kutip miring HP menjadi kutip lurus, amankan kutip dua di dalam kalimat dengan backslash (\")
    text = text.replace('“', '\\"').replace('”', '\\"').replace('"', '\\"')
    text = re.sub(r'(?<!\\)\\"', '\\"', text)
    return text

def translate_rpy_speedrun(content, target_lang='id'):
    lines = content.split('\n')
    
    # Regex super akurat: Hanya ambil teks murni di dalam tanda kutip dua pertama dan terakhir
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]*)"([^"\n]*)$')
    
    dialog_data = []
    
    # LANGKAH 1: Kumpulkan semua data dialog
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip(): # Lewati jika kutip kosong
                dialog_data.append({
                    'line_idx': idx,
                    'text': text_inside,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not dialog_data:
        return content

    # LANGKAH 2: Terjemahkan Massal (Batch) Secara Kilat Menggunakan Engine Baru
    batch_size = 80
    translator = GoogleTranslator()
    
    all_texts = [data['text'] for data in dialog_data]
    translated_texts = []
    
    progress_bar = st.progress(0)
    total_batches = (len(all_texts) + batch_size - 1) // batch_size

    for i in range(0, len(all_texts), batch_size):
        batch = all_texts[i:i + batch_size]
        try:
            # Gunakan bulk translation bawaan yang super cepat
            translated_batch = [translator.translate(t, lang_tgt=target_lang) for t in batch]
            translated_texts.extend(translated_batch)
        except Exception as e:
            # Proteksi jika gagal, kembalikan teks asli agar proses tetap jalan terus tanpa berhenti
            translated_texts.extend(batch)
            
        current_batch_idx = i // batch_size
        progress_bar.progress((current_batch_idx + 1) / total_batches)

    # LANGKAH 3: Tulis kembali hasil ke file .rpy dengan optimasi bahasa kasual
    for idx, data in enumerate(dialog_data):
        line_idx = data['line_idx']
        prefix = data['prefix']
        suffix = data['suffix']
        
        # Ambil hasil terjemahan (pastikan berupa string)
        raw_text = translated_texts[idx]
        if not isinstance(raw_text, str):
            raw_text = str(raw_text) if raw_text is not None else data['text']
            
        # Ubah ke bahasa gaul santai dunia nyata
        casual_text = make_it_casual(raw_text)
        
        # Bersihkan kutip dua liar agar game tidak force close
        safe_text = clean_for_renpy(casual_text)
        
        # Kembalikan ke dalam tanda kutip dua murni, luar tanda kutip dijamin tidak berubah
        lines[line_idx] = f'{prefix}"{safe_text}"{suffix}'
            
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - SPEEDRUN & CASUAL MODE ⚡")
st.write("Hanya menerjemahkan isi tanda kutip dua. Cepat, otomatis bahasa santai, dan anti-crash.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Kilat"):
        with st.spinner("Sedang memproses seluruh percakapan game... Mohon tunggu."):
            result = translate_rpy_speedrun(file_contents, target_code)
            st.success("Selesai! File Anda siap diunduh.")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
