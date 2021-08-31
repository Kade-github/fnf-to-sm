# fnf-to-sm.py
# FNF to SM converter
# Copyright (C) 2021 shockdude

# Modified by KadeDev to add support for Dance Double

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.	If not, see <https://www.gnu.org/licenses/>.

# Built from the original chart-to-sm.js by Paturages, released under GPL3 with his permission

import re
import json
import math
import sys
import os

VERSION = "v0.1.2"

SM_EXT = ".sm"
SSC_EXT = ".ssc"
FNF_EXT = ".json"
CHART_FOLDER = "charts\\"

# stepmania editor's default note precision is 1/192
MEASURE_TICKS = 192
BEAT_TICKS = 48
# fnf step = 1/16 note
STEP_TICKS = 12

NUM_COLUMNS = 8

# borrowed from my Sharktooth code
class TempoMarker:
	def __init__(self, bpm, tick_pos, time_pos):
		self.bpm = float(bpm)
		self.tick_pos = tick_pos
		self.time_pos = time_pos

	def getBPM(self):
		return self.bpm

	def getTick(self):
		return self.tick_pos

	def getTime(self):
		return self.time_pos

	def timeToTick(self, note_time):
		return int(round(self.tick_pos + (float(note_time) - self.time_pos) * MEASURE_TICKS * self.bpm / 240000))

	def tickToTime(self, note_tick):
		return self.time_pos + (float(note_tick) - self.tick_pos) / MEASURE_TICKS * 240000 / self.bpm

# compute the maximum note index step per measure
def measure_gcd(num_set, MEASURE_TICKS):
	d = MEASURE_TICKS
	for x in num_set:
		d = math.gcd(d, x)
		if d == 1:
			return d
	return d

tempomarkers = []

# helper functions for handling global tempomarkers 
def timeToTick(timestamp):
	for i in range(len(tempomarkers)):
		if i == len(tempomarkers) - 1 or tempomarkers[i+1].getTime() > timestamp:
			return tempomarkers[i].timeToTick(timestamp)
	return 0

def tickToTime(tick):
	for i in range(len(tempomarkers)):
		if i == len(tempomarkers) - 1 or tempomarkers[i+1].getTick() > tick:
			return tempomarkers[i].tickToTime(tick)
	return 0.0

def tickToBPM(tick):
	for i in range(len(tempomarkers)):
		if i == len(tempomarkers) - 1 or tempomarkers[i+1].getTick() > tick:
			return tempomarkers[i].getBPM()
	return 0.0

