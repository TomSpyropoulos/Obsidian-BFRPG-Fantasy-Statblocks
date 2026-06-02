import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(SCRIPT_DIR, "json")

def main():
    if not os.path.exists(CACHE_DIR):
        print("No cache directory found")
        return
        
    save_as_with_vs = set()
    traits_with_saves = []
    
    for filename in os.listdir(CACHE_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(CACHE_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            monster_name = data.get("schema:name", "Unknown")
            slug = data.get("slug")
            
            portrayals = data.get("fabio:hasPortrayal", [])
            for p in portrayals:
                stats = p.get("stats")
                if not stats:
                    continue
                    
                # 1. Check saveAs
                save_entries = []
                if "saveAs" in stats:
                    save_entries.append(str(stats["saveAs"]))
                variants = stats.get("variants", {})
                if variants:
                    for var_stats in variants.values():
                        if "saveAs" in var_stats:
                            save_entries.append(str(var_stats["saveAs"]))
                            
                for entry in save_entries:
                    if any(w in entry.lower() for w in ["vs", "+", "save", "bonus"]):
                        save_as_with_vs.add(entry)
                        
                # 2. Check specialAbilities (traits)
                spec = p.get("specialAbilities", [])
                if spec:
                    for sa in spec:
                        name = sa.get("name", "")
                        desc = sa.get("description", "")
                        combined = f"{name} {desc}".lower()
                        
                        # Match common saving throw phrases in traits
                        if any(w in combined for w in ["saving throw", "save vs", "saves vs", "+2 vs", "+3 vs", "+4 vs", "+5 vs", "save vs."]):
                            traits_with_saves.append({
                                "monster": monster_name,
                                "slug": slug,
                                "source": p.get("dc:source"),
                                "trait_name": name,
                                "trait_desc": desc
                            })
                            
        except Exception as e:
            pass
            
    print(f"=== UNIQUE saveAs ENTRIES CONTAINING ADJUSTMENTS: {len(save_as_with_vs)} ===")
    for entry in sorted(list(save_as_with_vs)):
        print(f" - '{entry}'")
        
    print(f"\n=== TRAITS (specialAbilities) CONTAINING ADJUSTMENTS: {len(traits_with_saves)} ===")
    for idx, t in enumerate(traits_with_saves[:60], 1):
        print(f"{idx}. {t['monster']} ({t['source']}) -> Trait: '{t['trait_name']}'")
        print(f"   Desc: \"{t['trait_desc']}\"")
        print()

if __name__ == "__main__":
    main()
