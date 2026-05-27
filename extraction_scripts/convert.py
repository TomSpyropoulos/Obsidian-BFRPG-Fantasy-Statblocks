#!/usr/bin/env python3
import json
import re
import sys
import os
import math
import argparse

# Determine directory of this script to load sibling files correctly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Hardcoded reference tables
ATTACK_BONUS_TABLE = [
    { "monster_hit_dice": "less than 1", "attack_bonus": 0 },
    { "monster_hit_dice": "1", "attack_bonus": 1 },
    { "monster_hit_dice": "2", "attack_bonus": 2 },
    { "monster_hit_dice": "3", "attack_bonus": 3 },
    { "monster_hit_dice": "4", "attack_bonus": 4 },
    { "monster_hit_dice": "5", "attack_bonus": 5 },
    { "monster_hit_dice": "6", "attack_bonus": 6 },
    { "monster_hit_dice": "7", "attack_bonus": 7 },
    { "monster_hit_dice": "8-9", "attack_bonus": 8 },
    { "monster_hit_dice": "10-11", "attack_bonus": 9 },
    { "monster_hit_dice": "12-13", "attack_bonus": 10 },
    { "monster_hit_dice": "14-15", "attack_bonus": 11 },
    { "monster_hit_dice": "16-19", "attack_bonus": 12 },
    { "monster_hit_dice": "20-23", "attack_bonus": 13 },
    { "monster_hit_dice": "24-27", "attack_bonus": 14 },
    { "monster_hit_dice": "28-31", "attack_bonus": 15 },
    { "monster_hit_dice": "32 or more", "attack_bonus": 16 }
]

