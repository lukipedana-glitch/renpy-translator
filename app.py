import streamlit as st
import re, time
from deep_translator import GoogleTranslator

st.set_page_config(page_title="RenPy Translator Anti FC", layout="centered")
st.title("🌏 Translator.rpy Anti FC V2")

uploaded_file = st.file_uploader("Upload file.rpy", type=["rpy"])
tombol = st.button("TRANSLATE PAKAI GOOGLE")

def protect_tags(text):
    tags = re.findall(r'\{.*?\}|\[.*?\]|\\|~', text) # protect {tag} [tag] \ ~
    for i, tag in enumerate(tags): 
        text = text.replace(tag, f'@@TAG{i}@@')
    return text, tags

def unprotect_tags(text, tags):
    for i, tag in enumerate(tags): 
        text = text.replace(f'@@TAG{i}@@', tag)
    return text

if tombol and uploaded_file:
    st.info("Mulai translate...")
    content = uploaded_file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    out = []
    bar = st.progress(0)
    
    for i, line in enumerate(lines):
        m = re.match(r'^(\s*\w*\s*)"([^"]*)"(.*)$', line)
        if m and m.group(2).strip():
            text_asli, tags = protect_tags(m.group(2)) # 1. Amankan tag dulu
            try:
                hasil = GoogleTranslator(source='auto', target='id').translate(text_asli) # 2. Translate
                hasil = unprotect_tags(hasil, tags) # 3. Kembalikan tag
                out.append(f'{m.group(1)}"{hasil}"{m.group(3)}')
            except:
                out.append(line)
                time.sleep(1)
        else:
            out.append(line)
        bar.progress((i+1)/len(lines))
    
    st.success("SELESAI")
    st.download_button("Download Hasil", '\n'.join(out), "ID_"+uploaded_file.name)
