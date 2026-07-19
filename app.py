import streamlit as st
import re, time

st.set_page_config(page_title="RenPy Translator", layout="centered")
st.title("🌏 Translator.rpy Versi Gampang")

uploaded_file = st.file_uploader("Upload file.rpy", type=["rpy"])
gemini_key = st.text_input("Tempel API Key Gemini di sini", type="password")
tombol = st.button("TRANSLATE PAKAI GEMINI")

def translate_google(text): # pake google dulu biar pasti jalan
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source='auto', target='id').translate(text)

if tombol:
    if not uploaded_file: 
        st.error("Upload file dulu")
    elif not gemini_key:
        st.error("Isi API Key dulu")
    else:
        st.info("Mulai translate... ini bisa 5-10 menit")
        content = uploaded_file.read().decode('utf-8', errors='ignore')
        lines = content.split('\n')
        out = []
        bar = st.progress(0)
        
        for i, line in enumerate(lines):
            m = re.match(r'^(\s*\w*\s*)"([^"]*)"(.*)$', line)
            if m and m.group(2).strip():
                try:
                    hasil = translate_google(m.group(2)) # kita tes pake google dulu
                    out.append(f'{m.group(1)}"{hasil}"{m.group(3)}')
                except:
                    out.append(line)
                    time.sleep(1)
            else:
                out.append(line)
            bar.progress((i+1)/len(lines))
        
        st.success("SELESAI")
        st.download_button("Download Hasil", '\n'.join(out), "ID_"+uploaded_file.name)
