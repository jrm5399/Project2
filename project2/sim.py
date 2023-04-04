# John Murphy
# CDA 5106
# Project 2

import sys
from os import path
import re

#Handles file
def file(trace):
	#Grab contents from txt file
	with open(trace, encoding='utf-8-sig') as f : 
		text = f.read()
	words = re.split(r'\W+', text)
	words = text.split()
	return words


#grabbing parameters
def params(args):
	params = [[x for x in args[i]] for i in range(1,len(args))]
	return ["".join(arr) for arr in params]

#Grabs the TN and the HEX
def TN_HEX(file):
	TN = [x for x in file if x is 't' or x is 'n']
	tn_set = set(TN)
	HEX = [x for x in file if x not in tn_set]
	return TN, HEX

#PREDICTORS
def smith(bits,TN):
	guess = ''
	wrong = 0
	split = 2 ** (bits - 1)
	counter = split

	#loops through TN values from list
	for vals in TN:
		if counter >= split:
			guess = 't'
			if vals != guess:
				wrong += 1
		#Simple if counter greater than split then guess T otherwise guess N
		else:
			guess = 'n'
			if vals != guess:
				wrong += 1
				
		if vals == 't' and counter < (2 ** bits) - 1:
			counter += 1
		if vals == 'n' and counter > 0:
			counter -= 1


	return len(TN), wrong, counter

def gshare(values, m, n):
	GBHR = ('0' * n)
	TEMP = GBHR.zfill(m)
	counter = [4] * (2 ** m)
	guess = ''
	wrong = 0

	#loop through TN and HEX values from list
	for tn, val in values:
		binary = bin(int(val,16))[:-2]		#convert to binary and cut off last 2 bits
		binary = binary[-m:]				#cut off from -m
		index = int(TEMP,2) ^ int(binary,2)	#XOR results

		#Guess T if counter sub index is 4 or higher otherwise guess N
		if counter[index] >= 4:
			guess = 't'
			if guess != tn:
				wrong += 1

		else:
			guess = 'n'
			if guess != tn:
				wrong += 1

		#Handles updating GBHR
		if tn == 't':
			GBHR = "1" + GBHR[:-1]
			TEMP = GBHR.zfill(m)
			if counter[index] < 7:
				counter[index] += 1

		if tn == 'n':
			GBHR = "0" + GBHR[:-1]
			TEMP = GBHR.zfill(m)
			if counter[index] > 0:
				counter[index] -= 1

	return counter, wrong

#Bimodal
def bimodal(values, m):
	counter = [4] * (2 ** m)
	guess = ''
	wrong = 0

	#Loop through file values
	for tn, val in values:
		binary = bin(int(val,16))[:-2]
		binary = binary[-m:]
		index = int(binary,2)

		#Creates our Guess T or N
		if counter[index] >= 4:
			guess = 't'
			if guess != tn:
				wrong += 1

		else:
			guess = 'n'
			if guess != tn:
				wrong += 1

		#Update counter table
		if tn == 't':
			if counter[index] < 7:
				counter[index] += 1

		if tn == 'n':
			if counter[index] > 0:
				counter[index] -= 1


	return counter, wrong

#############HYBRID###############

#Gshare without looping <Used for Hybrid>
def hybrid_gshare(tn,val, m, n, GBHR,counter):
	guess = ''
	TEMP = GBHR.zfill(m)

	binary = bin(int(val,16))[:-2]
	binary = binary[-m:]
	index = int(TEMP,2) ^ int(binary,2)

	if counter[index] >= 4:
		guess = 't' 
	else:
		guess = 'n'

	if tn == 't':
		GBHR = "1" + GBHR[:-1]
		TEMP = GBHR.zfill(m)

	if tn == 'n':
		GBHR = "0" + GBHR[:-1]
		TEMP = GBHR.zfill(m)

	return guess, GBHR, index

#Bimodal without looping <Used for Hybrid>
def hybrid_bimodal(tn,val, m, counter):
	guess = ''
	binary = bin(int(val,16))[:-2]
	binary = binary[-m:]
	index = int(binary,2)


	if counter[index] >= 4:
		guess = 't' 
	else:
		guess = 'n'

	return guess, index


#Updates counter tables for gshare and bimodal in Hybrid
def update_counter(counter, index, tn):
	if tn == 't' and counter[index] < 7:
		counter[index] += 1

	if tn == 'n' and counter[index] > 0:
		counter[index] -= 1

	return counter

