import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Universal to ID V7.9")
st.title("Universal to ID V7.9 - Anti Crash Multi Dialog")
st.error("HANYA TEKS DALAM \"...\" YANG DITERJEMAHKAN.")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

def protect(text):
    tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrtw"\\]|\.\.|~|\bnone\b', text, flags=re.IGNORECASE)
    temp = text
    for i,t in enumerate(tags):
        temp = temp.replace(t, f'@@P{i}@@')
    return temp, tags

def unprotect(text, tags):
    for i,t in enumerate(tags):
        text = text.replace(f'@@P{i}@@', t)
    return text

def get_download_link(content, filename):
    b64 = base64.b64encode(content.encode('utf-8')).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">KLIK UNTUK DOWNLOAD FILE ID</a>'

if file and st.button("TERJEMAHKAN KE INDONESIA", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    batch = []
    batch_index = []

    with st.status("1. Scan & Kumpulin semua \"...\"...") as s:
        for idx, line in enumerate(lines):
            matches = list(re.finditer(r'"((?:[^"\\]|\\.)*)"', line)) # DIJADIIN LIST DULU
            for m in matches:
                original_text = m.group(1)
                if original_text.strip() and original_text.strip().lower()!= "none":
                    clean_text, tags = protect(original_text)
                    batch.append(clean_text)
                    # SIMPAN SEMUA DATA PER BARIS
                    batch_index.append((idx, m.start(1), m.end(1), tags))
        s.update(label=f"2. Nemu {len(batch)} teks", state="running")

    # TRANSLATE
    results_all = []
    progress = st.progress(0)
    for i in range(0, len(batch), 100):
        chunk = batch[i:i+100]
        try:
            results = GoogleTranslator(source='auto', target='id').translate_batch(chunk)
        except:
            results = chunk
            time.sleep(5)
        results_all.extend(results)
        progress.progress((i + 100) / len(batch))
        time.sleep(1.5)

    # KUNCI: GANTI DARI BELAKANG BIAR INDEX GAK GESER
    s.update(label="3. Masukin hasil ke file...", state="running")
    lines_dict = {}
    for (idx, start, end, tags), result in zip(batch_index, results_all):
        if idx not in lines_dict:
            lines_dict[idx] = lines[idx]
        
        final_text = unprotect(result, tags)
        line = lines_dict[idx]
        lines_dict[idx] = line[:start+1] + final_text + line[end+1:]
    
    # TIMPA KE LINES UTAMA
    for idx, new_line in lines_dict.items():
        lines[idx] = new_line

    final_content = '\n'.join(lines)
    s.update(label="Selesai!", state="complete")
    st.success(f"Selesai! {len(batch)} teks diterjemahkan")
    st.markdown(get_download_link(final_content, "ID_V79_" + file.name), unsafe_allow_html=True)
