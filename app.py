from deep_translator import GoogleTranslator
import re, time
from google.colab import files

def protect_and_clean(text):
    tags = re.findall(r'\{.*?\}', text)
    for i, tag in enumerate(tags): text = text.replace(tag, f'@@TAG{i}@@')
    text = text.replace('"', "'").replace('%', ' persen').replace('\\', '/')
    for i, tag in enumerate(tags): text = text.replace(f'@@TAG{i}@@', tag)
    return text

def make_it_casual(text):
    kamus = {r'\bAnda\b': 'kamu', r'\bSaya\b': 'aku', r'\bTidak\b': 'nggak', r'\bSangat\b': 'banget'}
    for k, v in kamus.items(): text = re.sub(k, v, text, flags=re.IGNORECASE)
    return text

print("Upload file.rpy kamu")
uploaded = files.upload() # nanti muncul tombol pilih file
input_file = list(uploaded.keys())[0]
output_file = "ID_" + input_file

with open(input_file, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
lines = content.split('\n')
pattern = re.compile(r'^(\s*[a-zA-Z0-9_#]*\s*)"([^"]*?)"(.*)$')
translator = GoogleTranslator(source='auto', target='id')
count = 0

for i, line in enumerate(lines):
    m = pattern.match(line)
    if m and m.group(2).strip():
        text = protect_and_clean(m.group(2))
        hasil = translator.translate(text)
        hasil = make_it_casual(hasil)
        lines[i] = f'{m.group(1)}"{hasil}"{m.group(3)}'
        count += 1
        if count % 500 == 0: print(f"Progress: {count}")

with open(output_file, 'w', encoding='utf-8-sig') as f: f.write('\n'.join(lines))
print(f"SELESAI! {count} baris. Download file:")
files.download(output_file)