#Hybrid
def hybrid(values, k, m1, n, m2):
	choose_table = [1] * (2 ** k)
	bimodal_counter = [4] * (2 ** m2)
	gshare_counter = [4] * (2 ** m1)

	GBHR = ('0' * n)
	guess = ''
	wrong = 0
	

	#Loops through file values
	for tn, val in values:
		binary = bin(int(val,16))[:-2]
		binary = binary[-k:]
		index = int(binary,2)

		#creates all values for gshare and bimodal
		gshare, GBHR,gindex = hybrid_gshare(tn,val, m1, n, GBHR,gshare_counter)
		bimodal, bindex = hybrid_bimodal(tn,val, m2, bimodal_counter)


		#Grab the value and decides to use gshare or bimodal
		if choose_table[index] > 1:
			guess = gshare
			gshare_counter = update_counter(gshare_counter, gindex, tn)

		else:
			guess = bimodal
			bimodal_counter = update_counter(bimodal_counter, bindex, tn)

		#Update wrong
		if guess != tn:
			wrong += 1



		#If only gshare is correct
		if (gshare == tn and bimodal != tn) and choose_table[index] < 3:
			choose_table[index] += 1

		#If only bimodal is correct
		if (bimodal == tn and gshare != tn) and choose_table[index] > 0:
			choose_table[index] -= 1




	return choose_table, wrong, gshare_counter, bimodal_counter

###Main###

#Grabbing parameters
params = params(sys.argv)

#SMITH
if params[0] == 'smith' and int(params[1]) > 0 and path.isfile(params[2]) == True:
	f = file(params[2])				#Getting file
	TN, _ = TN_HEX(f)				#Grabbing TN values
	total, wrong,counter = smith(int(params[1]), TN)	#Results of smith machine
	print("OUTPUT")
	print("number of predictions: ", total)
	print("number of misspredictions: ", wrong)
	print("misprediction rate: ", str(round(wrong/total*100, 2)) + "%")
	print("FINAL COUNTER CONTENT: ", counter)
	#print("MISSPRED", wrong/total*100)


#GSHARE
if params[0] == 'gshare' and int(params[1]) > 0 and int(params[2]) > 0 and path.isfile(params[3]) == True:
	f = file(params[3])				#Getting file
	TN, HEX = TN_HEX(f)				#Grabbing TN and HEX values

	count, wrong = gshare(zip(TN, HEX), int(params[1]), int(params[2]))

	print("OUTPUT")
	print("number of predictions: ", len(TN))
	print("number of misspredictions: ", wrong)
	print("misprediction rate: ", str(round((wrong/len(TN) * 100),2)) +  "%")
	print("FINAL GSHARE CONTENTS")
	[print(i,"	", x) for i,x in enumerate(count)]
	#print("(", wrong/len(TN)*100, ", ",params[2]," )", ",")

#BIMODAL
if params[0] == 'bimodal' and int(params[1]) > 0 and path.isfile(params[2]) == True:
	f = file(params[2])				#Getting file
	TN, HEX = TN_HEX(f)				#Grabbing TN and HEX values

	count, wrong = bimodal(zip(TN, HEX), int(params[1]))

	print("OUTPUT")
	print("number of predictions: ", len(TN))
	print("number of misspredictions: ", wrong)
	print("misprediction rate: ", str(round((wrong/len(TN) * 100),2)) +  "%")
	print("FINAL BIMODAL CONTENTS")
	[print(i,"	", x) for i,x in enumerate(count)]


#HYBRID
if params[0] == 'hybrid' and int(params[1]) > 0 and int(params[2]) > 0 and int(params[3]) and int(params[4]) and path.isfile(params[5]) == True:
	f = file(params[5])				#Getting file
	TN, HEX = TN_HEX(f)				#Grabbing TN and HEX values

	count, wrong,gcount,bicount = hybrid(zip(TN, HEX), int(params[1]), int(params[2]), int(params[3]), int(params[4]))

	print("OUTPUT")
	print("number of predictions: ", len(TN))
	print("number of misspredictions: ", wrong)
	print("misprediction rate: ", str(round((wrong/len(TN) * 100),2)) +  "%")
	print("FINAL CHOOSER CONTENTS")
	[print(i,"	", x) for i,x in enumerate(count)]
	print("FINAL GSHARE CONTENTS")
	[print(i,"	", x) for i,x in enumerate(gcount)]
	print("FINAL BIMODAL CONTENTS")
	[print(i,"	", x) for i,x in enumerate(bicount)]
	#print(f"MISSPRED", "(", wrong/total*100, " {params[2]} )", ",")
