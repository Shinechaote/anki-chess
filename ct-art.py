from string import whitespace
from turtle import pu
from pynput import mouse
from PIL import ImageGrab
# from putznn import Board
import pyautogui
import pyperclip
import time
import re
import os

control = mouse.Controller()
board_positions = [(696, 224), (918, 445),  (696, 495), (918, 718), (697, 770), (918, 992), (982, 226), (1204, 447), (983, 498), (1205, 720),  (983, 770), (1205, 992)]
color_positions = [(930, 235), (930, 511), (930, 782), (1221, 237), (1221, 511), (1221, 783)]
two_positions = [(690, 406), (689, 670), (690, 950), (977, 406),  (977, 670),  (977, 950)]
anki_fen_position = (1156, 148)
fen_text_position = [(20, 558, 1876, 558)]

def on_click(x, y, button, pressed):

	print(control.position)

# with mouse.Listener(on_click=on_click) as listener:
# 	listener.join()
def isBlackPlaying(pos):
	px = ImageGrab.grab()
	bbox = (color_positions[pos][0], color_positions[pos][1],color_positions[pos][0] + 3,color_positions[pos][1] + 3)
	im = ImageGrab.grab(bbox).load()
	return im[1,1] == (128, 128, 128)

def getBoardsFromBook(pages = 411):
	puzzleNum = 0
	time.sleep(5)
	for j in range(pages):	
		dontSave = False
		for i in range(6):
			bbox = (board_positions[2*i][0], board_positions[2*i][1], board_positions[2*i+1][0], board_positions[2*i+1][1])
			im = ImageGrab.grab(bbox)
			il = im.load()
			for k in range(0, 50):
				for l in range(0, 50):
					if(il[k, l] != (255,255,255)):
						break
				else:
					continue
				break
			else:
				dontSave = True
				continue
			puzzleNum += 1
			if(dontSave):
				continue
			if(isBlackPlaying(i)):
				im.save("./Images/sc" + str(puzzleNum) + "_black.png")
			else:
				im.save("./Images/sc" + str(puzzleNum) + "_white.png")
		pyautogui.press("right")
		time.sleep(1)

def getAllImageNames(dir):
	files = []
	for file in os.listdir(dir):
		files.append(os.fsdecode(file))
	files.sort(key=lambda x: int(x[2:int(x.index("_"))])-1)
	return files



def getFenForImage(filename):
	print(filename)
	color = " w" if "white" in filename else " b"
	bd = Board(filename)
	return bd.boardprednn2() + color + " KQkq - 0 1"

def writeFensFromImages():
	last_fen = ""
	directory = "Images"
	files = getAllImageNames(directory)
	counter = 0

	with open("fens.txt", "w") as outfile:
		for file in files:
			if(counter%10 == 0):
				print(counter)
			if(int(file[2:int(file.index("_"))])-1 != counter):
				outfile.write("\n")
				counter = int(file[2:int(file.index("_"))])
				continue
			last_fen = getFenForImage(directory + "/"+file) 
			outfile.write(last_fen+ "\n")
			counter += 1

def splitPGNs(text, outfile="pgns_formated.txt"):
	tmp= text.splitlines()
	split_puzzles = []
	next_num = 1
	for i in range(len(tmp)):
		x = re.search(r"^\d+ [0-2]\.",  tmp[i])
		if(x != None):
			y = re.search(r"^\d+", tmp[i]).span()
			if(next_num != int(tmp[i][y[0]:y[1]])):
				print(tmp[i-1])
				print(tmp[i])
				print(tmp[i+1])
				quit()
				pass
			next_num += 1
			tmp[i] = re.sub(r"^\d+", "", tmp[i])
			split_puzzles.append(tmp[i])
		else:
			split_puzzles[-1] += tmp[i]
	count = 0
	newFile = open(outfile, mode="w", encoding="utf8")
	for i, puzzle in enumerate(split_puzzles):
		if(",") in puzzle:
			comma_splitted = puzzle.split(",")
			puzzle = comma_splitted[0] + comma_splitted[-1] if len(comma_splitted) > 2 else comma_splitted[0]
			whitespace_splitted = puzzle.split(" ")
			included = []
			for chars in whitespace_splitted:
				if(re.search(r"[ij]|[lm]|[op]|[s-w]|[y-z]|:|-|\d\d+", chars.lower()) is None):
					if(chars == "."):
						continue
					included.append(chars)
			puzzle = " ".join(included)
			split_puzzles[i] = puzzle
			newFile.write(puzzle + "\n")
			count +=1 
		else:
			whitespace_splitted = puzzle.split(" ")
			included = []
			for chars in whitespace_splitted:
				if(re.search(r"[ij]|[lm]|[op]|[s-w]|[y-z]|:|-|\d\d+", chars.lower()) is None):
					if(chars == "."):
						continue
					included.append(chars)
			puzzle = " ".join(included)
			split_puzzles[i] = puzzle
			
			newFile.write(puzzle + "\n")
	newFile.close()
	

	return split_puzzles

def loadFENs():
	file = open("fens.txt", mode="r", encoding="utf8")
	text = file.read().split("\n")
	file.close()
	return text

def readPGNs(file):
	pgnFile = open(file, mode="r", encoding="utf8")
	text = pgnFile.read()
	pgnFile.close()
	pgns = splitPGNs(text)
	return pgns

def createAnkiCards():
	pgns = readPGNs("pgns.txt")
	fens = loadFENs()

	for i, pgn in enumerate(pgns):
		if(i % 10 == 0):
			print(i)

		if(len(fens[i]) > 16):
			color_ind = len(fens[i]) - ("w" + fens[i])[::-1].index("w")
			if(color_ind == 0):
					color_ind = len(fens[i]) - (fens[i])[::-1].index("b")
			if(not "k" in fens[i][0:color_ind] or not "K" in fens[i][0:color_ind]):
				x = re.search("8/8/8", fens[i]) 
				if(x is not None):
					if(x.span()[0] == 0):
						fens[i] = "k7/pp6" + fens[i][3:]
					else:
						fens[i] = fens[i][:x.span()[0]+2] + "6PP/7K" + fens[i][x.span()[1]:]

			pyautogui.click(anki_fen_position[0], anki_fen_position[1])
			pyperclip.copy(fens[i])
			pyautogui.hotkey("ctrl", "v")
			pyautogui.press('tab')
			pyperclip.copy(pgn)
			pyautogui.hotkey("ctrl", "v")
			pyautogui.press('tab')
			pyperclip.copy("true")
			pyautogui.hotkey("ctrl", "v")
			pyautogui.press('tab')
			pyperclip.copy(str(i+1))
			pyautogui.hotkey("ctrl", "v")
			pyautogui.hotkey("ctrl", "enter")

createAnkiCards()