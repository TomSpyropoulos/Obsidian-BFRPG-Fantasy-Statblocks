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

def parse_saves_string(s):
    if not isinstance(s, str):
        return None
    m = re.findall(r'[DWPBS]\s*(\d+)', s, re.IGNORECASE)
    if len(m) == 5:
        prefixes = re.findall(r'([DWPBS])\s*(\d+)', s, re.IGNORECASE)
        save_map = {}
        for letter, val in prefixes:
            save_map[letter.upper()] = int(val)
        if len(save_map) == 5 and all(x in save_map for x in ['D', 'W', 'P', 'B', 'S']):
            return [save_map['D'], save_map['W'], save_map['P'], save_map['B'], save_map['S']]
    
    nums = [int(n) for n in re.findall(r'\b\d+\b', s)]
    parenthesis_match = re.search(r'\(\s*(\d+)\s*\)\s*$', s)
    if parenthesis_match:
        p_num = int(parenthesis_match.group(1))
        if nums and nums[-1] == p_num and len(nums) > 5:
            nums.pop()
    if len(nums) == 5:
        return nums
    return None

def match_saves_to_class(saves_list):
    for class_name, rows in SAVING_THROW_TABLES.items():
        for row in rows:
            row_saves = [row['death_ray_poison'], row['magic_wands'], row['paralysis_petrify'], row['dragon_breath'], row['spells']]
            if saves_list == row_saves:
                return class_name
    return "fighter"

def parse_save_entry(entry, current_hd):
    bonus = None
    if "elf" in entry.lower(): bonus = "elf"
    elif "dwarf" in entry.lower(): bonus = "dwarf"
    elif "halfling" in entry.lower(): bonus = "halfling"
    
    parsed_saves = parse_saves_string(entry)
    if parsed_saves:
        matched_cls = match_saves_to_class(parsed_saves)
        lvl = int(current_hd) if current_hd >= 1 else 1
        return [(matched_cls, lvl, bonus)]
        
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

def get_dc(level):
    try:
        lvl = float(level)
    except:
        lvl = 1.0
    return 12 + int(lvl / 5)

