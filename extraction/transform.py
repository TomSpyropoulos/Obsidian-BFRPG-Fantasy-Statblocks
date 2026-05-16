import json
import re
import sys
import os
import math

# Load all tables
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

ATTACK_BONUS_TABLE = load_json('monster_attack_bonus.json')['monster_attack_bonus_table']
SAVING_THROW_TABLES = load_json('saving_throws.json')['saving_throw_tables']

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
    m = re.search(r'^(\d+)', calc_str)
    if m: return [(float(m.group(1)), "")]
    if "1 hit point" in calc_str.lower() or "1 hp" in calc_str.lower() or "1d4" in calc_str.lower():
        return [(0.1, "")]
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

def clean_monster_name(raw_name):
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
    final_aliases = [process(a) for a in aliases]
    
    return final_name, final_aliases

def transform_monster(monster_data, source_name="BFRPG"):
    portrayals = monster_data.get("fabio:hasPortrayal", [])
    statblock_portrayal = None
    for p in portrayals:
        if "stats" in p and p["stats"] is not None:
            statblock_portrayal = p
            break
    if not statblock_portrayal: return []

    stats = statblock_portrayal.get("stats", {})
    raw_name = monster_data.get("schema:name", "Unknown")
    name, name_aliases = clean_monster_name(raw_name)
    
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
            
            # Shadowdark AC = Ascending BFRPG - 1
            ac_val = bfrpg_ac - 1
            
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

            stats_list = [hd_str, str(hp_val), str(ac_val), atk_display]
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

            md = f"---\nstatblock: inline\nname: {full_name}\nobsidianUIMode: preview\ntags:\n  - monster\naliases: {q_aliases}\nsource: {source_name}\n---\n\n"
            md += "```statblock\n"
            md += f"name: {full_name}\n"
            md += "layout: BFRPG\n"
            md += f"subtype: {source_name}\n"
            md += f"ac: {ac_val}\n"
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

if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(1)
    json_path = sys.argv[1]; output_dir = sys.argv[2]
    source_name = sys.argv[3] if len(sys.argv) > 3 else "BFRPG"
    with open(json_path, 'r') as f: data = json.load(f)
    outputs = transform_monster(data, source_name)
    if outputs:
        os.makedirs(output_dir, exist_ok=True)
        for fname, content in outputs:
            clean_fname = "".join([c for c in fname if c.isalnum() or c in " ()-"]).strip()
            with open(os.path.join(output_dir, f"{clean_fname}.md"), 'w') as out: out.write(content)
