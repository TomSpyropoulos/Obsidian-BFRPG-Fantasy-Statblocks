import re

def clean_name(raw_name):
    # 1. Handle parentheses
    aliases = []
    main_name = raw_name
    match = re.search(r'\((.*?)\)', raw_name)
    if match:
        alias_raw = match.group(1)
        main_name = raw_name.replace(match.group(0), "").strip()
        
        # Strip "or " or " or " from alias
        alias_raw = re.sub(r'^\s*or\s+', '', alias_raw, flags=re.IGNORECASE)
        alias_raw = re.sub(r'\s+or\s+', ' ', alias_raw, flags=re.IGNORECASE).strip()
        aliases.append(alias_raw)

    # 2. Reversal logic for commas
    def process(n):
        n = n.strip()
        # Strip "or " from main name too just in case
        n = re.sub(r'^\s*or\s+', '', n, flags=re.IGNORECASE).strip()
        parts = [p.strip() for p in n.split(',')]
        if len(parts) > 1:
            return " ".join(reversed(parts))
        return n

    final_name = process(main_name)
    final_aliases = [process(a) for n in aliases for a in re.split(r'\s+or\s+', n, flags=re.IGNORECASE)]
    
    return final_name, final_aliases

test_cases = [
    "Frog, Giant (or Toad, Giant)",
    "Medusa",
    "Beetle, Giant Fire",
    "Bear, Grizzly (or Brown)",
    "Dragon, Ice (White Dragon)"
]

for tc in test_cases:
    name, aliases = clean_name(tc)
    print(f"Original: {tc}")
    print(f"  Name: {name}")
    print(f"  Aliases: {aliases}")
    print("-" * 20)
