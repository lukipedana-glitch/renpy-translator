import streamlit as st
import re
from deep_translator import GoogleTranslator

def translate_text_safely(text, translator):
    """
    Fungsi untuk menerjemahkan teks sambil mengamankan tag internal Ren'Py seperti [variable] atau {w}
    """
    if not text.strip():
        return text
        
    # Proteksi tag Ren'Py agar tidak rusak (contoh: [name] atau {w})
    placeholders = {}
    
    def replacer(match):
        placeholder = f" _TAG_{len(placeholders)}_ "
        placeholders[placeholder.strip()] = match.group(0)
        return placeholder

    # Cari semua pola [teks] dan {teks} untuk diamankan
    protected_text = re.sub(r'(\[[^\]]+\]|\{[^\}]+\})', replacer, text)
    
    try:
        translated = translator.translate(protected_text)
        
        # Kembalikan tag asli ke tempatnya semula
        for placeholder, original_tag in placeholders.items():
            translated = re.sub(re.escape(placeholder), original_tag, translated, flags=re.IGNORECASE)
            # Cadangan jika translator merubah spasi tag
            translated = re.sub(re.escape(placeholder.strip()), original_tag, translated, flags=re.IGNORECASE)
            
        return translated
    except:
        return text

def translate_rpy_perfect(content, target_lang='id'):
    lines = content.split('\n')
    translator = GoogleTranslator(source='auto', target=target_lang)
    
    # Regex super yang bisa mendeteksi dialog dengan karakter, kutip satu, kutip dua, maupun kutip tiga
    # Format: karakter "dialog" ATAU "dialog saja"
    dialog_pattern = re.compile(r'^(\s*(?:\w+\s+)?)("""|\'\'\'|"|\')(.+?)\2\s*$')
    
    progress_bar = st.progress(0)
    total_lines = len(lines)
    
    for idx, line in enumerate(lines):
        match = dialog_pattern.match(line)
        if match:
            prefix = match.group(1)       # Nama karakter atau spasi di depan
            quote_type = match.group(2)   # Jenis tanda kutip yang dipakai (" atau ' atau """)
            text_to_translate = match.group(3) # Isi teks aslinya
            
            # Terjemahkan teks secara aman
            translated_text = translate_text_safely(text_to_translate, translator)
            
            # Susun kembali sesuai format aslinya tanpa merusak tanda kutip game
            lines[idx] = f'{prefix}{quote_type}{translated_text}{quote_type}'
            
        # Update status progress bar di HP
        if idx % 10 == 0 or idx == total_lines - 1:
            progress_bar.progress((idx + 1) / total_lines)
            
    return '\n'.join(lines)

st.title("Ren'Py (.rpy) Translator - PERFECT MODE 🛠️")
st.write("Versi pembaruan otomatis untuk membaca semua jenis format dialog dan mengamankan kode game.")

lang_options = {'Indonesia': 'id', 'Inggris': 'en', 'Jepang': 'ja', 'Spanyol': 'es'}
selected_lang = st.selectbox("Pilih Bahasa Target:", list(lang_options.keys()))
target_code = lang_options[selected_lang]

uploaded_file = st.file_uploader("Pilih file .rpy", type=["rpy"])

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    if st.button("Mulai Terjemahkan Semua Dialog"):
        with st.spinner("Sedang memproses seluruh baris dialog... Mohon tunggu."):
            result = translate_rpy_perfect(file_contents, target_code)
            st.success("Penerjemahan selesai total!")
            st.download_button(
                label="Unduh File Terjemahan",
                data=result,
                file_name=f"translated_{uploaded_file.name}",
                mime="text/plain"
            )