def fnf_to_sm(infile):
	chart_jsons = []

	# given a normal difficulty .json,
	# try to detect all 3 FNF difficulties if possible
	infile_name, infile_ext = os.path.splitext(infile)
	infile_easy = infile_name + "-easy" + FNF_EXT
	infile_hard = infile_name + "-hard" + FNF_EXT

	with open(infile, "r") as chartfile:
		chart_json = json.loads(chartfile.read().strip('\0'))
		chart_json["diff"] = "Medium"
		chart_jsons.append(chart_json)

	if os.path.isfile(infile_easy):
		with open(infile_easy, "r") as chartfile:
			chart_json = json.loads(chartfile.read().strip('\0'))
			chart_json["diff"] = "Easy"
			chart_jsons.append(chart_json)

	if os.path.isfile(infile_hard):
		with open(infile_hard, "r") as chartfile:
			chart_json = json.loads(chartfile.read().strip('\0'))
			chart_json["diff"] = "Hard"
			chart_jsons.append(chart_json)

	# for each fnf difficulty
	sm_header = ''
	sm_notes = ''
	for chart_json in chart_jsons:
		song_notes = chart_json["song"]["notes"]
		num_sections = len(song_notes)
		# build sm header if it doesn't already exist
		if len(sm_header) == 0:
			song_name = chart_json["song"]["song"]
			song_bpm = chart_json["song"]["bpm"]

			print("Converting {} to {}.sm".format(infile, song_name))

			# build tempomap
			bpms = "#BPMS:"
			current_bpm = None
			current_tick = 0
			current_time = 0.0
			for i in range(num_sections):
				section = song_notes[i]

				if section.get("changeBPM", 0) != 0:
					section_bpm = float(section["bpm"])
				elif current_bpm == None:
					section_bpm = song_bpm
				else:
					section_bpm = current_bpm
				if section_bpm != current_bpm:
					tempomarkers.append(TempoMarker(section_bpm, current_tick, current_time))
					bpms += "{}={},".format(i*4, section_bpm)
					current_bpm = section_bpm

				# each step is 1/16
				section_num_steps = section["lengthInSteps"]
				# default measure length = 192
				section_length = STEP_TICKS * section_num_steps
				time_in_section = 15000.0 * section_num_steps / current_bpm

				current_time += time_in_section
				current_tick += section_length

			# add semicolon to end of BPM header entry
			bpms = bpms[:-1] + ";\n"

			# write .sm header
			sm_header = "#TITLE:{};\n".format(song_name)
			sm_header += "#MUSIC:{}.ogg;\n".format(song_name)
			sm_header += bpms

		notes = {}
		last_note = 0
		diff_value = 1

		# convert note timestamps to ticks
		for i in range(num_sections):
			section = song_notes[i]
			section_notes = section["sectionNotes"]
			for section_note in section_notes:
				tick = timeToTick(section_note[0])
				note = section_note[1]
				if section["mustHitSection"]:
					note = (note + 4) % 8
				length = section_note[2]

				# Initialize a note for this tick position
				if tick not in notes:
					notes[tick] = [0]*NUM_COLUMNS

				if length == 0:
					notes[tick][note] = 1
				else:
					notes[tick][note] = 2
					# 3 is "long note toggle off", so we need to set it after a 2
					# FIXME long note tails can be overwritten by other notes
					long_end = timeToTick(section_note[0] + section_note[2])
					if long_end not in notes:
						notes[long_end] = [0]*NUM_COLUMNS
					notes[long_end][note] = 3
					if last_note < long_end:
						last_note = long_end

				if last_note <= tick:
					last_note = tick + 1

		if len(notes) > 0:
			# write chart & difficulty info
			sm_notes += "#NOTES:\n"
			sm_notes += "	  dance-double:\n"
			sm_notes += "	  :\n"
			sm_notes += "	  {}:\n".format(chart_json["diff"]) # e.g. Challenge:
			sm_notes += "	  {}:\n".format(diff_value)
			sm_notes += "	  :\n" # empty groove radar

			# ensure the last measure has the correct number of lines
			if last_note % MEASURE_TICKS != 0:
				last_note += MEASURE_TICKS - (last_note % MEASURE_TICKS)

			# add notes for each measure
			for measureStart in range(0, last_note, MEASURE_TICKS):
				measureEnd = measureStart + MEASURE_TICKS
				valid_indexes = set()
				for i in range(measureStart, measureEnd):
					if i in notes:
						valid_indexes.add(i - measureStart)

				noteStep = measure_gcd(valid_indexes, MEASURE_TICKS)

				for i in range(measureStart, measureEnd, noteStep):
					if i not in notes:
						sm_notes += '0'*NUM_COLUMNS + '\n'
					else:
						for digit in notes[i]:
							sm_notes += str(digit)
						sm_notes += '\n'

				if measureStart + MEASURE_TICKS == last_note:
					sm_notes += ";\n"
				else:
					sm_notes += ',\n'

	# output simfile
	with open("{}.sm".format(song_name), "w") as outfile:
		outfile.write(sm_header)
		if len(sm_notes) > 0:
			outfile.write(sm_notes)

# parse the BPMS out of a simfile
def parse_sm_bpms(bpm_string):
	sm_bpms = bpm_string.split(",")
	bpm_re = re.compile("(.+)=(.+)")
	for sm_bpm in sm_bpms:
		re_match = bpm_re.match(sm_bpm)
		if re_match != None and re_match.start() == 0:
			current_tick = int(round(float(re_match.group(1)) * BEAT_TICKS))
			current_bpm = float(re_match.group(2))
			current_time = tickToTime(current_tick)
			tempomarkers.append(TempoMarker(current_bpm, current_tick, current_time))