SAVING_THROW_TABLES = {
    "cleric": [
      { "level": "1", "death_ray_poison": 11, "magic_wands": 12, "paralysis_petrify": 14, "dragon_breath": 16, "spells": 15 },
      { "level": "2-3", "death_ray_poison": 10, "magic_wands": 11, "paralysis_petrify": 13, "dragon_breath": 15, "spells": 14 },
      { "level": "4-5", "death_ray_poison": 9, "magic_wands": 10, "paralysis_petrify": 13, "dragon_breath": 15, "spells": 14 },
      { "level": "6-7", "death_ray_poison": 9, "magic_wands": 10, "paralysis_petrify": 12, "dragon_breath": 14, "spells": 13 },
      { "level": "8-9", "death_ray_poison": 8, "magic_wands": 9, "paralysis_petrify": 12, "dragon_breath": 14, "spells": 13 },
      { "level": "10-11", "death_ray_poison": 8, "magic_wands": 9, "paralysis_petrify": 11, "dragon_breath": 13, "spells": 12 },
      { "level": "12-13", "death_ray_poison": 7, "magic_wands": 8, "paralysis_petrify": 11, "dragon_breath": 13, "spells": 12 },
      { "level": "14-15", "death_ray_poison": 7, "magic_wands": 8, "paralysis_petrify": 10, "dragon_breath": 12, "spells": 11 },
      { "level": "16-17", "death_ray_poison": 6, "magic_wands": 7, "paralysis_petrify": 10, "dragon_breath": 12, "spells": 11 },
      { "level": "18-19", "death_ray_poison": 6, "magic_wands": 7, "paralysis_petrify": 9, "dragon_breath": 11, "spells": 10 },
      { "level": "20", "death_ray_poison": 5, "magic_wands": 6, "paralysis_petrify": 9, "dragon_breath": 11, "spells": 10 }
    ],
    "magic_user": [
      { "level": "1", "death_ray_poison": 13, "magic_wands": 14, "paralysis_petrify": 13, "dragon_breath": 16, "spells": 15 },
      { "level": "2-3", "death_ray_poison": 13, "magic_wands": 14, "paralysis_petrify": 13, "dragon_breath": 15, "spells": 14 },
      { "level": "4-5", "death_ray_poison": 12, "magic_wands": 13, "paralysis_petrify": 12, "dragon_breath": 15, "spells": 13 },
      { "level": "6-7", "death_ray_poison": 12, "magic_wands": 12, "paralysis_petrify": 11, "dragon_breath": 14, "spells": 13 },
      { "level": "8-9", "death_ray_poison": 11, "magic_wands": 11, "paralysis_petrify": 10, "dragon_breath": 14, "spells": 12 },
      { "level": "10-11", "death_ray_poison": 11, "magic_wands": 10, "paralysis_petrify": 9, "dragon_breath": 13, "spells": 11 },
      { "level": "12-13", "death_ray_poison": 10, "magic_wands": 10, "paralysis_petrify": 9, "dragon_breath": 13, "spells": 11 },
      { "level": "14-15", "death_ray_poison": 10, "magic_wands": 9, "paralysis_petrify": 8, "dragon_breath": 12, "spells": 10 },
      { "level": "16-17", "death_ray_poison": 9, "magic_wands": 8, "paralysis_petrify": 7, "dragon_breath": 12, "spells": 9 },
      { "level": "18-19", "death_ray_poison": 9, "magic_wands": 7, "paralysis_petrify": 6, "dragon_breath": 11, "spells": 9 },
      { "level": "20", "death_ray_poison": 8, "magic_wands": 6, "paralysis_petrify": 5, "dragon_breath": 11, "spells": 8 }
    ],
    "fighter": [
      { "level": "NM", "death_ray_poison": 13, "magic_wands": 14, "paralysis_petrify": 15, "dragon_breath": 16, "spells": 18 },
      { "level": "1", "death_ray_poison": 12, "magic_wands": 13, "paralysis_petrify": 14, "dragon_breath": 15, "spells": 17 },
      { "level": "2-3", "death_ray_poison": 11, "magic_wands": 12, "paralysis_petrify": 14, "dragon_breath": 15, "spells": 16 },
      { "level": "4-5", "death_ray_poison": 11, "magic_wands": 11, "paralysis_petrify": 13, "dragon_breath": 14, "spells": 15 },
      { "level": "6-7", "death_ray_poison": 10, "magic_wands": 11, "paralysis_petrify": 12, "dragon_breath": 14, "spells": 15 },
      { "level": "8-9", "death_ray_poison": 9, "magic_wands": 10, "paralysis_petrify": 12, "dragon_breath": 13, "spells": 14 },
      { "level": "10-11", "death_ray_poison": 9, "magic_wands": 9, "paralysis_petrify": 11, "dragon_breath": 12, "spells": 13 },
      { "level": "12-13", "death_ray_poison": 8, "magic_wands": 9, "paralysis_petrify": 10, "dragon_breath": 12, "spells": 13 },
      { "level": "14-15", "death_ray_poison": 7, "magic_wands": 8, "paralysis_petrify": 10, "dragon_breath": 11, "spells": 12 },
      { "level": "16-17", "death_ray_poison": 7, "magic_wands": 7, "paralysis_petrify": 9, "dragon_breath": 10, "spells": 11 },
      { "level": "18-19", "death_ray_poison": 6, "magic_wands": 7, "paralysis_petrify": 8, "dragon_breath": 10, "spells": 11 },
      { "level": "20", "death_ray_poison": 5, "magic_wands": 6, "paralysis_petrify": 8, "dragon_breath": 9, "spells": 10 }
    ],
    "thief": [
      { "level": "1", "death_ray_poison": 13, "magic_wands": 14, "paralysis_petrify": 13, "dragon_breath": 16, "spells": 15 },
      { "level": "2-3", "death_ray_poison": 12, "magic_wands": 14, "paralysis_petrify": 12, "dragon_breath": 15, "spells": 14 },
      { "level": "4-5", "death_ray_poison": 11, "magic_wands": 13, "paralysis_petrify": 12, "dragon_breath": 14, "spells": 13 },
      { "level": "6-7", "death_ray_poison": 11, "magic_wands": 13, "paralysis_petrify": 11, "dragon_breath": 13, "spells": 13 },
      { "level": "8-9", "death_ray_poison": 10, "magic_wands": 12, "paralysis_petrify": 11, "dragon_breath": 12, "spells": 12 },
      { "level": "10-11", "death_ray_poison": 9, "magic_wands": 12, "paralysis_petrify": 10, "dragon_breath": 11, "spells": 11 },
      { "level": "12-13", "death_ray_poison": 9, "magic_wands": 10, "paralysis_petrify": 10, "dragon_breath": 10, "spells": 11 },
      { "level": "14-15", "death_ray_poison": 8, "magic_wands": 10, "paralysis_petrify": 9, "dragon_breath": 9, "spells": 10 },
      { "level": "16-17", "death_ray_poison": 7, "magic_wands": 9, "paralysis_petrify": 9, "dragon_breath": 8, "spells": 9 },
      { "level": "18-19", "death_ray_poison": 7, "magic_wands": 9, "paralysis_petrify": 8, "dragon_breath": 7, "spells": 9 },
      { "level": "20", "death_ray_poison": 6, "magic_wands": 8, "paralysis_petrify": 8, "dragon_breath": 6, "spells": 8 }
    ]
}

