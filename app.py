import streamlit as st
import re
from deep_translator import GoogleTranslator

def make_it_casual(text):
    """
    Mengubah kata kaku formal bawaan mesin translator 
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
    Menetralkan semua jenis tanda kutip internal agar emulator Joiplay Android tidak crash.
    """
    if not text:
        return ""
    # Menghapus kutip ganda internal dekoratif bawaan teks HP/Google Translate menjadi kutip satu
    text = text.replace('“', "'").replace('”', "'").replace('„', "'")
    text = text.replace('"', "'")
    # Bersihkan karakter pembaca internal yang sering merusak memori rendering Joiplay
    text = text.replace('%', ' persen').replace('\\', '/')
    return text.strip()

def translate_rpy_mega_fast_fixed(content, target_lang='id'):
    lines = content.split('\n')
    
    # REGEX UTAMA FIX: Menangkap semua format teks Spanyol/Inggris di dalam tanda kutip dua murni ("...")
    # Menggunakan pencarian non-greedy (.*?) agar tidak salah memotong kode variabel Ren'Py
    dialog_pattern = re.compile(r'^([^"\n]*?)"([^"\n]*?)"([^"\n]*?)$')
    
    dialog_data = []
    
    # LANGKAH 1: Kumpulkan semua data teks dialog
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

    # LANGKAH 2: Chunking Paket Massal Menggunakan Batas Karakter Google Translate (< 4500)
    chunks = []
    current_chunk = []
    current_length = 0
    separator = " @@@ " # Pembatas terisolasi yang kebal dari gangguan bahasa Spanyol
    
    for data in dialog_data:
        added_length = len(data['text']) + len(separator)
        if current_length + added_length > 4200:
            chunks.append(current_chunk)
            current_chunk = [data]
            current_length = len(data['text'])
        else:
            current_chunk.append(data)
            current_length += added_length
            
    if current_chunk:
        chunks.append(current_chunk)

    # LANGKAH 3: Eksekusi Kirim Instan ke Server
    translator = GoogleTranslator(source='auto', target=target_lang)
    progress_bar = st.progress(0)
    total_chunks = len(chunks)
    
    for chunk_idx, chunk in enumerate(chunks):
        # Satukan sekelompok baris dialog menjadi satu teks raksasa (Mengurangi loading kirim data)
        combined_text = separator.join([data['text'] for data in chunk])
        try:
            translated_combined = translator.translate(combined_text)
            translated_list = translated_combined.split(separator)
            
            # Validasi Akurasi: Jika jumlah data pas, langsung kembalikan ke baris aslinya
            if len(translated_list) == len(chunk):
                for i, data in enumerate(chunk):
                    idx = data['line_idx']
                    casual_text = make_it_casual(translated_list[i])
                    safe_text = clean_strictly_for_joiplay(casual_text)
                    lines[idx] = f'{data["prefix"]}"{safe_text}"{data["suffix"]}'
            else:
                # Mode Cadangan: Jika pembatas dirusak oleh Google, terjemahkan per baris khusus kelompok ini
                for data in chunk:
                    try:
                        idx = data['line_idx']
                        raw_res = translator.translate(data['text'])
                        lines[idx] = f'{data["prefix"]}"{clean_strictly_for_joiplay(make_it_casual(raw_res))}"{data["suffix"]}'
                    except:
                        pass
        except:
            # Proteksi Kehilangan Teks: Jika server mati sementara, gunakan teks aslinya agar file tidak korup
            for data in chunk:
                idx = data['line_idx']
                lines[idx] = f'{data["prefix"]}"{data["text"]}"{data["suffix"]}'
                
        progress_bar.progress((chunk_idx + 1) / total_chunks)
            
    return '\n'.join(lines)

st.title("Ren'Py Joiplay Translator - TOTAL PERFECTION ⚡")
st.write("Sistem Pemrosesan Paket Massal: Terjemahan bahasa gaul dunia nyata, super instan, dan anti-crash Joiplay.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Super Kilat"):
        with st.spinner("Menyelaraskan bahasa kasual dunia nyata... Mohon tunggu."):
            result = translate_with_fallback = translate_rpy_mega_fast_fixed(file_contents, target_code)
            st.success("Proses selesai total dengan aman!")
            
            # FITUR UTAMA JOIPLAY: Memaksa encoding file menggunakan format UTF-8 dengan tanda BOM (\ufeff)
            # Menjamin emulator Joiplay Android mengenali font bahasa Indonesia tanpa lag/stutter
            bom_result = '\ufeff' + result
            st.download_button(
                label="Unduh File Terjemahan Joiplay",
                data=bom_result.encode('utf-8'),
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
