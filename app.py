import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator

st.set_page_config(page_title="RenPy to ID V8.6", layout="wide")
st.title("RenPy to ID Translator V8.6 - SATU2 ANTI NGACO")
st.warning("INI LAMBAT TAPI 100% AMAN. 3451 teks = sekitar 3 jam")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

def split_text_and_tags(text):
    parts = re.split(r'(\{[^}]*\}|\[[^\]]*\]|\\[nrtw"\\]|\.\.|~|\bnone\b)', text, flags=re.IGNORECASE)
    texts_to_translate = [p for p in parts if p and not re.match(r'\{[^}]*\}|\[[^\]]*\]|\\[nrtw"\\]|\.\.|~|\bnone\b', p, flags=re.IGNORECASE)]
    return parts, texts_to_translate

def join_text_and_tags(parts, translated_texts):
    result = []
    t_idx = 0
    for p in parts:
        if re.match(r'\{[^}]*\}|\[[^\]]*\]|\\[nrtw"\\]|\.\.|~|\bnone\b', p, flags=re.IGNORECASE):
            result.append(p)
        else:
            result.append(translated_texts[t_idx])
            t_idx += 1
    return "".join(result)

def get_download_link(content, filename):
    b64 = base64.b64encode(content.encode('utf-8', errors='ignore')).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 KLIK UNTUK DOWNLOAD FILE ID</a>'

if file and st.button("🚀 TERJEMAHKAN SATU2", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    
    jobs = [] # [(idx, start, end, parts)]

    with st.status("Step 1/3: Scan semua dialog...") as s1:
        for idx, line in enumerate(lines):
            for m in re.finditer(r'"((?:[^"\\]|\\.)*?)"', line):
                original_text = m.group(1)
                if original_text.strip() and original_text.strip().lower()!= "none":
                    parts, texts = split_text_and_tags(original_text)
                    if texts:
                        jobs.append((idx, m.start(1), m.end(1), parts, texts))
        s1.update(label=f"Step 1/3 Selesai: Nemu {len(jobs)} dialog", state="complete")

    # TRANSLATE SATU2
    progress = st.progress(0, text="Step 2/3: Menerjemahkan satu2...")
    
    for i, (idx, start, end, parts, texts) in enumerate(jobs):
        translated_texts = []
        for t in texts:
            try:
                # TRANSLATE SATU KALIMAT
                res = GoogleTranslator(source='en', target='id').translate(t)
                translated_texts.append(str(res) if res else t)
            except:
                translated_texts.append(t) # kalau gagal, pake asli
                time.sleep(10) # kalau ke ban nunggu lama
            time.sleep(0.5) # jeda 0.5 detik biar gak ke ban
        
        final_text = join_text_and_tags(parts, translated_texts)
        lines[idx] = lines[idx][:start+1] + final_text + lines[idx][end+1:]
        
        progress.progress((i+1) / len(jobs), text=f"Step 2/3: {i+1}/{len(jobs)}")

    final_content = '\n'.join(lines)
    st.success("✅ Step 3/3 Selesai!")
    st.markdown(get_download_link(final_content, "ID_V86_" + file.name), unsafe_allow_html=True)