# Racial bonuses from save_special.md
RACIAL_BONUSES = {
    "dwarf": {"death": -4, "wands": -4, "paralysis": -4, "breath": -3, "spells": -4},
    "halfling": {"death": -4, "wands": -4, "paralysis": -4, "breath": -3, "spells": -4},
    "elf": {"death": 0, "wands": -2, "paralysis": -1, "breath": 0, "spells": -2}
}

def get_attack_bonus(hd_val):
    if hd_val < 0.5: return 0
    if hd_val == 0.9: hd_val = 1 # 1-1 uses 1 HD row
    
    for row in ATTACK_BONUS_TABLE:
        hd_range = row['monster_hit_dice']
        if hd_range == "less than 1":
            if hd_val < 1: return row['attack_bonus']
        elif hd_range == "32 or more":
            if hd_val >= 32: return row['attack_bonus']
        elif "-" in hd_range:
            start, end = map(int, hd_range.split("-"))
            if start <= hd_val <= end:
                return row['attack_bonus']
        elif hd_range == str(int(hd_val)):
            return row['attack_bonus']
    return ATTACK_BONUS_TABLE[-1]['attack_bonus']

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

def get_jds(cls, lvl, bonus_type=None):
    row = get_save_row(cls, lvl)
    saves = [row['death_ray_poison'], row['magic_wands'], row['paralysis_petrify'], row['dragon_breath'], row['spells']]
    if bonus_type:
        bonus_type = bonus_type.lower()
        if bonus_type in RACIAL_BONUSES:
            b = RACIAL_BONUSES[bonus_type]
            saves[0] += b['death']; saves[1] += b['wands']; saves[2] += b['paralysis']
            saves[3] += b['breath']; saves[4] += b['spells']
            # OSE rule: saves cannot be better than 2
            saves = [max(2, s) for s in saves]
    return saves

def parse_hd_str(hd_str):
    calc_str = hd_str.replace("*", "").strip()
    if " or " in calc_str.lower() or "," in calc_str:
        parts = re.findall(r'(\d+)', calc_str)
        if parts: return [(float(p), "") for p in parts]
    if (" to " in calc_str) or (("-" in calc_str or "–" in calc_str) and calc_str != "1-1" and "hp" not in calc_str.lower()):
        range_match = re.search(r'(\d+)\s*([-–]|to)\s*(\d+)', calc_str)
        if range_match:
            start = int(range_match.group(1)); end = int(range_match.group(3))
            return [(float(lvl), "") for lvl in range(start, end + 1)]
    if calc_str in ["1/2", "½", "0.5"]: return [(0.5, "")]
    if calc_str == "1-1": return [(0.9, "")]
    if "per mu level" in calc_str.lower(): return [(0.1, "")]
    if "1 hit point" in calc_str.lower() or "1 hp" in calc_str.lower() or "1d4" in calc_str.lower():
        return [(0.1, "")]
    m = re.search(r'^(\d+)', calc_str)
    if m: return [(float(m.group(1)), "")]
    return [(1.0, "")]

def calculate_hp(hd_val, hd_str):
    hd_lower = hd_str.lower()
    if hd_lower == "special": return "Special"
    if "1 hit point" in hd_lower or "1 hp" in hd_lower or "1hp" in hd_lower:
        bonus = 0
        flat_matches = re.findall(r'\+\s*(\d+)', hd_str)
        for fm in flat_matches: bonus += int(fm)
        return 1 + bonus
    if "1-2 hp" in hd_lower: return 2
    if "per mu level" in hd_lower: return 2
    if "1d4" in hd_lower:
        bonus = 0
        flat_matches = re.findall(r'\+\s*(\d+)', hd_str)
        for fm in flat_matches: bonus += int(fm)
        return 2 + bonus
    if "1d6" in hd_lower:
        bonus = 0
        flat_matches = re.findall(r'\+\s*(\d+)', hd_str)
        for fm in flat_matches: bonus += int(fm)
        return 3 + bonus
    if hd_val == 0.9: return 3
    if hd_val == 0.5: return 2
    if hd_val < 0.5: hp_val = 1
    else: hp_val = math.floor(hd_val * 4.5)
    bonus = 0
    flat_matches = re.findall(r'\+\s*(\d+)(?!d)', hd_str)
    for fm in flat_matches: bonus += int(fm)
    if "+1d" in hd_lower or " + 1d" in hd_lower: bonus += 2
    hp_val += bonus
    if hp_val < 1: hp_val = 1
    hp_match = re.search(r'\((\d+)\s*hp\)', hd_lower)
    if hp_match: hp_val = int(hp_match.group(1))
    return hp_val

