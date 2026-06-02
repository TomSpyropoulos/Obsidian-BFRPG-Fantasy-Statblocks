import os
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(SCRIPT_DIR, "json")

SAVE_MAPPINGS = {
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
    "paralysis": "STR",  # We can show STR or CON. Let's map paralysis to STR here to show petrify/paralyze together, or let the user choose.
    "paralysation": "STR",
    "paralyze": "STR"
}

def get_dc(level, scale_factor=5):
    try:
        lvl = float(level)
    except:
        lvl = 1.0
    return 12 + int(lvl / scale_factor)

def translate_trait_text(text, level, dc_scale=5):
    dc = get_dc(level, dc_scale)
    
    # We want to replace B/X style saving throw terms with Shadowdark checks grammatically.
    categories_pattern = "|".join([re.escape(k) for k in SAVE_MAPPINGS.keys()])
    
    def get_attr(category_str):
        category_clean = category_str.lower().strip()
        for key, attr in SAVE_MAPPINGS.items():
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
    
    # 3. "must save vs [X]" or "must make a saving throw vs [X]" -> "must succeed on a DC [DC] [ATTR] check"
    p_must = rf'\bmust\s+(?:make\s+(?:a\s+)?saving\s+throw|save)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_must(m):
        attr = get_attr(m.group(1))
        return f"must succeed on a DC {dc} {attr} check"
    processed = re.sub(p_must, repl_must, processed, flags=re.IGNORECASE)
    
    # 4. Verb/action form: "unless/if/or/to they/creatures save/saves/make a save vs [X]" -> "succeed on a DC [DC] [ATTR] check"
    # Matches: "unless they save vs magic", "if a creature saves vs spells", "or save vs poison", "to save vs wands"
    p_verb = rf'\b(unless|if|or|to)\s+([\w\s]{0,25}?\b)\s*(?:save|saves|make\s+a\s+save)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_verb(m):
        attr = get_attr(m.group(3))
        conjunction = m.group(1)
        subject = m.group(2)
        # Reconstruct: conjunction + subject + "succeed on a DC [DC] [ATTR] check"
        subject_space = " " if subject else ""
        return f"{conjunction} {subject}{subject_space}succeed on a DC {dc} {attr} check"
    processed = re.sub(p_verb, repl_verb, processed, flags=re.IGNORECASE)
    
    # 5. General noun cases: "saving throw/save/saving throws/saves vs [X]" -> "DC [DC] [ATTR] check"
    p_general = rf'\b(?:saving\s+throws?|saves?)\s+(?:vs\.?|against)\s+({categories_pattern})\b'
    def repl_general(m):
        attr = get_attr(m.group(1))
        return f"DC {dc} {attr} check"
    processed = re.sub(p_general, repl_general, processed, flags=re.IGNORECASE)
    
    return processed

def main():
    test_monsters = [
        "Gargoyle", 
        "Giant Rat", 
        "Giant, Storm", 
        "Golem, Stone*", 
        "Hellhound", 
        "Harpy", 
        "Lizard, Monitor", 
        "Monitor Lizard"
    ]
    
    found_monsters = []
    
    for filename in os.listdir(CACHE_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(CACHE_DIR, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        name = data.get("schema:name", "Unknown")
        clean_name = name.replace("*", "").strip()
        
        if any(t_name.lower() in clean_name.lower() for t_name in test_monsters):
            found_monsters.append(data)
            
    print("=== SCRIPT PREVIEW OF TRAIT SAVING THROW TRANSLATIONS ===")
    print("Using DC scaling formula: DC = 12 + Level / 5")
    print("-" * 80)
    
    for monster in found_monsters[:15]:
        name = monster.get("schema:name", "Unknown")
        portrayals = monster.get("fabio:hasPortrayal", [])
        for p in portrayals:
            stats = p.get("stats")
            if not stats: continue
            
            hd_str = str(stats.get("hitDice", "1"))
            m = re.search(r"^(\d+)", hd_str)
            level = int(m.group(1)) if m else 1
            
            spec = p.get("specialAbilities")
            if not spec: continue
            
            has_relevant_traits = False
            for sa in spec:
                desc = sa.get("description", "")
                if any(w in desc.lower() for w in ["save vs", "saves vs", "saving throw", "save against"]):
                    has_relevant_traits = True
                    break
            
            if not has_relevant_traits:
                continue
                
            print(f"Monster: {name} (Level/HD: {hd_str} -> Level {level})")
            print(f"Derived DCs: /5 scale -> DC {get_dc(level, 5)} | /4 scale -> DC {get_dc(level, 4)}")
            print()
            
            for sa in spec:
                desc = sa.get("description", "")
                if not any(w in desc.lower() for w in ["save vs", "saves vs", "saving throw", "save against"]):
                    continue
                    
                print(f"  Trait: '{sa.get('name')}'")
                print("    [BEFORE]:")
                print(f"      \"{desc}\"")
                print("    [AFTER (/5 scaling)]:")
                translated_5 = translate_trait_text(desc, level, dc_scale=5)
                print(f"      \"{translated_5}\"")
                print("    [AFTER (/4 scaling)]:")
                translated_4 = translate_trait_text(desc, level, dc_scale=4)
                print(f"      \"{translated_4}\"")
                print()
            print("-" * 80)

if __name__ == "__main__":
    main()
