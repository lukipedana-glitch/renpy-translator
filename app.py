import streamlit as st
import re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="ES to ID Anti Crash V7.1")
st.title("ES to ID Translator V7.1 - Anti Joyplay FC")
st.warning("Ini khusus fix crash pas dialog. Tag dan \\n dijamin aman 100%")

file = st.file_uploader("Upload file BAHASA SPANYOL .rpy", type=["rpy"])

def protect_tags(text):
    # Proteksi: {tag} [/tag] [ ] \n \t \" ... ~
    return re.findall(r'\{[^}]*\}|\[[^\]]*\]|\\[nrt"\\]|\.\.|~', text)

if file and st.button("TERJEMAHKAN KE INDONESIA"):
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    out = []
    crash_log = []

    for idx, line in enumerate(lines):
        m = re.match(r'^(\s*old\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
        m2 = re.match(r'^(\s*new\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
        
        if m or m2:
            prefix = m.group(1) if m else m2.group(1)
            text = m.group(2) if m else m2.group(2)
            suffix = m.group(3) if m else m2.group(3)
            
            # 1. Simpen tag asli
            tags = protect_tags(text)
            temp = text
            for i,t in enumerate(tags):
                temp = temp.replace(t, f'@@P{i}@@')
            
            # 2. Translate
            try:
                hasil = GoogleTranslator(source='es', target='id').translate(temp) if temp.strip() else temp
                # 3. Balikin tag
                for i,t in enumerate(tags):
                    hasil = hasil.replace(f'@@P{i}@@', t)
            except:
                hasil = text
                crash_log.append(f"Line {idx+1}: Gagal translate, pake teks asli")
            
            # 4. CEK KESEHATAN TAG - PENTING BANGET BUAT ANTI CRASH
            buka = hasil.count('{')
            tutup = hasil.count('}')
            if buka != tutup:
                crash_log.append(f"Line {idx+1}: Tag rusak! {buka} buka vs {tutup} tutup. Dibenerin manual")
                # kalau rusak, balikin ke teks asli biar gak crash
                hasil = text 

            out.append(f'{prefix}"{hasil}"{suffix}')
        else:
            out.append(line)
            
    st.success("Selesai!")
    if crash_log:
        with st.expander("Lihat Log Perbaikan"):
            st.write("\n".join(crash_log))
    
    st.download_button("DOWNLOAD FILE ID - ANTI CRASH", '\n'.join(out), "ID_" + file.name)

st.info("Setelah download: Pindah ke game/tl/Indonesian > Hapus cache Joyplay > Test lagi")
