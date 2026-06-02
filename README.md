[>>> SHADOWDARK VERSION HERE <<<](https://github.com/TomSpyropoulos/Obsidian-BFRPG-Fantasy-Statblocks/tree/shadowdark)

# BFRPG Obsidian Bestiary

This repository contains a comprehensive collection of monster statblocks for the **Basic Fantasy Role-Playing Game (BFRPG)**, specifically formatted for use with the [Obsidian TTRPG Statblocks](https://plugins.javalent.com/statblocks) plugin.

## Features (OSE/BX Compatible Edition)

* **Obsidian Ready:** Formatted in Markdown with YAML frontmatter compatible with TTRPG Statblocks.
* **OSE/BX Compatible Stats:**
    * **Dual AC Formatting:** Features OSE-compatible dual AC format displayed as `descending [ascending]` (e.g., `6 [13]`), automatically calculated using standard base-11 BFRPG AC with (+1/-1) offsets.
    * **Attack Bonus:** Uses standard BFRPG/OSE attack bonus (THAC0).
* **Naming & Formatting:** Standardized names preserved with OSR-style comma conventions (e.g., "Beetle, Giant Fire") for proper catalog organization, while clean formatting strips special/ability asterisks.
* **Automatic Aliases:** Alternative names found in parentheses are moved to the YAML `aliases` field for better searchability.
* **Consolidated Stats:** Core vitals are provided in a clean list field: `stats: [HD, HP, AC, ATK]`.
* **Saves in Statblock:** Full saving throw arrays included (mapped from BFRPG tables, including racial bonuses).
* **Calculated Initiative:** Includes a `modifier:` field representing an initiative modifier calculated from the monster's saving throws (specifically `(15 - Breath Save) / 2`) for use with the optional individual initiative rule or the Initiative Tracker plugin.
* **Sanitized Layout:** Descriptions, traits, and movement values are sanitized to prevent YAML parsing errors and preserve formatting.

## Installation

1. Ensure you have the **Fantasy Statblocks** (formerly TTRPG Statblocks) plugin installed in your Obsidian vault.
2. Download the bestiary folders from this branch.
3. Place the **BFRPG Complete Bestiary** folder (containing `BFRPG Core` and `BFRPG Field Guide`) into your Obsidian vault.
4. Import the provided `BFRPG.json` layout.
5. Activate "Automatically Parse Frontmatter for Creatures" in settings.
6. Point the plugin to the Bestiary folder for faster indexing.

## Caveats

The statblocks were generated programmaticaly with the help of an AI agent, so some errors are almost certain. I haven't checked each monster, but most of them should be fine.

I also removed some dice parsing from some fields due to non standard text structure from the source. It would take too much time to go through each field and map out edge cases to make everything rollable.

## Attribution & Legal

This project is a derivative work based on the Basic Fantasy Role-Playing Game.

### Original Sources

* **Basic Fantasy Role-Playing Game Core Rules**: Copyright © 2006-2023 Chris Gonnerman.
* **Basic Fantasy Field Guide Omnibus**: Copyright © 2010-2025 Chris Gonnerman, R. Kevin Smoot, James Lemon, Matt Sluis, and Contributors.
* **Data Source**: Monster statistics were sourced via [Monstro.cc](https://monstro.cc), which extracts data from the [Basic Fantasy SRD](https://www.basicfantasy.org/srd/).

### Modifications

The original text has been reformatted into Markdown and YAML structures to function within the Obsidian MD ecosystem. No mechanical changes have been made to the statistics.

## License

This work is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** license.

To view a copy of this license, visit [http://creativecommons.org/licenses/by-sa/4.0/](http://creativecommons.org/licenses/by-sa/4.0/).

**Note:** Under the ShareAlike provision, if you remix, transform, or build upon this material, you must distribute your contributions under the same license as the original.
