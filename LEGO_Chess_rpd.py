#!/usr/bin/env python
#
# This module copyright 2018 Richard Day, chess@gotobiz.co.uk
# This code must not be resold, or redistributed in any way without express permission

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import CBstate

from subprocess import call

# Obtain required libraries
import serial
import time
from math import sqrt, atan
from lib_al5_2D_IK import al5_2D_IK, al5_moveMotors

# Constants - Speed in mu s/s, 4000 is roughly equal to 360 degrees/s or 60 RPM
#           - A lower speed will most likely be more useful in real use, such as 100 mu s/s (~9 degrees/s)
CST_SPEED_MAX = 4000
CST_SPEED_DEFAULT = 250

# Create and open a serial port
sp = serial.Serial('/dev/ttyACM0', 9600)

# Set default values
AL5_DefaultPos = (1500, 1500, 1500, 500, 1500, 1500);
cont = True
defaultTargetX = 4
defaultTargetY = 4
defaultTargetZ = 90
defaultTargetG = 90
defaultTargetWA = 0
defaultTargetWR = 90
defaultTargetShoulder = 90
defaultTargetElbow = 90
targetX = defaultTargetX
targetY = defaultTargetY
targetZ = defaultTargetZ
targetG = defaultTargetG
targetWA = defaultTargetWA
targetWR = defaultTargetWR
index_X = 0
index_Y = 1
index_Z = 2
index_G = 3
index_WA = 4
index_WR = 5
targetXYZGWAWR = (targetX, targetY, targetZ, targetG, targetWA, targetWR)
targetQ = "y"
motors_SEWBZWrG = (90, 90, 90, 90, 90, 90)
speed_SEWBZWrG = (CST_SPEED_DEFAULT, CST_SPEED_DEFAULT, CST_SPEED_DEFAULT, CST_SPEED_DEFAULT, CST_SPEED_DEFAULT, CST_SPEED_DEFAULT)

axistorow0forangle = 3.8 - 0.375
axistorow0 = 3.8 - 0.375
squaresize = 1.37795	# inches
rtod = 57.295779	# Radians to degrees constant
cmtoin = 0.393701	# cm to inches
stickout = 1.3 + 0.3 + 0.2		# inches
#Gfudge = 4.1
#Gfudge = 3.5
#Gfudge = 3.2
Gfudge = 2.9
piecetype = "p"
pickheightadj = -0.27	# inches
extraheight = 0.8 + 0.8
extrawidth = -30 + 35 + 5

xmtrans = {
	"a": 3.5,
	"b": 2.5,
	"c": 1.5,
	"d": 0.5,
	"e": -0.5,
	"f": -1.5,
	"g": -2.5,
	"h": -3.5
}

xtrans = {
	"a": 0,
	"b": 1,
	"c": 2,
	"d": 3,
	"e": 4,
	"f": 5,
	"g": 6,
	"h": 7
}
pieceheights = {
	"p": 3.2, 	# cm
	"r": 3.6,
	"n": 4.0,
	"b": 4.9,
	"q": 5.7,
	"k": 6.3
}
piecewidths = {
	"p": 85, 	# degrees
	"r": 81,
	"n": 95,
	"b": 80,
	"q": 75,
	"k": 77
}

gameresult = ("No result", "Checkmate! White wins", "Checkmate! Black wins", "Stalemate", "50 moves rule", "3 repetitions rule")
lastmovetype = (
	"Normal",
	"En passant available",
	"Capture en passant",
	"Pawn promoted",
	"Castle on king's side",
	"Castle on queen's side")
	
firsttime = 1

def speaker(text):
	cmd_beg= 'espeak -s100 '
	cmd_end= ' | aplay /home/pi/Desktop/Text.wav  2>/dev/null' # To play back the stored .wav file and to dump the std errors to /dev/null
	cmd_out= '--stdout > /home/pi/Desktop/Text.wav ' # To store the voice file
	text = text.replace(' ', '_')
	call([cmd_beg+cmd_out+text], shell=True)
	call(["aplay", "/home/pi/Desktop/Text.wav"])

def idleall():
	# Set all motors to idle/unpowered (pulse = 0)
	print("< Idling motors... >");
	for i in range(0,6):
		print(("#" + str(i) + " P" + str(0) + "\r").encode())
		sp.write(("#" + str(i) + " P" + str(0) + "\r").encode())
	print("< Done >")

def armangle (squarename):
	#  x,y on board
	x = xmtrans[squarename[0:1]] * squaresize
	y = (8 - int(squarename[1:2])) * squaresize
	return (Gfudge + 90 + (rtod * (atan(x/(y+axistorow0forangle)))))

def armlength (squarename):
	x = xmtrans[squarename[0:1]] * squaresize
	y = (8 - int(squarename[1:2])) * squaresize
	print (y)
	print ((sqrt(x**2 + (y+axistorow0)**2))+stickout)
	return (((sqrt(x**2 + (y+axistorow0)**2))+stickout)*0.84)
	
