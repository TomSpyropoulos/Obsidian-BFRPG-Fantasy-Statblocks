import json
import os
import subprocess

def process_sourcebook(source_json, output_dir, source_label):
    if not os.path.exists(source_json):
        print(f"Error: {source_json} not found.")
        return

    with open(source_json, 'r') as f:
        data = json.load(f)

    monsters = data.get("fabio:hasPart", [])
    print(f"Converting {len(monsters)} monsters from {source_label}...")

    for i, monster in enumerate(monsters):
        slug = monster.get("slug")
        if not slug: continue
        
        json_path = f"json/{slug}.json"
        if os.path.exists(json_path):
            cmd = ["python3", "transform.py", json_path, output_dir, source_label]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(f"Error in {slug}: {result.stderr.strip()}")
        else:
            print(f"  Warning: {slug}.json not found in cache.")

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(monsters)}...")

if __name__ == "__main__":
    # Use relative path to project root
    base_dir = "../Basic Fantasy RPG Bestiary"
    process_sourcebook("sourcebooks/bfrpg.json", os.path.join(base_dir, "Core Rulebook"), "Core Rulebook")
    process_sourcebook("sourcebooks/field-guide-omnibus.json", os.path.join(base_dir, "Field Guide Omnibus"), "Field Guide Omnibus")
    print("Conversion complete!")
