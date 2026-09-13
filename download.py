import kagglehub
import shutil
import os

# Small Tomato 5 class dataset
print("Downloading...")
path = kagglehub.dataset_download("kaustubhb999/tomatoleaf")
print("Downloaded to:", path)

# Copy to our project
# This dataset has 10 classes, we will take only 5 to save RAM
import pathlib
src = pathlib.Path(path)
dst = pathlib.Path("dataset")
dst.mkdir(exist_ok=True)

# Pick 5 classes only for your 8GB laptop
wanted = ["Tomato___healthy", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Bacterial_spot", "Tomato___Leaf_Mold"]
# If names differ, it will take first 5 folders
all_classes = [d for d in src.iterdir() if d.is_dir()]
if len(all_classes) == 0: # check inside subfolder
    for d in src.rglob("*"):
        if d.is_dir() and len(list(d.glob("*.jpg")))>10:
            all_classes.append(d)

print("Found classes:", [c.name for c in all_classes])

for c in all_classes[:5]:
    if c.name in wanted or len(wanted)==5:
        target = dst / c.name.replace("Tomato___","")
        if not target.exists():
            shutil.copytree(c, target)
            print(f"Copied {c.name} -> {target}")

print("Done! Now run: dir dataset")