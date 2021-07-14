# FNF/SM converter (Dance Double Support)

This is a modified fork of [the orginal repo](https://github.com/shockdude/fnf-to-sm) which adds dance double support instead of dance single charts.

Roughly convert Friday Night Funkin .json charts to doubles simfiles for StepMania \
Or convert StepMania simfiles to FNF charts. \
Very WIP but it works, kinda.

Usage: Drag-and-drop the FNF .json chart or a StepMania .sm simfile onto `fnf-to-sm.exe` \
Or use the command line: `python fnf-to-sm.py [chart_file]`

For FNF-to-SM, if you input the Normal difficulty .json, and have the \
easy & hard .jsons in the same folder, then FNF-to-SM will output \
a single .sm with all 3 difficulties.

SM-to-FNF currently only supports Challenge Single difficulty. \
The output "blammed.json" is meant to replace "Blammed", Normal difficulty.

Written by shockdude in Python 3.7 \
Original chart-to-sm.js by Paturages \
https://github.com/Paturages/

Project Outfox (active StepMania fork): https://projectmoon.dance/ \
Friday Night Funkin: https://ninja-muffin24.itch.io/funkin