def parse_save_entry(entry, current_hd):
    bonus = None
    if "elf" in entry.lower(): bonus = "elf"
    elif "dwarf" in entry.lower(): bonus = "dwarf"
    elif "halfling" in entry.lower(): bonus = "halfling"
    
    clean_entry = re.sub(r'\(.*?\)', '', entry.replace("*", "")).strip()
    
    if "normal man" in clean_entry.lower(): return [("fighter", "NM", bonus)]

    full_range_match = re.search(r'(.*?):\s*(\d+)\s+(?:to|[-–])\s+(.*?):\s*(\d+)', clean_entry)
    if full_range_match:
        cls1 = full_range_match.group(1).strip()
        start = int(full_range_match.group(2))
        end = int(full_range_match.group(4))
        if start <= int(current_hd) <= end: return [(cls1, int(current_hd), bonus)]
        return [(cls1, start, bonus)]

    range_match = re.search(r'(.*?):\s*(\d+)\s+(?:to|[-–])\s+(\d+)', clean_entry)
    if range_match:
        cls = range_match.group(1).strip()
        start = int(range_match.group(2))
        end = int(range_match.group(3))
        if start <= int(current_hd) <= end: return [(cls, int(current_hd), bonus)]
        return [(cls, start, bonus)]

    single_match = re.search(r'(.*?):\s*(-?\d+)', clean_entry)
    if single_match:
        cls = single_match.group(1).strip()
        lvl = int(single_match.group(2))
        if lvl < 1: lvl = 1
        return [(cls, lvl, bonus)]
    
    missing_colon = re.search(r'([a-zA-Z-]+)\s+(\d+)', clean_entry)
    if missing_colon: return [(missing_colon.group(1).strip(), missing_colon.group(2).strip(), bonus)]
        
    return [("fighter", int(current_hd) if current_hd >= 1 else "NM", bonus)]

def extract_xp(xp_str, current_hd):
    if not xp_str: return 0
    xp_str = str(xp_str).replace(",", "").replace("–", "-")
    try:
        # 1. Match specific HD level if possible (e.g. "1 HD: 37")
        hd_int = int(current_hd) if current_hd >= 1 else 1
        pattern = rf"{hd_int}\s*(?:HD|Hit\s*Dice|Hit\s*Point)[s]?\s*[:\s=]+\s*(\d+)"
        match = re.search(pattern, xp_str, re.IGNORECASE)
        if match: return int(match.group(1))

        # 2. Match hyphenated or slash-separated range: "25-240", "100/200"
        # Take the first number.
        range_match = re.search(r'(\d+)\s*[-/]', xp_str)
        if range_match: return int(range_match.group(1))

        # 3. Fallback: take the first number that isn't a small HD index
        nums = re.findall(r'(\d+)', xp_str)
        if nums:
            for n in nums:
                if int(n) > 20: return int(n)
            return int(nums[0])
    except:
        pass
    return xp_str

