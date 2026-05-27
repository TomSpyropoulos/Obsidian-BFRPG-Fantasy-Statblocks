# BFRPG Bestiary Extraction Toolset

This directory contains the tools and raw data used to transform raw BFRPG JSON-LD databases into clean, Obsidian-ready Markdown statblocks for old-school play (fully compatible with the Obsidian Fantasy Statblocks plugin).

## Directory Structure

* **`convert.py`**: The fully self-contained, single-file Python CLI tool. Handles unit tests, single-monster conversion, and bulk bestiary regeneration.
* **`bfrpg.json`**: The raw sourcebook JSON database for the *Basic Fantasy RPG Core Rulebook*.
* **`fieldguide.json`**: The raw sourcebook JSON database for the *Basic Fantasy Field Guide Omnibus*.
* **`json/`**: Git-ignored cached individual monster JSONs used during bulk generation.

---

## How to Use the CLI

All conversion and testing commands are unified under `convert.py`.

### 1. Run Unit Tests
Verifies the naming engine, AC calculations, HD/HP parsing, and initiative modifiers:
```bash
python3 convert.py test
```

### 2. Run Bulk Bestiary Conversion
Regenerates all Markdown monster statblocks inside `../Basic Fantasy RPG Bestiary/Core Rulebook` and `../Basic Fantasy RPG Bestiary/Field Guide Omnibus` using the raw sourcebook JSONs:
```bash
python3 convert.py bulk
```

### 3. Convert a Single Monster JSON
Converts a single cached monster JSON file:
```bash
python3 convert.py single json/aboleth.json "../Basic Fantasy RPG Bestiary/Field Guide Omnibus" "Field Guide Omnibus"
```

---

## Core Calculations & Rulesets

### 1. Initiative Modifier (B/X "Reflex" Hack)
In classic B/X and OSE, monsters do not have individual attribute scores like Dexterity. To derive a functional individual initiative modifier for d20-based systems (like *Shadowdark*), the CLI uses the monster's **Save vs. Dragon Breath** as a proxy for reflexes:
$$\text{Initiative Modifier} = \left\lfloor \frac{15 - \text{Save vs. Dragon Breath}}{2} \right\rfloor$$

For standard Fighter progression, this scales beautifully from **-1** (Normal Man) up to **+5** (Level 16+), mirroring the classic ability score modifier range.

### 2. Dual AC Formatting: `descending [ascending]`
Classic old-school games (B/X, OSE) utilize both descending and ascending AC scales. To support both playstyles seamlessly, the AC in statblocks is generated in the `descending [ascending]` format (e.g., `"3 [16]"` for Plate Mail):
1. **Ascending OSE AC**: Derived from standard BFRPG ascending AC (which uses a base-11 unarmored standard) by adjusting it to B/X's base-10 standard:
   $$\text{OSE Ascending AC} = \text{BFRPG AC} - 1$$
2. **Descending OSE AC**: Calculated using the classic B/X formula:
   $$\text{OSE Descending AC} = 19 - \text{OSE Ascending AC}$$
3. **Format**: Combined into a single YAML-safe string, e.g., `"6 [13]"`. This formatted value is populated in both the YAML `ac:` property and as the third entry of the `stats` field (e.g., `stats: ["5", "22", "6 [13]", "+5"]`).
