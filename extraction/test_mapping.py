import json
import re
import math

def load_tables():
    with open('saving_throws.json', 'r') as f:
        data = json.load(f)
    return data['saving_throw_tables']

TABLES = load_tables()

# Racial bonuses from save_special.md
RACIAL_BONUSES = {
    "dwarf": {"death": -4, "wands": -4, "paralysis": -4, "breath": -3, "spells": -4},
    "halfling": {"death": -4, "wands": -4, "paralysis": -4, "breath": -3, "spells": -4},
    "elf": {"death": 0, "wands": -2, "paralysis": -1, "breath": 0, "spells": -2}
}

def get_save_row(class_name, level):
    class_name = class_name.lower().replace("-", "_")
    if class_name not in TABLES:
        # Default to fighter if unknown
        class_name = "fighter"
    
    rows = TABLES[class_name]
    
    # Handle "NM" (Normal Man)
    if str(level).upper() == "NM" or level == 0:
        for row in rows:
            if row['level'] == "NM":
                return row
        return rows[0] # Fallback to first row if NM not found in MU/Cleric/Thief

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
            
    # If level exceeds table, return last row
    return rows[-1]

def parse_save_entry(entry):
    # Entry looks like "Fighter: 6" or "Normal Man" or "Fighter: 1 to 4"
    entry = entry.strip()
    if entry.lower() == "normal man":
        return [("fighter", "NM")]
    
    # Handle ranges like "Fighter: 1 to 4"
    range_match = re.search(r'(.*?):\s*(\d+)\s+to\s+(\d+)', entry)
    if range_match:
        cls = range_match.group(1).strip()
        start = int(range_match.group(2))
        end = int(range_match.group(3))
        return [(cls, i) for i in range(start, end + 1)]

    # Handle single entry "Fighter: 6"
    single_match = re.search(r'(.*?):\s*(\d+)', entry)
    if single_match:
        cls = single_match.group(1).strip()
        lvl = single_match.group(2).strip()
        return [(cls, lvl)]
    
    # Handle "Fighter:10" (no space)
    no_space_match = re.search(r'(.*?):(\d+)', entry)
    if no_space_match:
        cls = no_space_match.group(1).strip()
        lvl = no_space_match.group(2).strip()
        return [(cls, lvl)]

    return [("fighter", "1")] # Fallback

def get_jds(cls, lvl, bonus_type=None):
    row = get_save_row(cls, lvl)
    saves = [
        row['death_ray_poison'],
        row['magic_wands'],
        row['paralysis_petrify'],
        row['dragon_breath'],
        row['spells']
    ]
    
    if bonus_type:
        bonus_type = bonus_type.lower()
        if bonus_type in RACIAL_BONUSES:
            b = RACIAL_BONUSES[bonus_type]
            saves[0] += b['death']
            saves[1] += b['wands']
            saves[2] += b['paralysis']
            saves[3] += b['breath']
            saves[4] += b['spells']
            # Ensure saves don't go below 2 or some reasonable minimum if BFRPG allows
            saves = [max(2, s) for s in saves]
            
    return saves

def test_mapping():
    print("--- Testing Save Mapping ---")
    test_entries = [
        "Fighter: 6",
        "Normal Man",
        "Fighter: 1 to 4",
        "Fighter: 1 (with Elf bonuses)",
        "Magic-User: 4"
    ]
    
    for entry in test_entries:
        print(f"Entry: {entry}")
        bonus = None
        if "elf" in entry.lower(): bonus = "elf"
        elif "dwarf" in entry.lower(): bonus = "dwarf"
        elif "halfling" in entry.lower(): bonus = "halfling"
        
        parsed = parse_save_entry(entry)
        for cls, lvl in parsed:
            jds = get_jds(cls, lvl, bonus)
            print(f"  -> {cls} {lvl} (Bonus: {bonus}): {jds}")

    print("\n--- Testing HD Expansion ---")
    hd_entries = ["1", "1 to 4", "1/2", "1-1"]
    for hd in hd_entries:
        print(f"HD: {hd}")
        # Range logic
        if "to" in hd:
            start, end = map(int, re.findall(r'\d+', hd))
            hds = list(range(start, end + 1))
        elif "-" in hd and not hd.startswith("-"):
            # Could be range 1-4 or bonus 1-1
            # In BFRPG 1-1 usually means 1 HD minus 1 HP
            hds = [hd]
        else:
            hds = [hd]
        
        for h in hds:
            # Derive HP
            try:
                # Handle 1/2 or 1-1
                if h == "1/2": val = 0.5
                elif h == "1-1": val = 0.8 # Rough approx for calculation
                else: val = float(h)
                hp = math.floor(val * 4.5)
                if hp < 1: hp = 1
                
                # Derive THAC0: 19 - floor(HD)
                thac0 = 19 - math.floor(val)
                print(f"  -> Sub-monster: {h} HD, HP: {hp}, THAC0: {thac0}")
            except:
                print(f"  -> Could not derive stats for {h}")

if __name__ == "__main__":
    test_mapping()
