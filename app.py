from deep_translator import GoogleTranslator
import re, time

def protect_and_clean(text):
    # 1. Simpan tag {i}{/i}{b}{/b} dll
    tags = re.findall(r'\{.*?\}', text)
    for i, tag in enumerate(tags):
        text = text.replace(tag, f'@@TAG{i}@@')
    
    # 2. Bersihin karakter bahaya
    text = text.replace('"', "'").replace('%', ' persen').replace('\\', '/')
    
    # 3. Balikin tag
    for i, tag in enumerate(tags):
        text = text.replace(f'@@TAG{i}@@', tag)
    return text

def make_it_casual(text):
    kamus = {r'\bAnda\b': 'kamu', r'\bSaya\b': 'aku', r'\bTidak\b': 'nggak'}
    for k, v in kamus.items(): text = re.sub(k, v, text, flags=re.IGNORECASE)
    return text

def translate_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
    lines = content.split('\n')
    pattern = re.compile(r'^(\s*[a-zA-Z0-9_#]*\s*)"([^"]*?)"(.*)$')
    translator = GoogleTranslator(source='auto', target='id')
    count = 0

    for i, line in enumerate(lines):
        m = pattern.match(line)
        if m and m.group(2).strip():
            try:
                text = m.group(2)
                text = protect_and_clean(text)
                hasil = translator.translate(text)
                hasil = make_it_casual(hasil)
                lines[i] = f'{m.group(1)}"{hasil}"{m.group(3)}'
                count += 1
                if count % 50 == 0: print(f"Progress: {count}")
                time.sleep(0.3)
            except: time.sleep(5)

    with open(output_file, 'w', encoding='utf-8-sig') as f: f.write('\n'.join(lines))
    print(f"SELESAI! {count} baris. File: {output_file}")

translate_file('/sdcard/Download/akane_events.rpy', '/sdcard/Download/ID_akane_events.rpy')