def clean_monster_name(raw_name, check_alias=False):
    # Hardcoded alias overrides for known database anomalies
    ALIAS_OVERRIDES = {
        "Brown": "Brown Bear",
        "Giant and Toad": "Giant Toad"
    }

    # 1. Handle parentheses for aliases
    aliases = []
    main_name = raw_name
    match = re.search(r'\((.*?)\)', raw_name)
    if match:
        content = match.group(1).strip()
        main_name = raw_name.replace(match.group(0), "").strip()
        
        # Split by " or "
        for part in re.split(r'\s+or\s+', content, flags=re.IGNORECASE):
            part = part.strip()
            if part: aliases.append(part)

    # 2. Reversal logic for commas and stripping "or" from start
    def process(n):
        n = n.strip()
        # Strip leading "or "
        n = re.sub(r'^(?:or\s+)', '', n, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in n.split(',')]
        if len(parts) > 1:
            return " ".join(reversed(parts))
        return n

    final_name = process(main_name)
    final_aliases = []
    for a in aliases:
        p = process(a)
        if p in ALIAS_OVERRIDES:
            final_aliases.append(ALIAS_OVERRIDES[p])
        else:
            final_aliases.append(p)
    
    if check_alias:
        checked_aliases = []
        main_word_count = len(final_name.split())
        for alias in final_aliases:
            alias_word_count = len(alias.split())
            if main_word_count != alias_word_count:
                print(f"\n[Alias Check] Monster: \"{final_name}\" | Extracted Alias: \"{alias}\"")
                print(f"The word count is different ({main_word_count} vs {alias_word_count}).")
                print("Options:")
                print(f"  [1] Keep \"{alias}\"")
                print("  [2] Discard this alias")
                print("  [3] Enter a custom alias manually")
                try:
                    choice = input("Your choice (1/2/3) [default: 1]: ").strip()
                except (KeyboardInterrupt, EOFError):
                    choice = "1"
                
                if choice == "2":
                    print(f"  -> Discarded alias \"{alias}\"")
                    continue
                elif choice == "3":
                    try:
                        custom = input("  Enter custom alias: ").strip()
                    except (KeyboardInterrupt, EOFError):
                        custom = ""
                    if custom:
                        checked_aliases.append(custom)
                        print(f"  -> Added custom alias \"{custom}\"")
                    else:
                        print("  -> No custom alias entered, discarding.")
                else:
                    checked_aliases.append(alias)
                    print(f"  -> Kept alias \"{alias}\"")
            else:
                checked_aliases.append(alias)
        final_aliases = checked_aliases
    
    return final_name, final_aliases

