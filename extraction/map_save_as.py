import json
import os
import re

# Load tables
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

SAVING_THROW_TABLES = load_json('saving_throws.json')['saving_throw_tables']

RACIAL_BONUSES = {
    "dwarf": {"death": -4, "wands": -4, "paralysis": -4, "breath": -3, "spells": -4},
    "halfling": {"death": -4, "wands": -4, "paralysis": -4, "breath": -3, "spells": -4},
    "elf": {"death": 0, "wands": -2, "paralysis": -1, "breath": 0, "spells": -2}
}

def get_save_row(class_name, level):
    class_name = class_name.lower().strip().replace(" ", "_").replace("-", "_")
    if class_name not in SAVING_THROW_TABLES:
        class_name = "fighter"
    rows = SAVING_THROW_TABLES[class_name]
    
    if str(level).upper() == "NM" or level == 0:
        for row in rows:
            if row['level'] == "NM": return row
        return rows[0]
        
    try:
        lvl_int = int(level)
    except:
        lvl_int = 1
        
    for row in rows:
        lvl_range = row['level']
        if "-" in lvl_range:
            start, end = lvl_range.split("-")
            if int(start) <= lvl_int <= int(end):
                return row
        elif lvl_range == str(lvl_int):
            return row
    return rows[-1]

def calculate_saves(cls, lvl, bonus_type=None):
    row = get_save_row(cls, lvl)
    saves = [row['death_ray_poison'], row['magic_wands'], row['paralysis_petrify'], row['dragon_breath'], row['spells']]
    if bonus_type:
        bonus_type = bonus_type.lower()
        if bonus_type in RACIAL_BONUSES:
            b = RACIAL_BONUSES[bonus_type]
            saves[0] += b['death']
            saves[1] += b['wands']
            saves[2] += b['paralysis']
            saves[3] += b['breath']
            saves[4] += b['spells']
            # OSE rule: saves cannot be better than 2
            saves = [max(2, s) for s in saves]
    return saves

def parse_save_entry(entry):
    # Entry like "Fighter: 1 (+ Elf bonuses)"
    bonus = None
    if "elf" in entry.lower(): bonus = "elf"
    elif "dwarf" in entry.lower(): bonus = "dwarf"
    elif "halfling" in entry.lower(): bonus = "halfling"
    
    clean_entry = re.sub(r'\(.*?\)', '', entry.replace("*", "")).strip()
    
    # Handle "Normal Man"
    if "normal man" in clean_entry.lower():
        return [("fighter", "NM", bonus)]

    # Handle range "Fighter: 1 to Fighter: 4" or "Cleric: 1 to Cleric: 6"
    full_range_match = re.search(r'(.*?):\s*(\d+)\s+(?:to|[-–])\s+(.*?):\s*(\d+)', clean_entry)
    if full_range_match:
        cls1 = full_range_match.group(1).strip()
        start = int(full_range_match.group(2))
        cls2 = full_range_match.group(3).strip()
        end = int(full_range_match.group(4))
        # Use cls1 for the range
        return [(cls1, lvl, bonus) for lvl in range(start, end + 1)]

    # Handle range "Fighter: 1 to 4"
    range_match = re.search(r'(.*?):\s*(\d+)\s+(?:to|[-–])\s+(\d+)', clean_entry)
    if range_match:
        cls = range_match.group(1).strip()
        start = int(range_match.group(2))
        end = int(range_match.group(3))
        return [(cls, lvl, bonus) for lvl in range(start, end + 1)]

    # Handle "Fighter 6" (missing colon)
    missing_colon = re.search(r'([a-zA-Z-]+)\s+(\d+)', clean_entry)
    if missing_colon and ":" not in clean_entry:
        return [(missing_colon.group(1).strip(), missing_colon.group(2).strip(), bonus)]

    # Handle single "Fighter: 10"
    single_match = re.search(r'(.*?):\s*(-?\d+)', clean_entry)
    if single_match:
        cls = single_match.group(1).strip()
        lvl = single_match.group(2).strip()
        # Handle negative levels by treating as level 1
        if int(lvl) < 1: lvl = 1
        return [(cls, lvl, bonus)]
        
    return [("fighter", 1, bonus)]

def generate_mapping():
    mapping = []
    with open("formats/unique_save_as.md", "r") as f:
        for line in f:
            full_line = line.strip()
            if not full_line: continue
            
            # Remove filename prefix if present (e.g., "json/aboleth.json:")
            if ".json:" in full_line:
                entry = full_line.split(".json:", 1)[1].strip()
            else:
                entry = full_line
            
            try:
                parsed = parse_save_entry(entry)
                results = []
                for cls, lvl, bonus in parsed:
                    saves = calculate_saves(cls, lvl, bonus)
                    results.append(f"{cls} {lvl}{' + '+bonus if bonus else ''} -> {saves}")
                
                mapping.append(f"{entry} -> {', '.join(results)}")
            except Exception as e:
                mapping.append(f"{entry} -> ERROR: {str(e)}")

    with open("formats/save_as_mapping.md", "w") as f:
        f.write("\n".join(mapping))
    print("Mapping generated in formats/save_as_mapping.md")

if __name__ == "__main__":
    generate_mapping()
