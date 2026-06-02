import os
import json
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(SCRIPT_DIR, "json")

def main():
    if not os.path.exists(CACHE_DIR):
        print("No cache directory found")
        return
        
    # Match patterns of saving throws
    # Look for patterns like:
    # "save vs. [word]"
    # "save vs [word]"
    # "saves vs. [word]"
    # "saves vs [word]"
    # "saving throw vs [word]"
    # "saving throw vs. [word]"
    # "saving throws vs [word]"
    # "saving throws vs. [word]"
    # "save against [word]"
    # "saving throw against [word]"
    
    save_patterns = [
        r'\bsave\s+vs\.?\s+([A-Za-z0-9_ -]+?)(?=\b(?:or|and|to|with|for|after|\.|\,|$))',
        r'\bsaves\s+vs\.?\s+([A-Za-z0-9_ -]+?)(?=\b(?:or|and|to|with|for|after|\.|\,|$))',
        r'\bsaving\s+throw\s+vs\.?\s+([A-Za-z0-9_ -]+?)(?=\b(?:or|and|to|with|for|after|\.|\,|$))',
        r'\bsaving\s+throws\s+vs\.?\s+([A-Za-z0-9_ -]+?)(?=\b(?:or|and|to|with|for|after|\.|\,|$))',
        r'\bsave\s+against\s+([A-Za-z0-9_ -]+?)(?=\b(?:or|and|to|with|for|after|\.|\,|$))',
        r'\bsaving\s+throw\s+against\s+([A-Za-z0-9_ -]+?)(?=\b(?:or|and|to|with|for|after|\.|\,|$))'
    ]
    
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in save_patterns]
    
    unique_matches = {}
    examples = {}
    
    for filename in os.listdir(CACHE_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(CACHE_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            monster_name = data.get("schema:name", "Unknown")
            portrayals = data.get("fabio:hasPortrayal", [])
            for p in portrayals:
                spec = p.get("specialAbilities", [])
                for sa in spec:
                    desc = sa.get("description", "")
                    name = sa.get("name", "")
                    
                    for pattern in compiled_patterns:
                        for match in pattern.finditer(desc):
                            full_phrase = match.group(0).strip()
                            target = match.group(1).strip()
                            # Clean up target (remove trailing punctuation or common filler words)
                            target_clean = re.sub(r'\s+(?:a|an|the|this|any)\b', '', target, flags=re.IGNORECASE)
                            target_clean = target_clean.strip()
                            
                            key = target_clean.lower()
                            if key not in unique_matches:
                                unique_matches[key] = 0
                                examples[key] = []
                            unique_matches[key] += 1
                            if len(examples[key]) < 3:
                                examples[key].append({
                                    "monster": monster_name,
                                    "trait": name,
                                    "phrase": full_phrase,
                                    "sentence": desc
                                })
        except Exception as e:
            pass
            
    print("=== UNIQUE 'SAVE VS' TARGETS IN TRAIT DESCRIPTIONS ===")
    sorted_targets = sorted(unique_matches.items(), key=lambda x: x[1], reverse=True)
    for target, count in sorted_targets:
        print(f"Target: '{target}' (Found {count} times)")
        print("  Examples:")
        for ex in examples[target]:
            # Print a snippet of the sentence
            phrase_idx = ex["sentence"].lower().find(ex["phrase"].lower())
            start = max(0, phrase_idx - 40)
            end = min(len(ex["sentence"]), phrase_idx + len(ex["phrase"]) + 60)
            snippet = ex["sentence"][start:end].replace('\n', ' ').strip()
            print(f"   - {ex['monster']} ({ex['trait']}): ...{snippet}...")
        print("-" * 50)

if __name__ == "__main__":
    main()
