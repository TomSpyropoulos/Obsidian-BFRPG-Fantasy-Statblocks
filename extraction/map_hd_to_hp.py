import json
import os
import re
import math
import ast

def parse_hd(hd_str):
    # Handle dictionary-style strings
    if hd_str.startswith('{'):
        try:
            d = ast.literal_eval(hd_str)
            all_hds = []
            for key, val in d.items():
                parsed = parse_hd(val)
                # parsed is a list of (float, str)
                for h_val, h_suffix in parsed:
                    all_hds.append((h_val, f" ({key}){h_suffix}"))
            return all_hds
        except:
            pass

    # Normalize for calculation
    calc_str = hd_str.replace("*", "").strip()
    
    # Handle "or" ranges
    if " or " in calc_str.lower() or "," in calc_str:
        parts = re.findall(r'(\d+)', calc_str)
        if parts:
            return [(float(p), "") for p in parts]

    # Handle range like "1 to 4" or hyphen/en-dash range
    if (" to " in calc_str) or (("-" in calc_str or "–" in calc_str) and calc_str != "1-1" and "hp" not in calc_str.lower()):
        range_match = re.search(r'(\d+)\s*([-–]|to)\s*(\d+)', calc_str)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(3))
            return [(float(i), "") for i in range(start, end + 1)]

    # Half HD
    if calc_str in ["1/2", "½", "0.5"]:
        return [(0.5, "")]
    
    # 1-1 format
    if calc_str == "1-1":
        return [(0.9, "")] 

    # 1d4 per MU level fix
    if "per mu level" in calc_str.lower():
        return [(0.1, "")]

    # Single number or addition
    m = re.search(r'^(\d+)', calc_str)
    if m:
        return [(float(m.group(1)), "")]
    
    # Check for "1 Hit Point"
    if "1 hit point" in calc_str.lower() or "1 hp" in calc_str.lower():
        return [(0.1, "")]
        
    return [(1.0, "")]

def calculate_hp(hd_val, hd_str):
    hd_lower = hd_str.lower()
    
    # Specific overrides first
    if hd_lower == "special":
        return "Special"
    if "1 hit point" in hd_lower or "1 hp" in hd_lower or "1hp" in hd_lower:
        # Check if there is an addition like "1hp + 1"
        bonus = 0
        flat_matches = re.findall(r'\+\s*(\d+)', hd_str)
        for fm in flat_matches:
            bonus += int(fm)
        return 1 + bonus
        
    if "1-2 hp" in hd_lower:
        return 2
    if "per mu level" in hd_lower:
        return 2
    
    # Handle d4/d6 averages specifically for small creatures
    if "1d4" in hd_lower:
        bonus = 0
        flat_matches = re.findall(r'\+\s*(\d+)', hd_str)
        for fm in flat_matches:
            bonus += int(fm)
        return 2 + bonus
    if "1d6" in hd_lower:
        bonus = 0
        flat_matches = re.findall(r'\+\s*(\d+)', hd_str)
        for fm in flat_matches:
            bonus += int(fm)
        return 3 + bonus

    if hd_val == 0.9: # 1-1
        return 3
    if hd_val == 0.5:
        return 2
    
    # Base calculation
    if hd_val < 0.5: hp_val = 1
    else: hp_val = math.floor(hd_val * 4.5)
    
    # Handle bonuses for standard HD
    bonus = 0
    flat_matches = re.findall(r'\+\s*(\d+)(?!d)', hd_str)
    for fm in flat_matches:
        bonus += int(fm)
    
    if "+1d" in hd_lower or " + 1d" in hd_lower:
        bonus += 2
        
    hp_val += bonus
    if hp_val < 1: hp_val = 1
    
    # Specific parens override
    hp_match = re.search(r'\((\d+)\s*hp\)', hd_lower)
    if hp_match:
        hp_val = int(hp_match.group(1))
            
    return hp_val

def generate_mapping():
    unique_hd_entries = set()
    for filename in ["formats/core_hit_dice_format.md", "formats/field_guide_hit_dice_format.md"]:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                for line in f:
                    entry = line.strip()
                    if entry: unique_hd_entries.add(entry)
    
    mapping = []
    for entry in sorted(list(unique_hd_entries)):
        hds_with_variants = parse_hd(entry)
        results = []
        for h, var in hds_with_variants:
            hp = calculate_hp(h, entry)
            results.append(str(hp))
        
        # Remove duplicates from results while preserving order
        seen = set()
        unique_results = []
        for r in results:
            if r not in seen:
                unique_results.append(r)
                seen.add(r)
                
        mapping.append(f"{entry} -> {', '.join(unique_results)}")
    
    with open("formats/hd_hp_mapping.md", "w") as f:
        f.write("\n".join(mapping))
    print("Mapping generated in formats/hd_hp_mapping.md")

if __name__ == "__main__":
    generate_mapping()

if __name__ == "__main__":
    generate_mapping()
