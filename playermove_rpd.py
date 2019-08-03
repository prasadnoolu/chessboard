# Vision code

# This module copyright 2018 Richard Day, chess@gotobiz.co.uk
# This code must not be resold, or distributed in any way without express permission

# For each square compute standard deviation and mean of colour values within the square
# Can tell which squares are empty by standard deviation being below a certain value
# After which we distinguish between black (brown) and white because max mean for brown is less than min mean for white

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
import time
import os
#import cv2
import sys
import numpy
from PIL import Image

firsttimeonly = 1
firstgbp = 1
splitwb = 112
stdrgb = 23

xrevtrans = {
	1: "a",
	2: "b",
	3: "c",
	4: "d",
	5: "e",
	6: "f",
	7: "g",
	8: "h"
}

# Now initialize board arrays
xx, yy = 8, 8;
pieces = [["e" for x in range(xx)] for y in range(yy)]
oldpieces = [["e" for x in range(xx)] for y in range(yy)]
for row in range(2):
	for col in range(8):
		pieces[row][col] = "b"
		oldpieces[row][col] = "b"
for row in range(6,8):
	for col in range(8):
		pieces[row][col] = "w"
		oldpieces[row][col] = "w"	

def updateforcomputermove(board):
	global oldpieces, pieces, firsttimeonly
	if firsttimeonly:
		firsttimeonly = 0
		print ("first time only:")		
	
	else:
		for x in range(8):
			for y in range(8):
				current = board[x][y]
				if current == ".":
					oldpieces[x][y] = "e"
				elif current.islower():
					oldpieces[x][y] = "b"
				else:
					oldpieces[x][y] = "w"
	print ("After computer move:")
	print (oldpieces)
	#raw_input("Now any key")
	
def drawredlines():
	im = Image.open('/home/pi/Chess/images/4.jpg', 'r')
	pix = im.load()
	#im.show()
	squaresizex = float(im.size[0])/8	
	squaresizex = int(round(squaresizex))
	squaresizey = float(im.size[1])/8
	squaresizey = int(round(squaresizey))
	i = 0
	while i < im.size[0]:
		j = 0
		while j < im.size[1]:
			pix[i,j] = (255,0,0)
			j += 1
		i += squaresizex
	j = 0
	while j < im.size[1]:
		i = 0
		while i < im.size[0]:
			pix[i,j] = (255,0,0)
			i += 1
		j += squaresizey
	im.save('/home/pi/Chess/images/redlines.jpg')  # Save the modified pixels
	im = Image.open('/home/pi/Chess/images/redlines.jpg', 'r')
	im.show()	# uncomment to test

def nudgecrop(im):	
	#nudcurrsplit = (178,12,526,358)
	nudcurrsplit = (195,22,517,336)	# x1, y1, x2, y2; white on left
	nudinc = ("0,0,0,0")
	while True:
		nudincsplit = nudinc.split(",")
		nudcurrsplit = (int(nudcurrsplit[0])+int(nudincsplit[0]), int(nudcurrsplit[1])+int(nudincsplit[1]), int(nudcurrsplit[2])+int(nudincsplit[2]), int(nudcurrsplit[3])+int(nudincsplit[3]) )
		cropped_image = im.crop(nudcurrsplit) 
		cropped_image.save('/home/pi/Chess/images/4.jpg')
		cropped_image.show()   # uncomment for testing
		print (nudcurrsplit)
		sys.stdout.flush()		

		return()  ##### comment out for re-nudging
		nudinc = raw_input("x1, y1, x2, y2 OR q")		
		if nudinc == "q":
			return()
def calibratecamera(board):
	global firstgbp
	os.system('fswebcam -r 640x480 -S 20 --set "Power Line Frequency"="50 Hz" --list-controls --no-banner --delay 2 --set brightness=25% --jpeg 50 --save /home/pi/Chess/images/1.jpg')	
	#os.system('fswebcam -r 640x480 -S 5 -F 5 --set "Power Line Frequency"="50 Hz" --list-controls --no-banner --delay 1 --set brightness=50% --set "Exposure, Auto"=False --set "Exposure (absolute)"=400 --jpeg 50 --save /home/pi/Chess/images/1.jpg')
	#takepic()
	im = Image.open('/home/pi/Chess/images/1.jpg', 'r')
	#im = im.rotate(0.10)
	nudgecrop(im)
	while True:
		firstgbp = 1
		getplayermove (board, ()) # dummy in order to get best number to differentiate between black and white
		drawredlines()
		#return() 	# comment out for testing
		conti = raw_input("Try again? y/n")
		if conti == "n":
			return()

