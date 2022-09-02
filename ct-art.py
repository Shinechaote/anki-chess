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
			next_num += 1
			tmp[i] = re.sub(r"^\d+", "", tmp[i])
			split_puzzles.append(tmp[i])
		else:
			split_puzzles[-1] += " " + tmp[i]
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
	
	complete_puzzles = []
	for i, puzzle in enumerate(split_puzzles):
		split_pgn = puzzle.split()
		if("." in split_pgn):
			puzzle = " ".join(split_pgn[:-1])
		puzzle = puzzle.strip()
		if(puzzle[-1] == "."):
			puzzle = puzzle[:-1]
		complete_puzzles.append(puzzle)
		complete_puzzles.append(flipPGN(puzzle))
		


	return complete_puzzles

def getAllBoards():

	file = open("boards.txt", mode="r", encoding="utf8")
	text = file.read().splitlines()
	file.close()

	boards = []
	leftRows = 0
	board = []

	for line in text:
		x = re.search(r"^\d+$", line)
		if(leftRows != 0):
			board.append(line[1:])
			leftRows -= 1
			if(leftRows == 0):
				boards.append(board)
		if(x is not None):
			leftRows = 8
			board = []
	return boards

def getFenForBoard(board):
	fen = ""
	for row in board:
		counter = 0
		for char in row:
			if(char == "0" or char == "Z"):
				counter += 1
			else:
				if(counter != 0):
					fen += str(counter)
				if(char == "J"):
					fen += "K"
				elif(char == "j"):
					fen += "k"
				elif(char == "L"):
					fen += "Q"
				elif(char == "l"):
					fen += "q"
				elif(char == "S"):
					fen += "R"
				elif(char == "s"):
					fen += "r"
				elif(char == "A"):
					fen += "B"
				elif(char == "M"):
					fen += "N"
				elif(char == "m"):
					fen += "n"
				elif(char == "a"):
					fen += "b"
				elif(char == "o"):
					fen += "p"
				elif(char == "O"):
					fen += "P"
				else:
					fen += char
				counter = 0
		if(counter != 0):
			fen += str(counter)
		fen += "/"
	return fen[:-1]

def loadFENs():
	boards = getAllBoards()
	imageNames = getAllImageNames("Images")

	complete_text = []
	for i, board in enumerate(boards):
		fen = getFenForBoard(board)
		fen += " w" if "white" in imageNames[i] else " b" 
		fen += " KQkq - 0 1"
		complete_text.append(fen)
		complete_text.append(flipFen(fen))
	return complete_text

def readPGNs(file):
	pgnFile = open(file, mode="r", encoding="utf8")
	text = pgnFile.read()
	pgnFile.close()
	pgns = splitPGNs(text)
	return pgns

def flipFen(fen):
	if(len(fen) < 16):
		return fen
	color_ind = len(fen) - ("w" + fen)[::-1].index("w")
	color = " b"
	if(color_ind == 0):
		color_ind = len(fen) - (fen)[::-1].index("b")
		color = " w"
	rest =fen[color_ind:]
	fen = fen[:color_ind-2]
	tmp_fen = ""
	for i in range(1,len(fen)+1):
		tmp_fen += fen[-i].lower() if fen[-i].isupper() else fen[-i].upper()
	
	fen = tmp_fen + color + rest
	return fen

def flipPGN(pgn):
	tmp_pgn = ""
	flip_dict = {"a": "h", "b":"g", "c":"f", "d": "e", "e": "d", "f": "c", "g": "b", "h":"a"}
	pgn = pgn.strip()
	for i, char in enumerate(pgn):
		if(char.isalpha() and char.islower() and char in flip_dict.keys()):
			tmp_pgn += flip_dict[char]
		elif(i < len(pgn)-1 and char.isnumeric()):
			if(pgn[i+1] != "."):
				tmp_pgn += str(9-int(char))
			else:
				tmp_pgn += char
		elif (char.isnumeric()):
			tmp_pgn += str(9-int(char))
		else:
			tmp_pgn += char
	

	
	return tmp_pgn
			

def createAnkiCards():
	pgns = readPGNs("pgns.txt")
	fens = loadFENs()

	for i, pgn in enumerate(pgns):
		if(i < 102):
			continue
		if(i % 100 == 0):
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
			pyperclip.copy(str(i//2+1))
			pyautogui.hotkey("ctrl", "v")
			pyautogui.hotkey("ctrl", "enter")
		


# readPGNs("pgns.txt")

	
createAnkiCards()