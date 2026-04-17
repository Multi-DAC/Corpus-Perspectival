path = r'C:\Users\Wasch\clawd\projects\aigrandprix\sim\train_v9_dagger_warmstart.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('\u2192', '->')
content = content.replace('\u2190', '<-')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Fixed unicode arrows")
