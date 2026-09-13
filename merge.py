# save as merge.py and run: python merge.py
import shutil
from pathlib import Path

Path("dataset/train").mkdir(exist_ok=True)
Path("dataset/val").mkdir(exist_ok=True)

for src in [Path("dataset/potato/train"), Path("dataset/tomato/train")]:
    for cls_folder in src.iterdir():
        dest = Path("dataset/train") / cls_folder.name
        shutil.copytree(cls_folder, dest, dirs_exist_ok=True)
        print(f"Copied {cls_folder.name}")

for src in [Path("dataset/potato/val"), Path("dataset/tomato/val")]:
    for cls_folder in src.iterdir():
        dest = Path("dataset/val") / cls_folder.name
        shutil.copytree(cls_folder, dest, dirs_exist_ok=True)

print("DONE - 8 classes merged")