import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, TooManyRequests

st.set_page_config(page_title="RenPy to ID V8.2 Final", layout="wide")
st.title("RenPy to ID Translator V8.2 FINAL FIX")

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
    b64 = base64.b64encode(content.encode('utf-8', errors='ignore')).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 KLIK UNTUK DOWNLOAD FILE ID</a>'

def safe_translate(texts, retries=3):
    for attempt in range(retries):
        try:
            return GoogleTranslator(source='auto', target='id').translate_batch(texts)
        except TooManyRequests:
            wait = (attempt + 1) * 15
            st.warning(f"Ke ban Google. Nunggu {wait} detik...")
            time.sleep(wait)
        except: pass
    return texts

if file and st.button("🚀 TERJEMAHKAN KE INDONESIA", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    
    # KUNCI: SIMPAN PERUBAHAN PER BARIS DULU
    changes_per_line = {} # {idx: [(start, end, new_text),...]}
    batch = []

    with st.status("Step 1/4: Scan semua dialog...") as s1:
        for idx, line in enumerate(lines):
            matches = list(re.finditer(r'"((?:[^"\\]|\\.)*?)"', line))
            for m in matches:
                original_text = m.group(1)
                if original_text.strip() and original_text.strip().lower()!= "none":
                    clean_text, tags = protect(original_text)
                    if clean_text.strip():
                        batch.append((clean_text, tags))
                        if idx not in changes_per_line:
                            changes_per_line[idx] = []
                        changes_per_line[idx].append((m.start(1), m.end(1)))
        s1.update(label=f"Step 1/4 Selesai: Nemu {len(batch)} teks", state="complete")

    # TRANSLATE
    texts_only = [b[0] for b in batch]
    results_all = []
    progress = st.progress(0, text="Step 2/4: Menerjemahkan...")
    
    for i in range(0, len(texts_only), 80):
        chunk = texts_only[i:i+80]
        progress.progress(i / len(texts_only), text=f"Step 2/4: {i}/{len(texts_only)}")
        results = safe_translate(chunk)
        results_all.extend(results)
        time.sleep(2.5)

    # GABUNGKAN HASIL + TAGS
    final_results = []
    for (res, tags) in zip(results_all, [b[1] for b in batch]):
        final_results.append(unprotect(res, tags))

    # STEP 3: GANTI DARI BELAKANG BIAR GAK GESER
    with st.status("Step 3/4: Menulis hasil ke file...") as s3:
        result_idx = 0
        for idx in sorted(changes_per_line.keys()): # urut
            line = lines[idx]
            # Ambil semua perubahan di baris ini, urut dari belakang
            changes = changes_per_line[idx]
            # Ambil hasil translate yg sesuai
            line_results = final_results[result_idx : result_idx + len(changes)]
            result_idx += len(changes)
            
            # Ganti dari belakang
            for (start, end), new_text in sorted(zip(changes, line_results), reverse=True):
                line = line[:start+1] + new_text + line[end+1:]
            lines[idx] = line
        s3.update(label="Step 3/4 Selesai", state="complete")

    final_content = '\n'.join(lines)
    st.success("✅ Step 4/4 Selesai!")
    st.markdown(get_download_link(final_content, "ID_V82_" + file.name), unsafe_allow_html=True)