def adjforlen(armlen):
	if armlen < 4:
		return(0.2)
	elif armlen < 7:
		return(0)
	elif armlen < 11:
		return(-0.2)
	else:
		return(0)

def movemotors(motors_SEWBZWrG):		
	# Perform IK
	errorValue = al5_2D_IK(targetXYZGWAWR)
	if isinstance(errorValue, tuple):
		motors_SEWBZWrG = errorValue
	else:
		print(errorValue)
		motors_SEWBZWrG = (defaultTargetShoulder, defaultTargetElbow, defaultTargetWA, defaultTargetZ, defaultTargetG, defaultTargetWR)

	# Move motors
	errorValue = al5_moveMotors(motors_SEWBZWrG, speed_SEWBZWrG, sp)
	time.sleep(2)

def waiter():
	while (sp.write(("Q\r").encode()) == "+"):	
		print ("+", end="")	
		time.sleep(0.3)
	print (".")

def quitter():
	print ("Game ends")
	idleall() 
	time.sleep(3)	
	quit()
	
def closejaws(piecetype):
	global targetXYZGWAWR
	jawsize = piecewidths[piecetype] + 15 + extrawidth
	targetXYZGWAWR = (targetXYZGWAWR[0], targetXYZGWAWR[1], targetXYZGWAWR[2], jawsize, targetXYZGWAWR[4], targetXYZGWAWR[5])
	movemotors(motors_SEWBZWrG)
	time.sleep(1.4)

def openjaws():
	global targetXYZGWAWR
	targetXYZGWAWR = (targetXYZGWAWR[0], targetXYZGWAWR[1], targetXYZGWAWR[2], 42+extrawidth, targetXYZGWAWR[4], targetXYZGWAWR[5])
	movemotors(motors_SEWBZWrG)
	#waiter()

def moveXYZGWA(X, Y, Z, G, WA):
	global targetXYZGWAWR
	targetXYZGWAWR = (float(X), float(Y), float(Z), float(G), float(WA), targetXYZGWAWR[5])
	movemotors(motors_SEWBZWrG)
	#waiter()
	
def movearm(X, Z):
	global targetXYZGWAWR	
	targetXYZGWAWR = (float(X), targetXYZGWAWR[1], float(Z), targetXYZGWAWR[3], targetXYZGWAWR[4], targetXYZGWAWR[5])
	movemotors(motors_SEWBZWrG)
	#waiter()
	
def moveXY(toheight):
	global targetXYZGWAWR
	targetXYZGWAWR = (targetXYZGWAWR[0], float(toheight), targetXYZGWAWR[2], targetXYZGWAWR[3], -90, targetXYZGWAWR[5])
	movemotors(motors_SEWBZWrG)
	#waiter()
			
def pickuppiece(pickheight, piecetype, armlen):
	global targetXYZGWAWR
	#saveWA = targetXYZGWAWR[4]
	targetXYZGWAWR = (targetXYZGWAWR[0], targetXYZGWAWR[1], targetXYZGWAWR[2], targetXYZGWAWR[3], -75, targetXYZGWAWR[5])	
	movemotors(motors_SEWBZWrG)
	#waiter()	
	#targetXYZGWAWR = (targetXYZGWAWR[0], targetXYZGWAWR[1], targetXYZGWAWR[2], targetXYZGWAWR[3], -90, targetXYZGWAWR[5])
	# was -100
	moveXY(pickheight + extraheight + adjforlen(armlen))	# go down
	closejaws(piecetype)
	moveXY (6)	# go up
	
def droppiece(dropheight, armlen):
	global targetXYZGWAWR
	targetXYZGWAWR = (targetXYZGWAWR[0], targetXYZGWAWR[1], targetXYZGWAWR[2], targetXYZGWAWR[3], -75, targetXYZGWAWR[5])	
	movemotors(motors_SEWBZWrG)
	moveXY(dropheight + extraheight + adjforlen(armlen))	# go down
	openjaws()
	moveXY(5 + extraheight) 	# go up
	
def takepiece (X, Z, targetpiece):
	Xgraveyard = armlength("h9") + 0.5
	Zgraveyard = armangle("h9")
	movearm (X, Z)
	tpickheight = (pieceheights[targetpiece.lower()] * cmtoin) + pickheightadj
	print (tpickheight)
	pickuppiece(tpickheight, targetpiece, X)
	movearm (Xgraveyard, Zgraveyard)
	time.sleep(1.5)
	#Xgraveyard += 1
	#if Xgraveyard > 8:
		#Xgraveyard = 1
	droppiece(tpickheight, Xgraveyard)
	gohome()