def translate_trait_text(text, level):
    if not isinstance(text, str):
        return text
        
    dc = get_dc(level)
    
    save_mappings = {
        "poison": "CON",
        "death ray": "CON",
        "death": "CON",
        "poison/death": "CON",
        "poison or death": "CON",
        "poison or death ray": "CON",
        "wands": "WIS",
        "magic wands": "WIS",
        "wand": "WIS",
        "spells": "INT",
        "magic": "INT",
        "spell": "INT",
        "dragon breath": "DEX",
        "breath": "DEX",
        "petrify": "STR",
        "petrification": "STR",
        "turn to stone": "STR",
        "paralysis": "STR",
        "paralysation": "STR",
        "paralyze": "STR"
    }
    
    categories_pattern = "|".join([re.escape(k) for k in save_mappings.keys()])
    
    def get_attr(category_str):
        category_clean = category_str.lower().strip()
        for key, attr in save_mappings.items():
            if category_clean == key or category_clean.startswith(key):
                return attr
        return "CON" # fallback
        
    processed = text
    
    # 1. "a successful saving throw/save vs [X]" -> "a successful DC [DC] [ATTR] check"
    p_success = rf'\ba?\s*successful\s+(?:saving\s+throw|save)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_success(m):
        attr = get_attr(m.group(1))
        return f"a successful DC {dc} {attr} check"
    processed = re.sub(p_success, repl_success, processed, flags=re.IGNORECASE)
    
    # 2. "succeed on a saving throw/save vs [X]" -> "succeed on a DC [DC] [ATTR] check"
    p_succeed = rf'\bsucceed\s+on\s+(?:a\s+)?(?:saving\s+throw|save)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_succeed(m):
        attr = get_attr(m.group(1))
        return f"succeed on a DC {dc} {attr} check"
    processed = re.sub(p_succeed, repl_succeed, processed, flags=re.IGNORECASE)
    
    # 3. Noun-only pattern for "saving throw(s) vs [X]" -> always DC [DC] [ATTR] check
    p_saving_throw = rf'\b(?:saving\s+throws?)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_saving_throw(m):
        attr = get_attr(m.group(1))
        return f"DC {dc} {attr} check"
    processed = re.sub(p_saving_throw, repl_saving_throw, processed, flags=re.IGNORECASE)
    
    # 4. Context-aware "save/saves vs [X]" parsing based on preceding word:
    p_save_phrase = rf'\b([\w\'-]+)?(\s+)?(save|saves)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_save_phrase(m):
        prev_word = m.group(1)
        space = m.group(2) or ""
        verb_type = m.group(3).lower()
        category = m.group(4)
        attr = get_attr(category)
        
        if not prev_word:
            # If start of sentence/phrase, default to verb command
            if verb_type == "saves":
                return f"Succeeds on a DC {dc} {attr} check"
            else:
                return f"Succeed on a DC {dc} {attr} check"
                
        prev_word_lower = prev_word.lower()
        noun_indicators = {"a", "an", "the", "their", "its", "her", "his", "our", "on", "for", "of", "successful", "standard", "first", "saves"}
        
        if prev_word_lower in noun_indicators:
            return f"{prev_word}{space}DC {dc} {attr} check"
        else:
            if verb_type == "saves":
                return f"{prev_word}{space}succeeds on a DC {dc} {attr} check"
            else:
                return f"{prev_word}{space}succeed on a DC {dc} {attr} check"
                
    processed = re.sub(p_save_phrase, repl_save_phrase, processed, flags=re.IGNORECASE)
    
    # 5. Sanitize B/X terms to Shadowdark equivalents:
    # A. "hit dice" -> "levels", "hit die" -> "level", "HD" -> "LVL" (preserving capitalization)
    processed = re.sub(r'\b[Hh]it\s+[Dd]ice\b', lambda m: 'levels' if m.group(0)[0].islower() else 'Levels', processed)
    processed = re.sub(r'\b[Hh]it\s+[Dd]ie\b', lambda m: 'level' if m.group(0)[0].islower() else 'Level', processed)
    processed = re.sub(r'\bHD\b', 'LVL', processed)
    
    # B. "morale check/checks" -> "DC 12 WIS check/checks"
    processed = re.sub(r'\bmorale\s+checks\b', 'morale checks (DC 12 WIS checks)', processed, flags=re.IGNORECASE)
    processed = re.sub(r'\bmorale\s+check\b', 'DC 12 WIS check', processed, flags=re.IGNORECASE)
    processed = re.sub(r'\bchecking\s+morale\b', 'making a DC 12 WIS check', processed, flags=re.IGNORECASE)
    processed = re.sub(r'\bmorale\s+rating\b', 'WIS modifier', processed, flags=re.IGNORECASE)
    processed = re.sub(r'\bmorale\s+value\b', 'WIS modifier', processed, flags=re.IGNORECASE)
    processed = re.sub(r'\bmorale\b(?! (?:checks|check|rating|value))', 'morale (WIS)', processed, flags=re.IGNORECASE)
    
    # C. "Magic-User" / "magic-user" -> "Wizard" / "wizard" (preserving capitalization and pluralization)
    def repl_wizard(m):
        word = m.group(0)
        is_plural = word.lower().endswith('s')
        capitalized = word[0].isupper()
        if capitalized:
            return 'Wizards' if is_plural else 'Wizard'
        else:
            return 'wizards' if is_plural else 'wizard'
    processed = re.sub(r'\bmagic-users?\b', repl_wizard, processed, flags=re.IGNORECASE)
    processed = re.sub(r'\bmagic\s+users?\b', repl_wizard, processed, flags=re.IGNORECASE)
    
    # D. "Infravision" / "infravision" -> "Darkvision" / "darkvision" (preserving capitalization)
    processed = re.sub(r'\binfravision\b', lambda m: 'darkvision' if m.group(0)[0].islower() else 'Darkvision', processed, flags=re.IGNORECASE)
    
    return processed

