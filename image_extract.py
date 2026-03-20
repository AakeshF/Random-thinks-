import json
import base64
import sys
import os

if len(sys.argv) < 3:
print(“Usage: python extract_images.py input.json output_folder”)
sys.exit(1)

json_path = sys.argv[1]
output_dir = sys.argv[2]

os.makedirs(output_dir, exist_ok=True)

print(f”Loading {json_path}…”)
tasks = json.load(open(json_path))
print(f”Total tasks: {len(tasks)}”)

# Track counts per name base for sequential numbering

name_counts = {}

for task in tasks:
data = task.get(“data”, {})
image_b64 = data.get(“image”, “”)

```
if not image_b64:
    continue

# Strip the data:image/jpeg;base64, prefix
if "," in image_b64:
    image_b64 = image_b64.split(",", 1)[1]

component = (data.get("component") or "").strip().upper().replace(" ", "_")
stage = (data.get("stage") or "").strip().upper().replace(" ", "_")
feature = (data.get("feature") or "").strip().upper().replace(" ", "_")

# Build name like LPT_STG_3_NOZZLES
name_base = "LPT"
if stage:
    name_base += "_STG_" + stage
if feature:
    name_base += "_" + feature

# Sequential numbering per unique name base
if name_base not in name_counts:
    name_counts[name_base] = 0
name_counts[name_base] += 1
seq = str(name_counts[name_base]).zfill(3)

filename = f"{name_base}_{seq}.jpg"
filename = filename.replace("/", "_").replace("\\", "_")

out_path = os.path.join(output_dir, filename)
with open(out_path, "wb") as f:
    f.write(base64.b64decode(image_b64))

print(f"Extracted: {filename}")
```

print(f”Done. Extracted {sum(name_counts.values())} images to {output_dir}”)