def newcastling(board, validkingmoves):
	global pieces
	print ("castling code")
	#print (pieces)
	print (validkingmoves)
	if board[7][4] == "K" :
		print ("h1")
		for (i, j) in validkingmoves:
			tup = (i, j)
			print ("h2", tup)
			if tup == (6,7):
				print ("h3")
				if pieces [7][4] == "e" and pieces[7][5] != "e" and pieces[7][6] != "e" and pieces [7][7] == "e" :
					print ("castled king side")
					return ("me1g1")
			if tup == (2,7):
				if pieces [7][0] == "e" and pieces[7][1] == "e" and pieces[7][2] != "e" and pieces [7][3] != "e" and pieces[7][4] == "e" :
					print ("castled queen side")
					return ("me1c1")
		# code for invalid castling:
		# on king's side, if K..R before and (6,7) not in validkingmoves and pieces ewwe then invalid castling
		if (6,7) not in validkingmoves:
			if board[7][4:8] == "K..R":
				if pieces[7][4:8] == "ewwe":
					print ("Invalid: castled king side")
					return ("me1g1")
		# on queen's side, if R...K before and (2,7) not in validkingmoves and pieces eewwe then invalid castling
		if (2,7) not in validkingmoves:
			if board[7][0:5] == "R...K":
				if pieces[7][0:5] == "eewwe":
					print ("Invalid: castled queen side")
					return ("me1g1")
		return ("")
	
def castling(board, validkingmoves):
	global pieces
	print ("castling code")
	#print (pieces)
	print (validkingmoves)
	if board[7][4] == "K" :
		print ("h1")
		#piecesr = list(zip(*reversed(pieces)))  # rotate
		for (i, j) in validkingmoves:
			tup = (i, j)
			print ("h2", tup)
			if tup == (6,7):
				print ("h3")
				if pieces [7][4] == "e" and pieces[7][5] != "e" and pieces[7][6] != "e" and pieces [7][7] == "e" :
					print ("castled king side")
					return ("me1g1")
			if tup == (2,7):
				if pieces [7][0] == "e" and pieces[7][1] == "e" and pieces[7][2] != "e" and pieces [7][3] != "e" and pieces[7][4] == "e" :
					print ("castled queen side")
					return ("me1c1")
		return ("")
		
def enpassantmove (board):
	global pieces
	if CBstate.cbstate == 1:	# piece available for en passant
		a = 1
				
