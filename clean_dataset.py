import re

# Load stories
with open("data/stories.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Remove bad tokens
text = text.replace("<unk>", "")

# Remove extra spaces/newlines
text = re.sub(r"\s+", " ", text)

# Save cleaned dataset
with open("data/clean.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Dataset cleaned successfully!")
print("Characters:", len(text))