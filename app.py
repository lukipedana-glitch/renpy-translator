import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, TooManyRequests

st.set_page_config(page_title="RenPy to ID V8.3", layout="wide")
st.title("RenPy to ID Translator V8.3 ANTI CRASH")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

def protect(text):
    tags = re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrtw"\\]|\.\.|~|\bnone\b', text, flags=re.IGNORECASE)
    temp = text
    for i,t in enumerate(tags):
        temp = temp.replace(t, f'@@P{i}@@')
    return temp, tags

def unprotect(text, tags):
    text = str(text) # PAKSA JADI STRING
    for i,t in enumerate(tags):
        text = text.replace(f'@@P{i}@@', t)
    return text

def get_download_link(content, filename):
    b64 = base64.b64encode(content.encode('utf-8', errors='ignore')).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 KLIK UNTUK DOWNLOAD FILE ID</a>'

def safe_translate(texts, retries=3):
    for attempt in range(retries):
        try:
            res = GoogleTranslator(source='auto', target='id').translate_batch(texts)
            # PAKSA SEMUA HASIL JADI STRING
            return [str(r) if r else t for r, t in zip(res, texts)]
        except TooManyRequests:
            wait = (attempt + 1) * 15
            st.warning(f"Ke ban Google. Nunggu {wait} detik...")
            time.sleep(wait)
        except Exception as e:
            st.error(f"Error translate: {e}. Di skip")
    return texts # fallback

if file and st.button("🚀 TERJEMAHKAN KE INDONESIA", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    changes_per_line = {}
    batch_texts = []
    batch_tags = []

    with st.status("Step 1/4: Scan semua dialog...") as s1:
        for idx, line in enumerate(lines):
            for m in re.finditer(r'"((?:[^"\\]|\\.)*?)"', line):
                original_text = m.group(1)
                if original_text.strip() and original_text.strip().lower()!= "none":
                    clean_text, tags = protect(original_text)
                    if clean_text.strip():
                        batch_texts.append(clean_text)
                        batch_tags.append(tags)
                        if idx not in changes_per_line:
                            changes_per_line[idx] = []
                        changes_per_line[idx].append((m.start(1), m.end(1)))
        s1.update(label=f"Step 1/4 Selesai: Nemu {len(batch_texts)} teks", state="complete")

    results_all = []
    progress = st.progress(0, text="Step 2/4: Menerjemahkan...")
    
    for i in range(0, len(batch_texts), 50): # TURUNIN LAGI JADI 50 BIAR AMAN
        chunk = batch_texts[i:i+50]
        progress.progress(i / len(batch_texts), text=f"Step 2/4: {i}/{len(batch_texts)}")
        results = safe_translate(chunk)
        results_all.extend(results)
        time.sleep(3)

    with st.status("Step 3/4: Menulis hasil ke file...") as s3:
        result_idx = 0
        for idx in sorted(changes_per_line.keys()):
            line = lines[idx]
            changes = changes_per_line[idx]
            line_results = results_all[result_idx : result_idx + len(changes)]
            result_idx += len(changes)
            
            # GANTI DARI BELAKANG + TRY EXCEPT
            for (start, end), new_text, tags in sorted(zip(changes, line_results, batch_tags[result_idx-len(changes):result_idx]), reverse=True):
                try:
                    final_text = unprotect(new_text, tags)
                    line = line[:start+1] + final_text + line[end+1:]
                except Exception as e:
                    st.warning(f"Skip 1 teks di baris {idx+1} karena error: {e}")
                    continue
            lines[idx] = line
        s3.update(label="Step 3/4 Selesai", state="complete")

    final_content = '\n'.join(lines)
    st.success("✅ Step 4/4 Selesai!")
    st.markdown(get_download_link(final_content, "ID_V83_" + file.name), unsafe_allow_html=True)