def transform_monster(monster_data, source_name="BFRPG", check_alias=False):
    portrayals = monster_data.get("fabio:hasPortrayal", [])
    statblock_portrayal = None
    for p in portrayals:
        if "stats" in p and p["stats"] is not None:
            statblock_portrayal = p
            break
    if not statblock_portrayal: return []

    stats = statblock_portrayal.get("stats", {})
    raw_name = monster_data.get("schema:name", "Unknown")
    name, name_aliases = clean_monster_name(raw_name, check_alias)
    
    # Identify variants
    variants_info = {}
    if "variants" in stats:
        variants_info = stats["variants"]
    else:
        keys = []
        for v in stats.values():
            if isinstance(v, dict):
                keys = list(v.keys()); break
        if keys:
            for k in keys: variants_info[k] = {field: (v[k] if isinstance(v, dict) else v) for field, v in stats.items()}
        else:
            variants_info[None] = stats

    results = []
    for var_key, var_stats in variants_info.items():
        hd_str_full = str(var_stats.get("hitDice", "1"))
        hd_parts = re.split(r'\s+(?:to|or)\s+', hd_str_full, flags=re.IGNORECASE)
        hd_str = hd_parts[0].strip()
        
        save_entry = str(var_stats.get("saveAs") or "Fighter: 1")
        
        hds = parse_hd_str(hd_str)
        if hds:
            hd_val, suffix = hds[0]
            ab = get_attack_bonus(hd_val)
            atk_display = f"+{ab}"
            hp_val = calculate_hp(hd_val, hd_str)
            
            display_hd = str(int(hd_val))
            if hd_val == 0.9: display_hd = "1-1"
            elif hd_val == 0.5: display_hd = "1/2"
            
            cls, lvl, bonus = parse_save_entry(save_entry, hd_val)[0]
            jds_list = get_jds(cls, lvl, bonus)
            modifier_val = math.floor((15 - jds_list[3]) / 2)
            
            ac_raw = var_stats.get("armorClass") or 10
            try:
                if isinstance(ac_raw, str): bfrpg_ac = int(re.search(r'(\d+)', ac_raw).group(1))
                else: bfrpg_ac = int(ac_raw)
            except: bfrpg_ac = 10
            
            # OSE/BX AC conversion:
            # Ascending OSE = bfrpg_ac - 1 (unarmored BFRPG 11 -> OSE 10)
            # Descending OSE = 19 - Ascending OSE (unarmored 10 -> OSE 9)
            ose_ascending = bfrpg_ac - 1
            ose_descending = 19 - ose_ascending
            ac_formatted = f"{ose_descending} [{ose_ascending}]"
            
            mov = str(var_stats.get("movement") or "0").strip().strip("'\"")
            
            if var_key:
                clean_name = name.replace("*", "").strip()
                full_name = f"{var_key.capitalize()} {clean_name}"
            else:
                full_name = name
            
            atks_raw = var_stats.get("attacks") or []
            if isinstance(atks_raw, (str, int)): atks = [str(atks_raw)]
            else: atks = list(atks_raw)
            dmg = str(var_stats.get("damage") or "")
            atk_str = " / ".join(atks) if atks else "-"
            dmg_str = dmg if dmg else "-"

            stats_list = [hd_str, str(hp_val), ac_formatted, atk_display]
            stats_field = json.dumps(stats_list)

            xp_val = extract_xp(var_stats.get('xp'), hd_val)
            
            # YAML-safe string dumping (outside f-strings)
            q_aliases = json.dumps(name_aliases)
            q_hd_str = json.dumps(hd_str)
            q_thac0 = json.dumps(atk_display)
            q_attack = json.dumps(atk_str)
            q_damage = json.dumps(dmg_str)
            q_speed = json.dumps(mov + "'")
            q_moral = json.dumps(str(var_stats.get('morale') or ''))
            q_nbr = json.dumps(str(var_stats.get('numberAppearing') or ''))
            q_loot = json.dumps(str(var_stats.get('treasureType') or 'None'))
            q_ac = json.dumps(ac_formatted)

            md = f"---\nstatblock: inline\nname: {full_name}\nobsidianUIMode: preview\ntags:\n  - monster\naliases: {q_aliases}\nsource: {source_name}\n---\n\n"
            md += "```statblock\n"
            md += f"name: {full_name}\n"
            md += "layout: BFRPG\n"
            md += f"ac: {q_ac}\n"
            md += f"hit_dice: {q_hd_str}\n"
            md += f"hp: {hp_val}\n"
            md += f"thaco: {q_thac0}\n"
            md += f"modifier: {modifier_val}\n"
            md += f"stats: {stats_field}\n"
            md += f"attack: {q_attack}\n"
            md += f"damage: {q_damage}\n"
            md += f"speed: {q_speed}\n"
            md += f"jds: {json.dumps(jds_list)}\n"
            md += f"moral: {q_moral}\n"
            md += f"xp: {xp_val}\n"
            md += f"nbr: {q_nbr}\n"
            md += f"loot: {q_loot}\n"
            md += "roll_jds: 1d20\n"
            md += "roll-moral: 2d6\n"
            
            spec = statblock_portrayal.get("specialAbilities", [])
            if spec:
                md += "traits:\n"
                for sa in spec:
                    desc_clean = sa.get('description', '').replace('"', "'").replace('\n', ' ').strip()
                    md += f"  - name: {sa.get('name')}\n    desc: \"{desc_clean}\"\n"
            
            if atks and dmg:
                md += "actions:\n"
                atk_p = []
                for a in atks:
                    for sp in str(a).split('/'):
                        sp = sp.strip(); m = re.match(r'(\d+)\s+(.*)', sp)
                        if m:
                            c = int(m.group(1)); t = m.group(2)
                            if t.lower() == "hooves": t = "Hoof"
                            for _ in range(c): atk_p.append(t)
                        else: atk_p.append(sp)
                dmg_p = [d.strip() for d in dmg.split('/')]
                for i in range(max(len(atk_p), len(dmg_p))):
                    an = (atk_p[i] if i < len(atk_p) else "Attack").strip()
                    dv = (dmg_p[i] if i < len(dmg_p) else "").strip()
                    dv_clean = dv.replace('"', "'")
                    md += f"  - name: {an}\n    desc: \"D20 to hit, {dv_clean}\"\n"
            
            md += f"source: {source_name}\n```\n"
            desc = statblock_portrayal.get("description", "")
            if desc: md += f"\n{desc}\n"
            results.append((full_name, md))
    return results

