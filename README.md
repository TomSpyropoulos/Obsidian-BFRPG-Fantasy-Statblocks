# BFRPG Obsidian Bestiary

This repository contains a comprehensive collection of monster statblocks for the **Basic Fantasy Role-Playing Game (BFRPG)**, specifically formatted for use with the [Obsidian TTRPG Statblocks](https://plugins.javalent.com/statblocks) plugin.

## Features

* **Obsidian Ready:** Formatted in Markdown with YAML frontmatter compatible with TTRPG Statblocks.
* **Descending AC:** Computed descending AC and THAC0 and formatted them like OSE statblocks (ascending in []).
* **Saves in statblock:** No reference to Core Rulebook Save Tables (like "Save As Fighter: 4").
* **Custom Layouts:** Two layouts are provided for Fantasy Statblocks, `BFRPG.json` which contains just the statblock layout and is compatible with ITS Theme and `BFRPG_Styled.json` which is the same but with some extra styling (dark mode) for the default Obsidian themes.

## Installation

1. Ensure you have the **TTRPG Statblocks** plugin installed in your Obsidian vault.
2. Download the bestiary files from this repository.
3. Place the Bestiary into your Obsidian vault.
4. Import the `.json` layout you want to use.
5. Activate "Automatically Parse Frontmatter for Creatures" in Fantasy Statblocks settings.
6. Point Fantasy Statblocks to the Bestiary Folder (this ensures faster startup since files are indexed each time you open obsidian)

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