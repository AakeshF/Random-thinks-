import json
import shutil
import sys
import os

if len(sys.argv) < 4:
    print("Usage: python copy_images.py input.json new_image_folder output.json")
    print("  input.json       - JSON with image paths")
    print("  new_image_folder - where to copy images to")
    print("  output.json      - new JSON with updated paths")
    sys.exit(1)

json_path = sys.argv[1]
new_folder = sys.argv[2]
output_json = sys.argv[3]

os.makedirs(new_folder, exist_ok=True)

print(f"Loading {json_path}...")
tasks = json.load(open(json_path))
print(f"Total tasks: {len(tasks)}")

copied = 0
skipped = 0

for task in tasks:
    data = task.get("data", {})
    image_path = data.get("image", "")

    if not image_path or image_path.startswith("data:"):
        skipped += 1
        continue

    if not os.path.exists(image_path):
        print(f"Not found, skipping: {image_path}")
        skipped += 1
        continue

    filename = os.path.basename(image_path)
    new_path = os.path.join(new_folder, filename)

    shutil.copy2(image_path, new_path)
    data["image"] = new_path
    copied += 1

with open(output_json, "w") as f:
    json.dump(tasks, f, indent=2)

print(f"Copied: {copied} images to {new_folder}")
print(f"Skipped: {skipped}")
print(f"New JSON: {output_json}")