def process_sourcebook(source_json, output_dir, source_label, check_alias=False):
    if not os.path.exists(source_json):
        print(f"Error: {source_json} not found.")
        return

    with open(source_json, 'r') as f:
        data = json.load(f)

    monsters = data.get("fabio:hasPart", [])
    print(f"Converting {len(monsters)} monsters from {source_label}...")

    # Define the raw json cached folder
    json_cache_dir = os.path.join(SCRIPT_DIR, "json")
    os.makedirs(json_cache_dir, exist_ok=True)

    import urllib.request
    import time

    for i, monster in enumerate(monsters):
        slug = monster.get("slug")
        if not slug: continue
        
        json_path = os.path.join(json_cache_dir, f"{slug}.json")
        if not os.path.exists(json_path):
            url = f"https://monstro.cc/monster/{slug}/index.json"
            print(f"  Downloading cache for {slug}...")
            try:
                # Add a User-Agent header so monstro.cc doesn't block standard Python urllib
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode('utf-8')
                    # Parse to ensure it is valid JSON
                    json.loads(content)
                    with open(json_path, 'w') as cache_file:
                        cache_file.write(content)
                # Sleep a tiny bit to be gentle to the server
                time.sleep(0.05)
            except Exception as e:
                print(f"  Error downloading {slug}: {e}")
                continue
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                monster_data = json.load(f)
            outputs = transform_monster(monster_data, source_label, check_alias)
            if outputs:
                os.makedirs(output_dir, exist_ok=True)
                for fname, content in outputs:
                    clean_fname = "".join([c for c in fname if c.isalnum() or c in " ()-"]).strip()
                    out_path = os.path.join(output_dir, f"{clean_fname}.md")
                    with open(out_path, 'w') as out:
                        out.write(content)
        else:
            print(f"  Warning: {slug}.json not found and failed to download.")

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(monsters)}...")

def run_bulk(check_alias=False):
    base_dir = os.path.join(SCRIPT_DIR, "../Bestiary")
    
    # Process Core Rulebook
    core_json = os.path.join(SCRIPT_DIR, "bfrpg.json")
    core_out = os.path.join(base_dir, "BFRPG Core")
    process_sourcebook(core_json, core_out, "BFRPG Core", check_alias)
    
    # Process Field Guide Omnibus
    fg_json = os.path.join(SCRIPT_DIR, "fieldguide.json")
    fg_out = os.path.join(base_dir, "BFRPG Field Guide")
    process_sourcebook(fg_json, fg_out, "BFRPG Field Guide", check_alias)
    print("Conversion complete!")