def iscastling (sourcesquarename):
	sourceX = armlength(sourcesquarename)
	sourceZ = armangle(sourcesquarename)
	if CBstate.cbstate == 4:
		rsourceX = armlength("h8")
		rsourceZ = armangle("h8")
		rtargetX= armlength("f8")
		rtargetZ= armangle("f8")
	elif CBstate.cbstate == 5:
		rsourceX = armlength("a8")
		rsourceZ = armangle("a8")
		rtargetX= armlength("d8")
		rtargetZ= armangle("d8")
	else:
		return()
	print("Castling " + sourcesquarename)	
	movearm (rsourceX, rsourceZ)
	pickrheight = ((pieceheights["r"]) * cmtoin) + pickheightadj
	pickuppiece(pickrheight, "r", rsourceX)
	movearm (rtargetX, rtargetZ)
	droppiece(pickrheight - 0.1, rtargetX)	
	gohome()
	
def enpassant (sourcesquarename):
	if CBstate.cbstate == 2:
		epsquarename = sourcesquarename[0:1] + str(int(sourcesquarename[1:2] - 1))
		print (epsquarename)
		takepiece(epsquarename)

def updateboard(source, target, boardbefore):
	sourcex = xtrans[source[0]]
	sourcey = 8-int(source[1])
	targetx = xtrans[target[0]]
	targety = 8-int(target[1])
	print (boardbefore)
	boardbefore[targety][targetx] = boardbefore[sourcey][sourcex] 
	boardbefore[sourcey][sourcex] = "."	
	print (boardbefore)	
	return (boardbefore)

def movepiece (sourcesquarename, targetsquarename, boardbefore):
	sourceX = armlength(sourcesquarename)
	sourceZ = armangle(sourcesquarename)
	targetX = armlength(targetsquarename)
	targetZ = armangle(targetsquarename)
	
	sourcex = xtrans[sourcesquarename[0]]
	sourcey = 8-int(sourcesquarename[1])
	targetx = xtrans[targetsquarename[0]]
	targety = 8-int(targetsquarename[1])
	
	if boardbefore[targety][targetx] != ".":		# row, column
		#print (boardbefore)
		print("Take piece!")
		takepiece(targetX, targetZ, boardbefore[targety][targetx].lower())

	#raw_input("now move to piece Enter:") 
	movearm(sourceX, sourceZ)
	#raw_input("now pick up:")
	sourcepiece = boardbefore[sourcey][sourcex].lower()
	print(sourcepiece)
	pickheight = ((pieceheights[sourcepiece]) * cmtoin) + pickheightadj
	print(pickheight)
	pickuppiece(pickheight, sourcepiece, sourceX)

	#raw_input("now move piece to target. Enter:") 
	movearm(targetX, targetZ)
	#raw_input("now drop:")
	print (pickheight)
	droppiece(pickheight - 0.1, targetX)		
	#raw_input("now go home")
	gohome()
	
	iscastling(sourcesquarename)
	enpassant (sourcesquarename)

def calibrategripper():
	global targetXYZGWAWR
	while True:
		angle = raw_input("Provide angle in degrees, or q:")
		if angle == "q":
			quitter()
		targetXYZGWAWR = (targetXYZGWAWR[0], targetXYZGWAWR[1], targetXYZGWAWR[2], float(angle), targetXYZGWAWR[4], targetXYZGWAWR[5])
		movemotors(motors_SEWBZWrG)
		waiter()

def park():
	try:
		moveXYZGWA(2.5, 7.0, 90 + Gfudge, 42+extrawidth, -110)
		#waiter()
		#quitter()
	except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
	    quitter()

def gohome():
	park()

def init():
	# adjust for non-centering
	sp.write(("#0 PO99\r").encode())  # offset base
	sp.write(("#1 PO-60\r").encode())  # offset shoulder 
	sp.write(("#2 PO-29\r").encode())  # offset elbow 
	sp.write(("#3 PO85\r").encode())  # offset wrist 
	# Set the arm to default centered position (careful of sudden movement)
	print("Default position is " + str(AL5_DefaultPos) + ".")
	for i in range(0,6):
		print(("#" + str(i) + " P" + str(AL5_DefaultPos[i]) + "\r").encode())
		sp.write(("#" + str(i) + " P" + str(AL5_DefaultPos[i]) + "\r").encode())
		time.sleep(0.3)
		#xxx = raw_input("?")
	#quitter()
	time.sleep(0.7)
	gohome()



#def inittest():
	#init1()
	#test
	#calibrategripper()	
	#boardbefore = [
	#			['r','n','b','q','k','b','n','r'],
	#			['p']*8,
	#			['.']*8,
	#			['.']*8,
	#			['.']*8,
	#			['.']*8,
	#			['P']*8,
	#			['R','N','B','Q','K','B','N','R']
	#			]
	#while True:
	#	smove = raw_input("Provide move, e.g. e2e4, or q:")
	#	if smove == "q":
	#		quitter()
	#	movepiece(smove[0:2], smove[2:4], boardbefore)
