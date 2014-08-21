import numpy as np
from animate import *
from matplotlib import animation
import matplotlib.pyplot as plt
from pylab import *

def plotResults_old(results):
	"""Plotting - Assumes results holds the coordinate of the end effector

	results - a list of lists of xyz-coordinates. [[[x1,y1,z1],[x2,y2,z2],...]]
	"""
	print "Plotting results - old method"
	for coordinates in results:
		x = []
		y = []
		color = []
		for coordinate in coordinates:
			x += [coordinate[0]]
			y += [coordinate[1]]
			color += ['r']
		fig = plt.figure()
		ax = fig.add_subplot(111)

		scatter(x,y, s=100 ,marker='o', c=color)

		# [ plot( [dot_x,dot_x] ,[0,dot_y]) for dot_x,dot_y in zip(x,y) ] 
		# [ plot( [0,dot_x] ,[dot_y,dot_y]) for dot_x,dot_y in zip(x,y) ]

		left,right = ax.get_xlim()
		low,high = ax.get_ylim()
		arrow( left, 0, right -left, 0)
		arrow( 0, low, 0, high-low) 
		grid()
		show()

def plotResults(results):
	"""Plotting - Assumes results holds the start-end coordinates of each beam.

	results - a list of lists of pairs of xyz-coordinates.
	"""
	folderName = "pics/"
	print "Plotting results: " + folderName
	plt.close()
	color = colorGenerator()
	counter = 0
	for trace in results:
		if len(trace) == 1:
			continue
		ax = plt.axes(xlim=(-5,5), ylim=(-5,5))
		counter += 1
		for state in trace:
			# xlist = []
			# ylist = []
			# for pair in state:
			# 	xlist.extend((pair[0][0], pair[1][0]))
			# 	ylist.extend((pair[0][1], pair[1][1]))
			# 	# Appending None improves performance
			# 	xlist.append(None)
			# 	ylist.append(None)
			for pair in state:
				plt.plot([pair[0][0], pair[1][0]],[pair[0][1], pair[1][1]], color=color())
				plt.plot(None,None)

		# plt.show()
		try:
			plt.savefig(folderName + '%d.png' % counter, bbox_inches='tight')
		except AssertionError:
			pass
		plt.close()
		print counter

def plotResults_mid(results):
	"""Plots the midpoint of the coupler
	"""
	folderName = "pics_mid/"
	print "Plotting midpoint of coupler: " + folderName
	counter = 0
	for trace in results:
		ax = plt.axes(xlim=(-5,5), ylim=(-5,5))
		counter += 1
		if len(trace) == 1:
			continue
		for state in trace:
			coupler = state[1]
			plt.scatter((coupler[0][0]+coupler[1][0])/2, (coupler[0][1]+coupler[1][1])/2)
		try:
				plt.savefig(folderName + '/%d.png' % counter, bbox_inches='tight')
		except AssertionError:
			pass
		plt.close()
		print counter

def colorGenerator():
	"""Returns a method that cycles through four different colors, returning one each time. For plotting four different beams

	Colors:
	red, blue, green, black
	"""
	colors = ['red', 'blue', 'green', 'black']
	counter = {'index':-1}
	def cycle():
		# nonlocal does not exist in python 2.7
		# nonlocal counter
		counter['index'] = (counter['index'] + 1) %4
		return colors[counter['index']]
	return cycle


def plotComponents(results):
	folderName = "pics_components/"
	print "Plotting principal components: " + folderName
	plt.close()
	counter = 0
	for trace in results:
		counter += 1
		if len(trace) == 1:
			continue
		points = getMids(trace)
		points = np.array(points)
		eVal, eVec = components(points)
		v1, v2 = findPrincipalComponents(eVal, eVec)

		ax = plt.axes(xlim=(-5,5), ylim=(-5,5))
		plt.plot(points[:,0], points[:,1])
		ax.arrow(0,0,v1[0],v1[1], color='red')
		ax.arrow(0,0,v2[0],v2[1])

		try:
			plt.savefig(folderName + '%d.png' % counter, bbox_inches='tight')
		except AssertionError:
			pass
		plt.close()
		print counter

def components(points):
	points = np.array(points)
	meanx = np.average(points[:,0])
	meany = np.average(points[:,1])	
	meanz = np.average(points[:,2])
	correctedX = [value-meanx for value in (points[:,0])] 
	correctedY = [value-meany for value in (points[:,1])] 
	correctedZ = [value-meanz for value in (points[:,2])] 

	data = np.array([correctedX, correctedY, correctedZ])
	covData = np.cov(data)
	eigenvalues, eigenvectors = np.linalg.eig(covData)

	return eigenvalues, eigenvectors

def findPrincipalComponents(eigenvalues, eigenvectors):
	"""Given two numpy arrays, one of eigenvalues, the other of the corresponding eigenvalues, 
		This function returns the 2 eigenvectors with the largest eigenvalues
	"""
	value1, value2 = -1.0, -1.0 	#value1 >= value2
	vec1, vec2 = None, None

	# Walk through the eigenvalues and record the two largest 
	for index in range(len(eigenvalues)):
		value = eigenvalues[index]
		if value > value1:
			value2 = value1
			value1 = value
			vec2 = vec1
			vec1 = eigenvectors[index]
		elif value > value2:
			value2 = value
			vec2 = eigenvectors[index]

	return vec1, vec2


def init():
	line.set_data([], [])
	return line,

def animateTrace(results, trace):
	trace = results[trace]
	def animate(i):
		structure = trace[i]
		thisx = [structure[_][0][0] for _ in range(4)]
		thisy = [structure[_][0][1] for _ in range(4)]
		line.set_data(thisx, thisy)
		return line,
	return animate

def animate(results):
	folderName = "animations/"
	print "Animating: " + folderName
	global line
	for index in range(len(results)):
		frames = len(results[index])
		if frames <= 1:
			continue
		plt.close()
		fig = plt.figure()
		ax = plt.axes(xlim=(-5,5), ylim=(-5,5))
		line, = ax.plot([], [], 'o-', lw=2)
		anim = animation.FuncAnimation(fig, animateTrace(results, index), interval=30, init_func=init, frames=frames)
		anim.save(folderName + str(index) + '.mp4', fps=15)
		print index


def filterResults(results):
	"""We only want traces that have more than a minimum number of points and are almost a closed loop
	"""
	with open('results_filtered.txt', 'w') as f:
		for trace in results:
			if len(trace) > 80 and closeEnough(trace):
				s = ""
				for coordinate in trace:
					s += "%s:" % coordinate
				s = s[:-1] + "\n" # drop the last colon and new line
				f.write(s)

def closeEnough(trace, distance = 1.0):
	items = getMids(trace)
	length = len(items) - 1
	dx = items[0][0] - items[length][0]
	dy = items[0][1] - items[length][1]
	dz = items[0][2] - items[length][2]
	d = sqrt(dx**2 + dy**2 + dz**2)
	if d > distance:
		return False
	return True

def getMids(trace):
	mids = [((state[1][0][0]+state[1][1][0])/2, (state[1][0][1]+state[1][1][1])/2, (state[1][0][2]+state[1][1][2])/2) for state in trace]
	return mids