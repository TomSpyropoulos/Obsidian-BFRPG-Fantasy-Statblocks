import json
import os
import re

def normalize(val):
    if not val:
        return val
    # Strip parentheticals like (4hp) or (as Hit Dice)
    val = re.sub(r'\(.*?\)', '', str(val))
    # Keep asterisks but strip extra whitespace
    return val.strip()

def analyze_sourcebook(file_path, hd_output, save_output):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        data = json.load(f)

    unique_hd = set()
    unique_save = set()
    
    monsters = data.get("fabio:hasPart", [])
    print(f"Processing {len(monsters)} monsters from {file_path}...")

    for i, monster in enumerate(monsters):
        slug = monster.get("slug")
        if not slug:
            continue
            
        json_cache_path = f"json/{slug}.json"
        
        if os.path.exists(json_cache_path):
            with open(json_cache_path, 'r') as f:
                monster_data = json.load(f)
        else:
            print(f"Warning: {slug}.json not found in cache.")
            continue

        portrayals = monster_data.get("fabio:hasPortrayal", [])
        for p in portrayals:
            stats = p.get("stats")
            if not stats:
                continue
            hd = stats.get("hitDice")
            save = stats.get("saveAs")
            
            if hd:
                unique_hd.add(normalize(str(hd)))
            if save:
                unique_save.add(normalize(str(save)))
        
    os.makedirs("formats", exist_ok=True)

    with open(hd_output, 'w') as f:
        for item in sorted(list(unique_hd)):
            f.write(f"{item}\n")

    with open(save_output, 'w') as f:
        for item in sorted(list(unique_save)):
            f.write(f"{item}\n")

    os.makedirs("formats", exist_ok=True)

    with open(hd_output, 'w') as f:
        for item in sorted(list(unique_hd)):
            f.write(f"{item}\n")

    with open(save_output, 'w') as f:
        for item in sorted(list(unique_save)):
            f.write(f"{item}\n")

if __name__ == "__main__":
    analyze_sourcebook(
        "sourcebooks/bfrpg.json", 
        "formats/core_hit_dice_format.md", 
        "formats/core_save_format.md"
    )
    analyze_sourcebook(
        "sourcebooks/field-guide-omnibus.json", 
        "formats/field_guide_hit_dice_format.md", 
        "formats/field_guide_save_format.md"
    )
    print("Analysis complete. Check the 'formats/' directory.")