def sm_to_fnf(infile):
	# input values for the converted file
	print("Converting {}".format(infile))

	songTitle = input("Input song title (auto defaults): ") or "Simfile"
	player1 = input("Input Player1 (defaults to bf): ") or "bf"
	player2 = input("Input Player2 (no default): ")
	keStage = input("Input Kade Engine stage (optional): ")

	# read the SM file
	with open(infile, "r") as chartfile:
		offset = 0
		metatag_re = re.compile("^#(.+):(.+);$")
		notes_re = re.compile("^[a-zA-Z0-9]{8}$")
		line = chartfile.readline().strip()
		while len(line) > 0:
			# read meta tags
			tag_matches = metatag_re.match(line)
			if tag_matches:
				tag_matches = tag_matches.groups()

				if tag_matches[0] == "TITLE":
					songTitle = tag_matches[1]
				elif tag_matches[0] == "OFFSET":
					offset = float(tag_matches[1]) * 1000
				elif tag_matches[0] == "BPMS":
					parse_sm_bpms(tag_matches[1])

				# skip to next line
				line = chartfile.readline().strip()
				continue

			# TODO support SSC
			# read each chart in simfile
			if line == "#NOTES:":
				# read chart meta tags
				chart_tags = {
					"chartType": chartfile.readline().strip(),
					"chartAuthor": chartfile.readline().strip(),
					"difficultyLevel": chartfile.readline().strip(),
					"difficultyRating": chartfile.readline().strip(),
					"grooveRadar": chartfile.readline().strip(),
				}

				# skip charts that are not dance double
				if chart_tags["chartType"] != "dance-double:":
					line = chartfile.readline().strip()
					continue

				# skip unused meta tags
				del chart_tags["chartType"]
				del chart_tags["chartAuthor"]
				del chart_tags["difficultyRating"]
				del chart_tags["grooveRadar"]

				# read notes in chart
				fnf_notes = []
				tracked_holds = {} # for tracking hold notes, need to add tails later
				line = chartfile.readline().strip()
				while line[0] != ";":
					# read the current measure
					measure_notes = []
					while line[0] not in (",",";"):
						if notes_re.match(line) != None:
							measure_notes.append(line)
						line = chartfile.readline().strip()

					# prepare the current section
					section_num = len(fnf_notes)
					fnf_section = {
						"bpm": tickToBPM(section_num * MEASURE_TICKS),
						"changeBPM": fnf_section["bpm"] != fnf_notes[-1]["bpm"]
						if section_num else False,
						"mustHitSection": False,
						"lengthInSteps": 16,
						"typeOfSection": 0,
					}

					# for ticks-to-time, ticks don't have to be integer :)
					ticks_per_row = float(MEASURE_TICKS) / len(measure_notes)

					# convert notes in section
					section_notes = []
					for row_num in range(len(measure_notes)):
						notes_row = measure_notes[row_num]
						for col_num in range(len(notes_row)):

							# since in dance-double, we're assuming that col 4-7 is the player and col 0-3 is the opponent

							# append single notes, hold notes, and roll notes
							if notes_row[col_num] in ("1","2","4"):
								note = [tickToTime(MEASURE_TICKS * section_num + row_num * ticks_per_row) - offset, col_num, 0]
								section_notes.append(note)
								# track hold notes and roll notes as long notes
								if notes_row[col_num] in ("2","4"):
									tracked_holds[col_num] = note
								# mustHitSection when player side has notes
								if col_num in range(4,8):
									fnf_section["mustHitSection"] = True
							# turn hold/roll tails into note duration
							elif notes_row[col_num] == "3":
								if col_num in tracked_holds:
									note = tracked_holds[col_num]
									del tracked_holds[col_num]
									note[2] = tickToTime(MEASURE_TICKS * section_num + row_num * ticks_per_row) - offset - note[0]
							# mines work with tricky fire notes
							elif notes_row[col_num] == "M":
								note = [tickToTime(MEASURE_TICKS * section_num + row_num * ticks_per_row) - offset, col_num + 8, 0]
								section_notes.append(note)

					# append converted section
					fnf_section["sectionNotes"] = section_notes
					fnf_notes.append(fnf_section)

					# don't skip the ending semicolon
					if line[0] != ";":
						line = chartfile.readline().strip()

				# swap sides for mustHitSection
				for section in fnf_notes:
					if section["mustHitSection"]:
						for note in section["sectionNotes"]:
							# swap opponent side
							if note[1] in range(0,4) or note[1] in range(8,12):
								note[1] += 4
							# swap player side
							elif note[1] in range(4,8) or note[1] in range(12,16):
								note[1] -= 4

				# prepare the chart json
				chart_json = {
					"song": {
						"song": songTitle,
						"needsVoices": True,
						"player1": player1,
						"player2": player2,
						"speed": 2.0,
						"bpm": tempomarkers[0].getBPM(),
						#"sections": 0,
						#"sectionLengths": [],
						"notes": fnf_notes,
					},
				}

				if keStage:
					chart_json["song"]["stage"] = keStage

				# prepare suffix for difficulty level
				if chart_tags["difficultyLevel"] == "Medium:":
					chart_tags["difficultyLevel"] = ""
				else:
					chart_tags["difficultyLevel"] = "-" + chart_tags["difficultyLevel"][:-1].lower()

				# prepare the complete file name
				chartTitle = (
					CHART_FOLDER +
					songTitle.replace(" ", "-").lower() +
					chart_tags["difficultyLevel"] +
					FNF_EXT
				)

				# convert chart to json
				with open(chartTitle, "w") as outfile:
					json.dump(chart_json, outfile, separators=(",", ":"))

			# continue reading the file
			line = chartfile.readline().strip()

def usage():
	print("FNF SM converter")
	print("Usage: {} [chart_file]".format(sys.argv[0]))
	print("where [chart_file] is a .json FNF chart or a .sm simfile")
	sys.exit(1)

def main():
	if len(sys.argv) < 2:
		print("Error: not enough arguments")
		usage()

	infile = sys.argv[1]
	infile_name, infile_ext = os.path.splitext(os.path.basename(infile))
	if infile_ext == FNF_EXT:
		fnf_to_sm(infile)
	elif infile_ext == SM_EXT:
		sm_to_fnf(infile)
	else:
		print("Error: unsupported file {}".format(infile))
		usage()

if __name__ == "__main__":
	main()
