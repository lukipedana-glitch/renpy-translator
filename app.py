import streamlit as st
import re
from deep_translator import GoogleTranslator

st.title("🌏 Translator.rpy Anti FC V4 - Skip Error")
uploaded_file = st.file_uploader("Upload file.rpy", type=["rpy"])

if st.button("TRANSLATE"):
    content = uploaded_file.read().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    out = []
    error_count = 0
    
    for line in lines:
        m = re.match(r'^(\s*\w*\s*)"((?:[^"\\]|\\.)*)"(.*)$', line)
        if m:
            dialog = m.group(2)
            # SKIP kalau ada kutip dobel mentah " di tengah
            if dialog.count('"') > 0 and '\\"' not in dialog:
                out.append(f'{m.group(1)}"[SKIP: Kutip error]"{m.group(3)}')
                error_count += 1
            else:
                try:
                    hasil = GoogleTranslator(source='auto', target='id').translate(dialog)
                    out.append(f'{m.group(1)}"{hasil}"{m.group(3)}')
                except:
                    out.append(line)
        else:
            out.append(line)
    
    st.success(f"SELESAI. {error_count} line di-skip karena bahaya")
    st.download_button("Download Hasil", '\n'.join(out), "ID_"+uploaded_file.name)
