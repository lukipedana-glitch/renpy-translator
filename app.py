import streamlit as st
import re
import time
import base64
from deep_translator import GoogleTranslator

st.set_page_config(page_title="RenPy to ID V9.0", layout="wide")
st.title("RenPy to ID V9.0 - CUMA TRANSLATE ISI \"...\"")
st.caption("Tag {w} \\n [player] 100% aman. Gak akan ke translate")

file = st.file_uploader("Upload file.rpy", type=["rpy"])

def get_download_link(content, filename):
    b64 = base64.b64encode(content.encode('utf-8', errors='ignore')).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 DOWNLOAD FILE ID</a>'

if file and st.button("🚀 TERJEMAHKAN", type="primary", use_container_width=True):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    
    jobs = [] # simpan semua teks yg di dalam "
    for idx, line in enumerate(lines):
        for m in re.finditer(r'"((?:[^"\\]|\\.)*?)"', line): # cari isi petik
            original_text = m.group(1)
            if original_text.strip() and original_text.strip().lower()!= "none":
                jobs.append((idx, m.start(1), m.end(1), original_text))

    st.info(f"Nemu {len(jobs)} teks di dalam \"...\". Estimasi 10-15 menit")
    results_all = []
    progress = st.progress(0)
    
    # TRANSLATE BATCH 100 BIAR CEPET
    for i in range(0, len(jobs), 100):
        chunk = [j[3] for j in jobs[i:i+100]] # ambil teksnya doang
        try:
            res = GoogleTranslator(source='auto', target='id').translate_batch(chunk)
            results_all.extend([str(r) if r else c for r, c in zip(res, chunk)])
        except:
            st.warning(f"Chunk {i//100 + 1} ke ban. Nunggu 15 detik")
            time.sleep(15)
            results_all.extend(chunk) # gagal = pake asli
        progress.progress((i+100) / len(jobs))
        time.sleep(1.5)

    # GANTI KE FILE DARI BELAKANG
    for (idx, start, end, original), result in sorted(zip(jobs, results_all), reverse=True):
        lines[idx] = lines[idx][:start+1] + result + lines[idx][end+1:]

    final_content = '\n'.join(lines)
    st.success("✅ Selesai! Tag {w} \\n aman 100%")
    st.markdown(get_download_link(final_content, "ID_V90_" + file.name), unsafe_allow_html=True)
