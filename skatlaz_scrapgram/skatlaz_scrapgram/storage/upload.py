import os
import uuid

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file):
    ext = file.filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, name)

    file.save(path)
    return path