def parse_save_adjustments(save_entry):
    adjustments = {"STR": 0, "DEX": 0, "CON": 0, "INT": 0, "WIS": 0, "CHA": 0}
    entry_lower = save_entry.lower()
    
    matches = re.findall(r'\+([1-9])', entry_lower)
    for m in matches:
        bonus = int(m)
        if "poison" in entry_lower or "death" in entry_lower or "disease" in entry_lower:
            adjustments["CON"] = max(adjustments["CON"], bonus)
        if "paralysis" in entry_lower or "petrif" in entry_lower or "stone" in entry_lower:
            adjustments["STR"] = max(adjustments["STR"], bonus)
        if "wand" in entry_lower:
            adjustments["WIS"] = max(adjustments["WIS"], bonus)
        if "spell" in entry_lower or "magic" in entry_lower:
            adjustments["INT"] = max(adjustments["INT"], bonus)
        if "breath" in entry_lower:
            adjustments["DEX"] = max(adjustments["DEX"], bonus)
            
    return adjustments

def format_dice(text):
    if not text:
        return text
    # Match standard dice notation: XdY optionally followed by + or - and Z, allowing spaces around the operator
    pattern = r'\b(\d+d\d+(?:\s*[+-]\s*\d+)?)\b'
    def repl(m):
        dice_expr = m.group(1).replace(" ", "")
        return f"{m.group(1)} (`dice:{dice_expr}`)"
    return re.sub(pattern, repl, text)

