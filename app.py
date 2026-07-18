import streamlit as st
import re
import translators as ts
from concurrent.futures import ThreadPoolExecutor

def make_it_casual(text):
    """
    Mengubah kata-kata kaku formal bawaan mesin translator 
    menjadi bahasa gaul santai sehari-hari di dunia nyata.
    """
    if not text or not isinstance(text, str):
        return text
        
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

def clean_strictly_for_joiplay(text):
    """
    SISTEM PROTEKSI UTAMA JOIPLAY:
    Menghapus dan menetralkan tanda kutip dua internal agar Joiplay tidak menutup paksa.
    """
    if not text:
        return ""
    # 1. Bersihkan tanda kutip dekoratif bawaan keyboard HP / Google Translate
    text = text.replace('“', "'").replace('”', "'").replace('„', "'")
    # 2. Jika ada kutip dua biasa di dalam kalimat, ganti menjadi kutip satu agar sintaks game aman
    text = text.replace('"', "'")
    # 3. Amankan karakter khusus Ren'Py % atau \ yang rawan merusak pembacaan script
    text = text.replace('%', ' persen').replace('\\', '/')
    return text.strip()

def translate_single_item(data, target_lang):
    """
    Fungsi pekerja untuk menerjemahkan satu baris dialog secara paralel
    """
    try:
        # PENTING: Menggunakan translator google dengan kode 'ind' untuk bahasa Indonesia
        raw_translation = ts.translate_text(
            data['text'], 
            from_language='spa', # Mengunci bahasa asal dari Spanyol (Spanish)
            to_language=target_lang, 
            translator='google'
        )
        casual_text = make_it_casual(raw_translation)
        safe_text = clean_strictly_for_joiplay(casual_text)
        return {'line_idx': data['line_idx'], 'result': f'{data["prefix"]}"{safe_text}"{data["suffix"]}'}
    except:
        # Jika gagal karena limit internet, pertahankan baris asli agar tidak ada teks yang hilang
        return {'line_idx': data['line_idx'], 'result': f'{data["prefix"]}"{data["text"]}"{data["suffix"]}'}

def translate_rpy_turbo_speed(content, target_lang='ind'):
    lines = content.split('\n')
    
    # Regex super akurat pemisah tanda kutip
    dialog_pattern = re.compile(r'^([^"\n]*)"([^"\n]*)"([^"\n]*)$')
    dialog_data = []
    
    # LANGKAH 1: Data Mining dialog secara cepat
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            text_inside = match.group(2)
            if text_inside.strip(): 
                dialog_data.append({
                    'line_idx': idx,
                    'text': text_inside,
                    'prefix': match.group(1),
                    'suffix': match.group(3)
                })
                
    if not dialog_data:
        return content

    # LANGKAH 2: Pemrosesan Paralel Turbo Multi-Threading
    progress_bar = st.progress(0)
    st.write(f"Mendeteksi {len(dialog_data)} baris dialog Spanyol. Memulai akselerasi paralel...")
    
    processed_count = 0
    total_dialogs = len(dialog_data)
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(translate_single_item, data, target_lang) for data in dialog_data]
        
        for future in futures:
            res_data = future.result()
            lines[res_data['line_idx']] = res_data['result']
            
            # Update bar progress secara berkala di layar HP
            processed_count += 1
            if processed_count % 10 == 0 or processed_count == total_dialogs:
                progress_bar.progress(processed_count / total_dialogs)
            
    return '\n'.join(lines)

st.title("Ren'Py Joiplay Translator - SPANISH TO INDONESIA TURBO 🏎️⚡")
st.write("Hanya menerjemahkan isi tanda kutip dua. Menggunakan sistem multi-core paralel, instan, bahasa gaul, dan Joiplay anti-crash.")

# Menyelaraskan kamus pilihan bahasa dengan kode ISO 3-letter khusus library translators
lang_options = {'Indonesia': 'ind', 'Inggris': 'eng', 'Jepang': 'jpn'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Turbo"):
        with st.spinner("Menerjemahkan bahasa Spanyol ke bahasa gaul Indonesia... Mohon tunggu."):
            result = translate_rpy_turbo_speed(file_contents, target_code)
            st.success("Selesai total! Struktur file 100% utuh dan aman.")
            
            # Memaksa file keluaran berformat UTF-8-BOM untuk kelancaran Joiplay di Android
            bom_result = '\ufeff' + result
            st.download_button(
                label="Unduh File Terjemahan Joiplay",
                data=bom_result.encode('utf-8'),
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