def getplayermove(board, validkingmoves):
	global pieces, oldpieces, firstgbp, splitwb
	updateforcomputermove(board)
	os.system('fswebcam -r 640x480 -S 20 --set "Power Line Frequency"="50 Hz" --list-controls --no-banner --delay 2 --set brightness=25% --set "Exposure, Auto Priority"=False --jpeg 50 --save /home/pi/Chess/images/1.jpg')
	#os.system('fswebcam -r 640x480 -S 5 -F 5 --set "Power Line Frequency"="50 Hz" --list-controls --no-banner --delay 1 --set brightness=50% --set "Exposure, Auto"=False --set "Exposure (absolute)"=400 --jpeg 50 --save /home/pi/Chess/images/1.jpg')
	#takepic()
	im = Image.open('/home/pi/Chess/images/1.jpg', 'r')
	im = im.rotate(0.10)	# modify as appropriate

	nudgecrop(im)

	im = Image.open('/home/pi/Chess/images/4.jpg', 'r')
	#im.show()	# uncomment for testing

	pix = im.load()
	print (im.size)  # Get the width and height of the image for iterating over
	squaresizex = float(im.size[0])/8
	squaresizex = int(round(squaresizex))
	squaresizey = float(im.size[1])/8
	squaresizey = int(round(squaresizey))
	minRw = minRe = minRb = minGw = minGe = minGb = minBw = minBe = minBb = 256
	maxRw = maxRe = maxRb = maxGw = maxGe = maxGb = maxBw = maxBe = maxBb = 0
	
	fudge = 7
	for row in range(8):	
		for col in range(8):
			i = int((row * squaresizex) + fudge)		
			pixlistR = []
			pixlistG = []
			pixlistB = []
			while i < ((row + 1) * squaresizex) - fudge:
				j = int((col * squaresizey) + fudge)
							
				while j < ((col + 1) * squaresizey) - fudge:
					pixlistR.append (pix[i,j][0])
					pixlistG.append (pix[i,j][1])
					pixlistB.append (pix[i,j][2])
					j += 1
				i += 1

			print (row,col)
			print ("std:")
			stdR = numpy.std(pixlistR)
			stdG = numpy.std(pixlistG)
			stdB = numpy.std(pixlistB)
			#print (stdR)
			#print (stdG)
			#print (stdB)
			print (stdR + stdG + stdB)
			#print("mean:")
			meanR = numpy.mean(pixlistR)
			meanG = numpy.mean(pixlistG)
			meanB = numpy.mean(pixlistB)
			#print (meanR)
			#print (meanG)
			#print (meanB)
			#print("next")
			
			if row < 2:
				minRw = min (minRw, meanR)
				maxRw = max (maxRw, meanR)
				minGw = min (minGw, meanG)
				maxGw = max (maxGw, meanG)
				minBw = min (minBw, meanB)
				maxBw = max (maxBw, meanB)
			elif row >5:
				minRb = min (minRb, meanR)
				maxRb = max (maxRb, meanR)
				minGb = min (minGb, meanG)
				maxGb = max (maxGb, meanG)
				minBb = min (minBb, meanB)
				maxBb = max (maxBb, meanB)
			else:
				minRe = min (minRe, meanR)
				maxRe = max (maxRe, meanR)
				minGe = min (minGe, meanG)
				maxGe = max (maxGe, meanG)
				minBe = min (minBe, meanB)
				maxBe = max (maxBe, meanB)
			# Not all of above assigned min and max variables are currently subsequently used :-)
			# and in any case, they should only be done on the first time in		
			
			if stdR + stdG + stdG < 23:
				pieces [7-row][col] = "e"
				print ("empty")
			else:
				#if meanR + meanG + meanB < 250:
				#if meanR + meanG + meanB < splitwb :
				if meanR < splitwb :
					pieces [7-row][col] = "b"
					print ("black", meanR)
				else: 
					pieces [7-row][col] = "w"
					print ("white", meanR)
				
	#print (minRw, maxRw, minGw, maxGw, minBw, maxBw)
	#print (minRe, maxRe, minGe, maxGe, minBe, maxBe)
	#print (minRb, maxRb, minGb, maxGb, minBb, maxBb)
	print ("minRw: ", minRw, ", maxRb: ", maxRb) 
	print ("minGw: ", minGw, ", maxGb: ", maxGb) 
	print ("minBw: ", minBw, ", maxBb: ", maxBb) 
	if firstgbp :
		splitwb = (minRw + maxRb)/2
		#splitwb = (minRw + minGw + minBw + maxRb + maxGb + maxBb) / 2	
		#splitwb = ((minRw + minGw + minBw) * 2/3) + ((maxRb + maxGb + maxBb) / 3)				
	print (minRw + minGw + minBw)
	print (maxRb + maxGb + maxBb)
	print ("splitwb: ", splitwb)
	
	constructmove = list("m    ")
	for row in range(8):	
		for col in range(8):

			if oldpieces[row][col] == "w" and pieces[row][col] == "e":
				constructmove[1] = 	xrevtrans[col+1]
				constructmove[2] = 	str(8-row)
			if	(oldpieces[row][col] == "e" and pieces[row][col] != "e") or \
				(oldpieces[row][col] == "b" and pieces[row][col] == "w") :
				constructmove[3] = 	xrevtrans[col+1]
				constructmove[4] = 	str(8-row)	
			#print ("m", oldpieces[row][col], pieces[row][col])
			if not firstgbp :				
				oldpieces[row][col] = pieces[row][col] # new to old
			else:				
				pieces[row][col] = oldpieces[row][col] # old to new, first (dummy) time	
	
	#print (oldpieces)
	print (pieces)	

	movestr = ''.join(constructmove)
	castles =  castling(board, validkingmoves)
	if castles :
		movestr = castles
	else:
		movestr = ''.join(constructmove)		
	print (movestr)
	firstgbp = 0
	sys.stdout.flush()
	return (movestr)