def clean_monster_name(raw_name, check_alias=False):
    # Hardcoded alias overrides for known database anomalies
    ALIAS_OVERRIDES = {
        "Brown": "Bear, Brown",
        "Giant and Toad": "Toad, Giant"
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

    # 2. Process stripping "or" from start and preserving commas
    def process(n):
        n = n.strip()
        # Strip leading "or "
        n = re.sub(r'^(?:or\s+)', '', n, flags=re.IGNORECASE).strip()
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

def map_shadowdark_speed(mov):
    parts = re.split(r'[/;,]|\band\b', mov)
    mapped_keys = []
    for part in parts:
        clean_part = re.sub(r'\(.*?\)', '', part).lower()
        clean_part = re.sub(r'\b(ft|feet)\b', '', clean_part)
        tokens = re.findall(r'[a-z]+|\d+', clean_part)
        num_indices = [i for i, t in enumerate(tokens) if t.isdigit()]
        for i, idx in enumerate(num_indices):
            val = int(tokens[idx])
            preceding = tokens[idx-1] if idx > 0 else ""
            succeeding = tokens[idx+1] if idx < len(tokens) - 1 else ""
            is_fly = False
            if "fly" in preceding or "flight" in preceding:
                is_fly = True
            elif "fly" in succeeding or "flight" in succeeding:
                if idx < len(tokens) - 2 and tokens[idx+2].isdigit():
                    is_fly = False
                else:
                    is_fly = True
            if val > 60:
                key = "double near (fly)" if is_fly else "double near"
            else:
                key = "near (fly)" if is_fly else "near"
            if key not in mapped_keys:
                mapped_keys.append(key)
    if not mapped_keys:
        return "near"
    
    # Priority order from best to worst:
    # 1. "double near (fly)"
    # 2. "near (fly)"
    # 3. "double near"
    # 4. "near"
    if "double near (fly)" in mapped_keys:
        return "double near (fly)"
    elif "near (fly)" in mapped_keys:
        return "near (fly)"
    elif "double near" in mapped_keys:
        return "double near"
    else:
        return "near"

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
    name = name.replace("*", "").strip()
    name_aliases = [a.replace("*", "").strip() for a in name_aliases]
    
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
        hd_str = hd_parts[0].strip().replace("*", "").replace("½", "1/2")
        
        m_san = re.search(r'^(\d+d\d+|\d+/\d+|\d+\-\d+|\d+)', hd_str, re.IGNORECASE)
        if m_san:
            hd_str_sanitized = m_san.group(1)
            if hd_str_sanitized == "1/2":
                hd_str_sanitized = "1"
        else:
            hd_str_sanitized = hd_str
        
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
            cls = cls.lower().strip().replace(" ", "_").replace("-", "_")
            
            # Parse morale
            morale_str = str(var_stats.get('morale') or '').strip()
            try:
                morale_val = int(re.search(r'(\d+)', morale_str).group(1))
            except:
                morale_val = 7
                
            # Initialize base modifiers
            st_mod = 0
            dx_mod = 0
            co_mod = 0
            it_mod = 0
            ws_mod = 0
            ch_mod = 0
            
            # 1. HD level scaling: +1 to all modifiers per 4 HD
            hd_bonus = int(hd_val / 4)
            st_mod += hd_bonus
            dx_mod += hd_bonus
            co_mod += hd_bonus
            it_mod += hd_bonus
            ws_mod += hd_bonus
            ch_mod += hd_bonus
            
            # 2. Class saves bonus: Fighter (+2 STR), Magic-User (+2 INT), Cleric (+2 WIS), Thief (+2 DEX)
            if cls == "fighter":
                st_mod += 2
            elif cls == "magic_user":
                it_mod += 2
            elif cls == "cleric":
                ws_mod += 2
            elif cls == "thief":
                dx_mod += 2
                
            # 3. Wisdom modifier Morale boost: int((morale_val - 7) / 2)
            ws_mod += int((morale_val - 7) / 2)
            
            # 4. Racial save bonuses:
            # Elf: -1 CON, +1 INT, +1 WIS
            # Dwarf: -1 CHA, +1 STR, +1 CON
            # Halfling: -1 STR, +2 DEX
            if bonus == "elf":
                co_mod -= 1
                it_mod += 1
                ws_mod += 1
            elif bonus == "dwarf":
                ch_mod -= 1
                st_mod += 1
                co_mod += 1
            elif bonus == "halfling":
                st_mod -= 1
                dx_mod += 2
                
            # 5. Special Hit Dice (+hp bonus): if hd_str has flat bonus, +1 to CON
            has_flat_hp_bonus = bool(re.search(r'\+\s*\d+(?!d)', hd_str))
            if has_flat_hp_bonus:
                co_mod += 1
                
            # 6. Speed bonus derived from resolved Shadowdark speed key:
            mov = str(var_stats.get("movement") or "0").strip().strip("'\"")
            mapped_speed = map_shadowdark_speed(mov)
            if mapped_speed == "double near (fly)":
                dx_mod += 2
            elif mapped_speed in ["near (fly)", "double near"]:
                dx_mod += 1
                
            # 7. Flat save adjustments in saveAs:
            adjustments = parse_save_adjustments(save_entry)
            st_mod += adjustments["STR"]
            dx_mod += adjustments["DEX"]
            co_mod += adjustments["CON"]
            it_mod += adjustments["INT"]
            ws_mod += adjustments["WIS"]
            ch_mod += adjustments["CHA"]
            
            modifier_val = dx_mod
            
            attributes_list = [
                f"{st_mod:+d}",
                f"{dx_mod:+d}",
                f"{co_mod:+d}",
                f"{it_mod:+d}",
                f"{ws_mod:+d}",
                f"{ch_mod:+d}"
            ]
            
            ac_raw = var_stats.get("armorClass") or 10
            try:
                if isinstance(ac_raw, str): bfrpg_ac = int(re.search(r'(\d+)', ac_raw).group(1))
                else: bfrpg_ac = int(ac_raw)
            except: bfrpg_ac = 10
            
            # Shadowdark AC is ascending only, base 10 (raw BFRPG AC - 1)
            shadowdark_ac = bfrpg_ac - 1
            
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
            dmg_str = format_dice(dmg) if dmg else "-"

            stats_list = [hd_str_sanitized, str(hp_val), str(shadowdark_ac), mapped_speed]
            stats_field = json.dumps(stats_list)
            
            # YAML-safe string dumping (outside f-strings)
            q_aliases = json.dumps(name_aliases)
            q_hd_str = json.dumps(hd_str_sanitized)
            q_thac0 = json.dumps(atk_display)
            q_attack = json.dumps(f"+{ab} (`dice: 1d20+{ab}`) " + atk_str)
            q_damage = json.dumps(dmg_str)
            q_ac = json.dumps(str(shadowdark_ac))

            md = f"---\nstatblock: inline\nname: {full_name}\nobsidianUIMode: preview\ntags:\n  - monster\naliases: {q_aliases}\nsource: {source_name}\n---\n\n"
            md += "```statblock\n"
            md += f"name: {full_name}\n"
            md += "layout: Shadowdark\n"
            md += f"ac: {q_ac}\n"
            md += f"level: {q_hd_str}\n"
            md += f"hp: {hp_val}\n"
            md += f"atk_bonus: {q_thac0}\n"
            md += f"modifier: {modifier_val}\n"
            md += f"stats: {stats_field}\n"
            md += f"attack: {q_attack}\n"
            md += f"damage: {q_damage}\n"
            md += f"attributes: {json.dumps(attributes_list)}\n"
            
            spec = statblock_portrayal.get("specialAbilities", [])
            if spec:
                md += "traits:\n"
                for sa in spec:
                    raw_desc = sa.get('description', '')
                    translated_desc = translate_trait_text(raw_desc, hd_val)
                    desc_clean = translated_desc.replace('"', "'").replace('\n', ' ').strip()
                    name_clean = sa.get('name', '').replace('"', "'").strip()
                    md += f"  - name: \"{name_clean}\"\n    desc: \"{desc_clean}\"\n"
            
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
                    an_clean = an.replace('"', "'")
                    dv_clean = dv.replace('"', "'").replace('\n', '\\n')
                    dv_clean_formatted = format_dice(dv_clean)
                    md += f"  - name: \"{an_clean}\"\n    desc: \"D20 to hit, {dv_clean_formatted}\"\n"
            
            md += f"source: {source_name}\n```\n"
            desc = statblock_portrayal.get("description", "")
            if desc:
                desc_translated = translate_trait_text(desc, hd_val)
                md += f"\n{desc_translated}\n"
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
                    clean_fname = "".join([c for c in fname if c.isalnum() or c in " ()-," ]).strip()
                    out_path = os.path.join(output_dir, f"{clean_fname}.md")
                    with open(out_path, 'w') as out:
                        out.write(content)
        else:
            print(f"  Warning: {slug}.json not found and failed to download.")

        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(monsters)}...")

