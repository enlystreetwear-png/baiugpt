import os
import re

raw_folder = "raw_data"
clean_folder = "clean_data"

os.makedirs(clean_folder, exist_ok=True)

for file in os.listdir(raw_folder):

    path = os.path.join(raw_folder, file)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    text = re.sub(r"\s+", " ", text)

    text = text[:500000]

    with open(
        os.path.join(clean_folder, file),
        "w",
        encoding="utf-8"
    ) as f:
        f.write(text)

print("Cleaned data!")