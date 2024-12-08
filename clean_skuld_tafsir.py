import json
import re

file_path = 'C:\\Users\\DELL\\Desktop\\quran_with_tafsir_skuld_operation.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)


for surah in data : 
    for verse in surah['verses'] :
        verse['translation'] = re.sub(r"\[.*?\]", "", verse['translation'])
        verse['translation'] = re.sub(r"[^a-zA-Z\s'-]", "", verse['translation'])
        verse['translation'] = verse['translation'].strip()


output_file_path = "C:\\Users\\DELL\\Desktop\\skuld_tafsir_pro.json"

with open(output_file_path, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

