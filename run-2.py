import re

def getAllBoards():

	file = open("boards.txt", mode="r", encoding="utf8")
	text = file.read().splitlines()
	file.close()

	boards = []
	leftRows = 0
	board = []
	expectedNum = 1

	for line in text:
		x = re.search(r"^\d+$", line)
		if(leftRows != 0):
			board.append(line[1:])
			leftRows -= 1
			if(leftRows == 0):
				boards.append(board)
		elif(x is not None):
			leftRows = 8
			expectedNum += 1
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

boards = getAllBoards()
print(len(boards))
print(boards[0])
print(getFenForBoard(boards[0]))