import zipfile
import sys
import os
import tempfile
import json
import math
import datetime
format = r'%Y/%m/%d %H:%M:%S.%f'

def GetFrame(framenumber):
	timestamp, jsondata = data[framenumber].split("\t")
	return datetime.datetime.strptime(timestamp, format), json.loads(jsondata)

filepath = sys.argv[1]

data = []
if zipfile.is_zipfile(filepath):
	# Unzip
	with zipfile.ZipFile(filepath, 'r') as zf:
		with tempfile.TemporaryDirectory() as td:
			zf.extractall(td)
			for entry in os.scandir(td):
				with open(entry.path, 'r') as f:
					data=f.readlines()
else:
	with open(filepath) as f:
		data = f.readlines()


startstr = input("Starting time (e.x 5:45): ")
startlist = startstr.split(':')
start = float(startlist[0]) * 60 + float(startlist[1])

endstr = input("Starting time (e.x 5:45): ")
endlist = endstr.split(':')
end = float(endlist[0]) * 60 + float(endlist[1])

player = []
lastpos = [0, 0, 0]
offset = [0, 0, 0]

lastts = 0

PRE = 0
DURING = 1
POST = 2

frame = 0
state = PRE

while True:
	ts, js = GetFrame(frame)

	gameclock = 0
	try:
		gameclock = js["game_clock"]
	except KeyError:
		frame += 1
		continue

	if state == PRE:
		if (gameclock < start):
			state = DURING
			players = []
			paths = []
			for teamindex, team in enumerate(js["teams"]):
				playerslist = []
				try:
					playerslist = team["players"]
				except KeyError:
					continue

				for playerindex, p in enumerate(playerslist):
					players.append(p["name"])
					paths.append([teamindex, playerindex])
			print("Select player:")
			for i,p in enumerate(players):
				print(f"({i}): {p}")
			pindex = int(input("Number: "))
			player = paths[pindex]
			lastpos = js["teams"][player[0]]["players"][player[1]]["head"]["position"]
			lastpos = [float(x) for x in lastpos]
			lastts = ts

	elif state == DURING:
		playerdata = js["teams"][player[0]]["players"][player[1]]
		pos = playerdata["head"]["position"]
		pos = [float(x) for x in pos]
		vel = playerdata["velocity"]
		vel = [float(x) for x in vel]
		offset = [offset_i + pos_i - lastpos_i - (vel_i * (ts - lastts).total_seconds()) for offset_i, pos_i, lastpos_i, vel_i in zip(offset, pos, lastpos, vel)]
		len = math.sqrt(sum([x * x for x in offset]))
		color = " "
		if len > 0.862: # 2*root(2) ft to m
			color = '!'
		print(f"{color} {js['game_clock_display']} {len:.2f} [{', '.join([f'{x: .2f}' for x in offset])}]")

		lastpos = pos
		lastts = ts
		if (gameclock < end):
			state=POST

	elif state == POST:
		input("Press enter to exit")
		break

	frame += 1