# FNF/SM converter (Dance Double Support)

This is a modified fork of [the original repo](https://github.com/shockdude/fnf-to-sm) which adds Dance Double support instead of Dance Single charts.

Roughly convert Friday Night Funkin charts (.json) to doubles simfiles (.sm) for StepMania \
Or convert StepMania simfiles to FNF charts. \
Very WIP but it works, kinda.

Usage: Drag-and-drop the FNF .json chart, or a StepMania .sm simfile, onto `fnf-to-sm.exe` \
Or use the command line: `python fnf-to-sm.py [chart_file]`

For FNF-to-SM, if you input the Normal difficulty .json, and have the \
easy & hard .jsons in the same folder, then FNF-to-SM will output a single .sm with all 3 difficulties.

This version of SM-to-FNF currently only supports Hard Difficulty Dance Double .sm files conversion. \
The output will use the same name of your chart with the "-hard" suffix, "chart-hard.json", which is meant to replace your song on the Hard difficulty.

By default player1 (ie. Boyfriend), player2 (ie. Dad), chart speed and stage (Kade Engine only) are converted from their .json, \
incase you made a song within FNF and wanted to edit it with external tools (such as ArrowVortex). \
However, if you are making a .sm simfile from scratch you need to assign them. \
In order to assign them, you have to go into the simfile's Properties and fill in the next properties: \
**Artist** to determine the **Player 1** (for example, bf - being the Boyfriend) \
**Credit** to determine the **Player 2** (for example, dad - being the Dad) \
**Subtitle** to determine the **speed** (for example, 2.0) \
**Background** to determine the **stage** (for example, philly - Pico's stage) \

Written by shockdude in Python 3.7 \
Original chart-to-sm.js by Paturages \
https://github.com/Paturages/

Project Outfox (active StepMania fork): https://projectmoon.dance/ \
Friday Night Funkin: https://ninja-muffin24.itch.io/funkin