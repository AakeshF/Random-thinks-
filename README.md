import os
import json
import base64
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

TAG_MAP = {
“0015:2010”: “component”,
“0015:2011”: “stage”,
“0015:2012”: “feature”,
“0015:2065”: “finding_type”,
“0040:A30A”: “measurement_value”,
“0013:4019”: “measurement_type”,
“0008:0020”: “study_date”,
“0008:0060”: “modality”,
“0013:4010”: “equipment”,
}

ALLOWED_DEFECTS = {
“crack”,
“dent”,
“corrosion”,
“nick”,
“fod”,
“rub”,
“missing material”,
“missing coating”,
“deposit”,
“fretting”,
“burn”,
“discoloration”,
“desiccant”,
“blend”,
}

def parse_xml(xml_path):
tree = ET.parse(xml_path)
meta = {}
for attr in tree.findall(”.//DICOM_ATTRIBUTE”):
tag = attr.get(“TAG”, “”)
if tag in TAG_MAP:
meta[TAG_MAP[tag]] = (attr.text or “”).strip()
return meta

def image_to_base64(image_path):
with open(image_path, “rb”) as img_file:
encoded = base64.b64encode(img_file.read()).decode(“utf-8”)
return “data:image/jpeg;base64,” + encoded

def find_xml(image_base, scan_dir, report):
“”“Look for matching XML in same folder or XML subfolder.”””
candidates = [
os.path.join(scan_dir, image_base + “.xml”),
os.path.join(scan_dir, “XML”, image_base + “.xml”),
os.path.join(scan_dir, “xml”, image_base + “.xml”),
]
# Also try without report prefix
if image_base.upper().startswith(report.upper() + “_”):
stripped = image_base[len(report) + 1:]
candidates.append(os.path.join(scan_dir, stripped + “.xml”))
candidates.append(os.path.join(scan_dir, “XML”, stripped + “.xml”))
candidates.append(os.path.join(scan_dir, “xml”, stripped + “.xml”))
for c in candidates:
if os.path.exists(c):
return c
return None

def main():
script_dir = Path(**file**).resolve().parent
parser = argparse.ArgumentParser(
description=“Export Label Studio tasks with embedded base64 images.”
)
parser.add_argument(
“–data-dir”,
default=str(script_dir),
help=“Top-level folder containing report subfolders”,
)
parser.add_argument(
“–output”,
default=str(script_dir / “label_studio_tasks.json”),
help=“Output JSON path”,
)
args = parser.parse_args()
data_dir = args.data_dir
output_path = args.output

```
tasks = []
skipped_no_xml = 0
skipped_defect = 0
scanned = 0

for report in sorted(os.listdir(data_dir)):
    report_dir = os.path.join(data_dir, report)
    if not os.path.isdir(report_dir):
        continue

    # Walk all subdirectories under each report folder
    for root, dirs, files in os.walk(report_dir):
        for f in sorted(files):
            if not f.lower().endswith((".jpg", ".jpeg")):
                continue

            # Accept LPT_*.jpg or <report>_LPT_*.jpg
            if not f.upper().startswith("LPT_"):
                if not f.upper().startswith(report.upper() + "_LPT_"):
                    continue

            scanned += 1
            base = os.path.splitext(f)[0]
            xml_path = find_xml(base, root, report)

            if xml_path is None:
                skipped_no_xml += 1
                continue

            meta = parse_xml(xml_path)
            meta["report"] = report

            finding = (meta.get("finding_type") or "").strip().lower()
            if finding not in ALLOWED_DEFECTS:
                skipped_defect += 1
                continue

            unique_name = report + "_" + f
            old_path = os.path.join(root, f)
            new_path = os.path.join(root, unique_name)

            if old_path != new_path and not os.path.exists(new_path):
                os.rename(old_path, new_path)

            img_path = new_path if os.path.exists(new_path) else old_path

            tasks.append({
                "data": {
                    "image": image_to_base64(img_path),
                    **meta,
                }
            })

with open(output_path, "w") as out_file:
    json.dump(tasks, out_file, indent=2)

print("Scanned: " + str(scanned) + " LPT images")
print("Skipped (no XML): " + str(skipped_no_xml))
print("Skipped (defect not in list): " + str(skipped_defect))
print("Exported: " + str(len(tasks)) + " tasks")
print("Wrote: " + str(output_path))
```

if **name** == “**main**”:
main()