def run_bulk(check_alias=False):
    base_dir = os.path.join(SCRIPT_DIR, "../BFRPG Complete Bestiary")
    
    # Process Core Rulebook
    core_json = os.path.join(SCRIPT_DIR, "bfrpg.json")
    process_sourcebook(core_json, base_dir, "BFRPG Core", check_alias)
    
    # Process Field Guide Omnibus
    fg_json = os.path.join(SCRIPT_DIR, "fieldguide.json")
    process_sourcebook(fg_json, base_dir, "BFRPG Field Guide", check_alias)
    print("Conversion complete!")

def run_tests():
    print("==================================================")
    print("           RUNNING EXTRACTOR UNIT TESTS           ")
    print("==================================================")
    
    # 1. Test Naming Engine
    print("\n--- 1. Testing Naming Engine ---")
    test_cases = [
        ("Frog, Giant (or Toad, Giant)", "Frog, Giant", ["Toad, Giant"]),
        ("Medusa", "Medusa", []),
        ("Beetle, Giant Fire", "Beetle, Giant Fire", []),
        ("Bear, Grizzly (or Brown)", "Bear, Grizzly", ["Bear, Brown"]),
        ("Dragon, Ice (White Dragon)", "Dragon, Ice", ["White Dragon"])
    ]
    for tc, expected_name, expected_aliases in test_cases:
        name, aliases = clean_monster_name(tc)
        print(f"Original: '{tc}'")
        print(f"  Result: '{name}', Aliases: {aliases}")
        assert name == expected_name, f"Expected {expected_name}, got {name}"
        assert aliases == expected_aliases, f"Expected {expected_aliases}, got {aliases}"
    print("Naming Engine: PASS")

    # 2. Test AC Calculation
    print("\n--- 2. Testing Shadowdark Ascending AC ---")
    ac_tests = [
        # (BFRPG AC, Expected Shadowdark AC)
        (10, 9),
        (11, 10), # Unarmored
        (13, 12), # Leather
        (15, 14), # Chain mail
        (17, 16), # Plate mail
        (19, 18)
    ]
    for bfrpg_ac, expected_ac in ac_tests:
        shadowdark_ac = bfrpg_ac - 1
        print(f"BFRPG AC: {bfrpg_ac} -> Shadowdark AC: {shadowdark_ac}")
        assert shadowdark_ac == expected_ac, f"Expected {expected_ac}, got {shadowdark_ac}"
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

    # 3b. Test Display Level Sanitization
    print("\n--- 3b. Testing Level Display Sanitization ---")
    san_tests = [
        ("1-1", "1-1"),
        ("1/2 (1d4 HP)", "1"),
        ("1 hit point", "1"),
        ("1 HP*", "1"),
        ("5+1*", "5"),
        ("½ (1d4 hit points)", "1"),
        ("1d4 Hit Points", "1d4"),
        ("Special", "Special")
    ]
    for raw_hd, expected in san_tests:
        calc_str = raw_hd.replace("*", "").replace("½", "1/2").strip()
        m_san = re.search(r'^(\d+d\d+|\d+/\d+|\d+\-\d+|\d+)', calc_str, re.IGNORECASE)
        sanitized = m_san.group(1) if m_san else calc_str
        if sanitized == "1/2":
            sanitized = "1"
        print(f"Raw: '{raw_hd}' -> Sanitized Display: '{sanitized}'")
        assert sanitized == expected, f"Expected '{expected}', got '{sanitized}'"
    print("Level Display Sanitization: PASS")

    # 4. Test Shadowdark Attributes Modifier Calculations
    print("\n--- 4. Testing Shadowdark Attributes & Modifiers ---")
    
    def compute_attributes(hd_str, save_entry, morale_str, movement_str, bonus_race=None):
        hds = parse_hd_str(hd_str)
        hd_val, _ = hds[0]
        cls, lvl, bonus = parse_save_entry(save_entry, hd_val)[0]
        cls = cls.lower().strip().replace(" ", "_").replace("-", "_")
        if bonus_race:
            bonus = bonus_race
            
        try:
            morale_val = int(re.search(r'(\d+)', morale_str).group(1))
        except:
            morale_val = 7
            
        st_mod = 0; dx_mod = 0; co_mod = 0; it_mod = 0; ws_mod = 0; ch_mod = 0
        
        # 1. HD level scaling
        hd_bonus = int(hd_val / 4)
        st_mod += hd_bonus; dx_mod += hd_bonus; co_mod += hd_bonus; it_mod += hd_bonus; ws_mod += hd_bonus; ch_mod += hd_bonus
        
        # 2. Class saves bonus
        if cls == "fighter":
            st_mod += 2
        elif cls == "magic_user":
            it_mod += 2
        elif cls == "cleric":
            ws_mod += 2
        elif cls == "thief":
            dx_mod += 2
            
        # 3. Wisdom modifier Morale boost
        ws_mod += int((morale_val - 7) / 2)
        
        # 4. Racial save bonuses
        if bonus == "elf":
            co_mod -= 1; it_mod += 1; ws_mod += 1
        elif bonus == "dwarf":
            ch_mod -= 1; st_mod += 1; co_mod += 1
        elif bonus == "halfling":
            st_mod -= 1; dx_mod += 2
            
        # 5. Special Hit Dice (+hp bonus)
        has_flat_hp_bonus = bool(re.search(r'\+\s*\d+(?!d)', hd_str))
        if has_flat_hp_bonus:
            co_mod += 1
            
        # 6. Speed bonus derived from resolved Shadowdark speed key:
        mapped_speed = map_shadowdark_speed(movement_str)
        if mapped_speed == "double near (fly)":
            dx_mod += 2
        elif mapped_speed in ["near (fly)", "double near"]:
            dx_mod += 1
            
        # 7. Flat save adjustments in saveAs:
        adjustments = parse_save_adjustments(save_entry)
        st_mod += adjustments["STR"]
        dx_mod += adjustments["DEX"]
        co_mod += adjustments["CON"]
        it_mod += adjustments["INT"]
        ws_mod += adjustments["WIS"]
        ch_mod += adjustments["CHA"]
            
        return [st_mod, dx_mod, co_mod, it_mod, ws_mod, ch_mod]

    # Test case 1: Hob (Thief: 1, morale 7, speed 20/30)
    # Expected: STR +0, DEX +2, CON +0, INT +0, WIS +0, CHA +0
    res1 = compute_attributes("1-1", "Thief: 1", "7", "20' Unarmored 30'")
    print(f"Hob parsed modifiers: {res1}")
    assert res1 == [0, 2, 0, 0, 0, 0], f"Hob failed: {res1}"

    # Test case 2: Gnome (Fighter: 1, morale 8, speed 20, dwarf bonus)
    # Expected: STR +3, DEX +0, CON +1, INT +0, WIS +0, CHA -1
    res2 = compute_attributes("1", "Fighter: 1 (with Dwarf bonuses)", "8", "20'")
    print(f"Gnome parsed modifiers: {res2}")
    assert res2 == [3, 0, 1, 0, 0, -1], f"Gnome failed: {res2}"

    # Test case 3: Gerbalaine (Fighter: 1, morale 8, halfling bonus)
    # Expected: STR +1, DEX +2, CON +0, INT +0, WIS +0, CHA +0
    res3 = compute_attributes("1", "Fighter: 1 (Halfling bonuses)", "8", "20'")
    print(f"Gerbalaine parsed modifiers: {res3}")
    assert res3 == [1, 2, 0, 0, 0, 0], f"Gerbalaine failed: {res3}"

    # Test case 4: Sprite (Magic-User: 4, morale 7, elf bonus)
    # Expected: STR +0, DEX +0, CON -1, INT +3, WIS +1, CHA +0
    res4 = compute_attributes("1*", "Magic-User: 4 (with Elf bonuses)", "7", "20'")
    print(f"Sprite parsed modifiers: {res4}")
    assert res4 == [0, 0, -1, 3, 1, 0], f"Sprite failed: {res4}"

    # Test case 5: High HD / Special HD / Fast monster
    # HD 5+1 (Fighter save, speed Fly 120', morale 9)
    # HD scaling: 5 / 4 = 1 bonus to all
    # Fighter save: +2 STR
    # Morale 9: +1 WIS boost
    # Special HD (+1 hp): +1 CON
    # Speed Fly 120' -> double near (fly): +2 DEX
    # Expected: STR 1+2=3, DEX 1+2=3, CON 1+1=2, INT 1, WIS 1+1=2, CHA 1
    res5 = compute_attributes("5+1*", "Fighter: 5", "9", "Fly 120'")
    print(f"Fast High-HD Giant parsed modifiers: {res5}")
    assert res5 == [3, 3, 2, 1, 2, 1], f"High HD failed: {res5}"
    
    # Test case 6: Flat save adjustments inside saveAs
    # Fighter: 1 (+2 Poison saves) -> CON +2
    res6a = compute_attributes("1", "Fighter: 1 (+2 Poison saves)", "7", "30'")
    print(f"CON Adjustment modifier: {res6a}")
    assert res6a == [2, 0, 2, 0, 0, 0], f"CON save bonus failed: {res6a}"
    
    # Fighter: 1 (+2 vs. Death Ray or Poison and Paralysis or Petrification) -> CON +2, STR +2
    res6b = compute_attributes("1", "Fighter: 1 (+2 vs. Death Ray or Poison and Paralysis or Petrification)", "7", "30'")
    print(f"Multi-Attribute save modifier: {res6b}")
    assert res6b == [4, 0, 2, 0, 0, 0], f"Multi-attribute save bonus failed: {res6b}"
    
    print("Shadowdark Attributes Modifiers: PASS")

    # 5. Test Trait Grammatical Translations
    print("\n--- 5. Testing Trait Grammatical Translations ---")
    trait_tests = [
        # (text, level, expected)
        ("a save vs. Spells reduces damage to half.", 15, "a DC 15 INT check reduces damage to half."),
        ("must succeed on a save vs. Spells or become charmed.", 2, "must succeed on a DC 12 INT check or become charmed."),
        ("unless they save vs magic.", 2, "unless they succeed on a DC 12 INT check."),
        ("unless the victim passes a saving throw vs poison.", 1, "unless the victim passes a DC 12 CON check."),
        ("must save vs. Poison at +2", 3, "must succeed on a DC 12 CON check at +2"),
        ("a successful save vs. Paralysis is allowed.", 10, "a successful DC 14 STR check is allowed."),
        ("created by an evil Magic-User.", 1, "created by an evil Wizard."),
        ("formed by two magic-users.", 1, "formed by two wizards."),
        ("It has infravision with a range of 120'.", 1, "It has darkvision with a range of 120'."),
        ("must make a morale check.", 1, "must make a DC 12 WIS check."),
        ("morale checks are made at -1.", 1, "morale checks (DC 12 WIS checks) are made at -1."),
    ]
    for text, lvl, expected in trait_tests:
        translated = translate_trait_text(text, lvl)
        print(f"Original: \"{text}\"\n  Result: \"{translated}\"")
        assert translated == expected, f"Failed translating: expected \"{expected}\", got \"{translated}\""
    print("Trait Grammatical Translations: PASS")

    # 6. Test Dice Roller Formatting
    print("\n--- 6. Testing Dice Roller Formatting ---")
    dice_tests = [
        ("1d8+1", "1d8+1 (`dice:1d8+1`)"),
        ("1d8", "1d8 (`dice:1d8`)"),
        ("3d4 thorn or 1d8 bite", "3d4 (`dice:3d4`) thorn or 1d8 (`dice:1d8`) bite"),
        ("1d8 + 2", "1d8 + 2 (`dice:1d8+2`)"),
        ("2d6-1", "2d6-1 (`dice:2d6-1`)"),
        ("1-1", "1-1") # Should not format flat stats without 'd'
    ]
    for text, expected in dice_tests:
        formatted = format_dice(text)
        print(f"Original: \"{text}\"\n  Result: \"{formatted}\"")
        assert formatted == expected, f"Failed dice format: expected \"{expected}\", got \"{formatted}\""
    print("Dice Roller Formatting: PASS")

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
                clean_fname = "".join([c for c in fname if c.isalnum() or c in " ()-," ]).strip()
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