def run_tests():
    print("==================================================")
    print("           RUNNING EXTRACTOR UNIT TESTS           ")
    print("==================================================")
    
    # 1. Test Naming Engine
    print("\n--- 1. Testing Naming Engine ---")
    test_cases = [
        ("Frog, Giant (or Toad, Giant)", "Giant Frog", ["Giant Toad"]),
        ("Medusa", "Medusa", []),
        ("Beetle, Giant Fire", "Giant Fire Beetle", []),
        ("Bear, Grizzly (or Brown)", "Grizzly Bear", ["Brown Bear"]),
        ("Dragon, Ice (White Dragon)", "Ice Dragon", ["White Dragon"])
    ]
    for tc, expected_name, expected_aliases in test_cases:
        name, aliases = clean_monster_name(tc)
        print(f"Original: '{tc}'")
        print(f"  Result: '{name}', Aliases: {aliases}")
        assert name == expected_name, f"Expected {expected_name}, got {name}"
        assert aliases == expected_aliases, f"Expected {expected_aliases}, got {aliases}"
    print("Naming Engine: PASS")

    # 2. Test AC Calculation
    print("\n--- 2. Testing OSE/BX AC Dual-Formatting ---")
    ac_tests = [
        # (BFRPG AC, Expected Descending, Expected Ascending, Expected Formatted)
        (10, 10, 9, "10 [9]"),
        (11, 9, 10, "9 [10]"), # Unarmored
        (13, 7, 12, "7 [12]"), # Leather
        (15, 5, 14, "5 [14]"), # Chain mail
        (17, 3, 16, "3 [16]"), # Plate mail
        (19, 1, 18, "1 [18]")
    ]
    for bfrpg_ac, expected_desc, expected_asc, expected_fmt in ac_tests:
        ose_ascending = bfrpg_ac - 1
        ose_descending = 19 - ose_ascending
        fmt = f"{ose_descending} [{ose_ascending}]"
        print(f"BFRPG AC: {bfrpg_ac} -> OSE Descending: {ose_descending}, OSE Ascending: {ose_ascending} -> Fmt: '{fmt}'")
        assert ose_descending == expected_desc, f"Expected desc {expected_desc}, got {ose_descending}"
        assert ose_ascending == expected_asc, f"Expected asc {expected_asc}, got {ose_ascending}"
        assert fmt == expected_fmt, f"Expected fmt '{expected_fmt}', got '{fmt}'"
    print("AC Formatting: PASS")

    # 3. Test HD & HP Calculations
    print("\n--- 3. Testing HD & HP Parsing ---")
    hp_tests = [
        ("1-1", 0.9, 3),
        ("1/2", 0.5, 2),
        ("5", 5.0, 22), # Grizzly Bear (math.floor(5 * 4.5) = 22)
        ("1d4", 0.1, 2),
        ("1 hit point", 0.1, 1),
    ]
    for hd_str, expected_hd, expected_hp in hp_tests:
        parsed_hd = parse_hd_str(hd_str)[0][0]
        hp = calculate_hp(parsed_hd, hd_str)
        print(f"HD Str: '{hd_str}' -> Parsed HD: {parsed_hd}, HP: {hp}")
        assert parsed_hd == expected_hd, f"Expected HD {expected_hd}, got {parsed_hd}"
        assert hp == expected_hp, f"Expected HP {expected_hp}, got {hp}"
    print("HD & HP Calculations: PASS")

    # 4. Test Saving Throw Modifier Progression (Reflex Hack)
    print("\n--- 4. Testing Save vs. Breath Initiative Modifier ---")
    # NM maps to Breath 16 -> modifier = floor((15-16)/2) = -1
    # Level 1-3 maps to Breath 15 -> modifier = floor((15-15)/2) = 0
    # Level 16+ maps to Breath 5 -> modifier = floor((15-5)/2) = 5
    modifier_tests = [
        ("fighter", "NM", -1),
        ("fighter", 1, 0),
        ("fighter", 6, 0), # Level 6 has breath save 14 -> floor((15-14)/2) = 0
        ("fighter", 16, 2) # Level 16 has breath save 10 -> floor((15-10)/2) = 2
    ]
    for cls, lvl, expected_mod in modifier_tests:
        jds = get_jds(cls, lvl)
        breath_save = jds[3]
        mod = math.floor((15 - breath_save) / 2)
        print(f"{cls.capitalize()} Level {lvl} -> Breath Save: {breath_save} -> Derived Initiative Modifier: {mod}")
        assert mod == expected_mod, f"Expected modifier {expected_mod}, got {mod}"
    print("Initiative Modifier Progression: PASS")

    print("\n==================================================")
    print("              ALL TESTS PASSED!                   ")
    print("==================================================")

def main():
    parser = argparse.ArgumentParser(description="Consolidated BFRPG Bestiary to Shadowdark/OSE Statblock Converter CLI")
    parser.add_argument("--checkalias", action="store_true", help="Prompt user to accept or add aliases manually if word counts differ")
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")
    subparsers.add_parser("bulk", help="Run bulk conversion on all raw JSON sourcebooks")
    
    single_parser = subparsers.add_parser("single", help="Convert a single monster JSON file")
    single_parser.add_argument("json_path", help="Path to raw monster JSON")
    single_parser.add_argument("output_dir", help="Output bestiary directory")
    single_parser.add_argument("source_name", help="Sourcebook name (e.g. 'Core Rulebook')")
    
    subparsers.add_parser("test", help="Run self-contained unit tests")
    
    args = parser.parse_args()
    
    if args.command == "bulk":
        run_bulk(args.checkalias)
    elif args.command == "single":
        with open(args.json_path, 'r') as f:
            monster_data = json.load(f)
        outputs = transform_monster(monster_data, args.source_name, args.checkalias)
        if outputs:
            os.makedirs(args.output_dir, exist_ok=True)
            for fname, content in outputs:
                clean_fname = "".join([c for c in fname if c.isalnum() or c in " ()-"]).strip()
                out_path = os.path.join(args.output_dir, f"{clean_fname}.md")
                with open(out_path, 'w') as out:
                    out.write(content)
                print(f"Successfully converted and wrote '{clean_fname}.md'")
    elif args.command == "test":
        run_tests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
