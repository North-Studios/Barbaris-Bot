import json

# Открываем файл и читаем
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data)        # Python-словарь
print(data["name"]) # Доступ по ключу