import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, TooManyRequests

st.set_page_config(page_title="RenPy to ID V8.1 Anti Bug", layout="wide")
st.title("RenPy to ID Translator V8.1 ANTI BUG")
st.caption("Support Emoji, Jepang, Escape, Multi Dialog. Auto retry kalau ke ban.")

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
    b64 = base64.b64encode(content.encode('utf-8', errors='ignore')).decode() # FIX UNICODE
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 KLIK UNTUK DOWNLOAD FILE ID</a>'

def safe_translate(texts, retries=3):
    for attempt in range(retries):
        try:
            return GoogleTranslator(source='auto', target='id').translate_batch(texts)
        except TooManyRequests:
            wait = (attempt + 1) * 15
            st.warning(f"Ke ban Google. Nunggu {wait} detik... Coba {attempt+1}/{retries}")
            time.sleep(wait)
        except NotValidPayload:
            st.error("Ada teks terlalu panjang. Di skip 1 chunk")
            return texts # fallback
    return texts # kalau gagal semua

if file and st.button("🚀 TERJEMAHKAN KE INDONESIA", type="primary", use_container_width=True):
    with st.spinner("Membaca file..."):
        content = file.read().decode('utf-8', errors='ignore') # FIX UNICODE
    lines = content.split('\n')
    
    batch = []
    batch_index = []

    with st.status("Step 1/4: Scan semua dialog...") as s1:
        for idx, line in enumerate(lines):
            # FIX REGEX: WAJIB ADA " TUTUP
            for m in re.finditer(r'"((?:[^"\\]|\\.)*?)"', line): 
                original_text = m.group(1)
                if original_text.strip() and original_text.strip().lower()!= "none":
                    clean_text, tags = protect(original_text)
                    if clean_text.strip():
                        batch.append(clean_text)
                        batch_index.append((idx, m.start(1), m.end(1), tags))
        s1.update(label=f"Step 1/4 Selesai: Nemu {len(batch)} teks", state="complete")

    if not batch:
        st.warning("Tidak ada teks untuk diterjemahkan")
        st.stop()

    results_all = []
    progress = st.progress(0, text="Step 2/4: Menerjemahkan...")
    total_chunks = (len(batch) - 1) // 80 + 1 # TURUNIN JADI 80 BIAR AMAN
    
    for i in range(0, len(batch), 80):
        chunk = batch[i:i+80]
        chunk_num = i // 80 + 1
        progress.progress(i / len(batch), text=f"Step 2/4: Chunk {chunk_num}/{total_chunks}")
        
        results = safe_translate(chunk) # PAKE AUTO RETRY
        results_all.extend(results)
        
        time.sleep(2.5) # JEDA LEBIH LAMA ANTI BAN

    progress.progress(1.0, text="Step 2/4 Selesai")

    with st.status("Step 3/4: Menulis hasil ke file...") as s3:
        lines_dict = {i: line for i, line in enumerate(lines)}
        for (idx, start, end, tags), result in zip(batch_index, results_all):
            final_text = unprotect(result, tags)
            line = lines_dict[idx]
            # FIX: CEK APAKAH INDEX MASIH VALID
            if start < len(line) and end <= len(line):
                lines_dict[idx] = line[:start+1] + final_text + line[end+1:]
        
        for idx, new_line in lines_dict.items():
            lines[idx] = new_line
        s3.update(label="Step 3/4 Selesai", state="complete")

    final_content = '\n'.join(lines)
    st.success("✅ Step 4/4 Selesai! File siap di download")
    st.markdown(get_download_link(final_content, "ID_V81_" + file.name), unsafe_allow_html=True)
    st.balloons()
