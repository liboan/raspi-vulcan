import cv2
import numpy
import time
import argparse

from turret_control import TurretRotator

parser = argparse.ArgumentParser()
parser.add_argument("-d", action = "store_true",  help = "display camera screens with contours")
args = parser.parse_args()
if args.d:
    print "SHOW"

def angle_cos(p0, p1, p2): # takes three points, finds the angle b/w two vectors formed from p0 & p1, p1 & p2
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( numpy.dot(d1, d2) / numpy.sqrt( numpy.dot(d1, d1)*numpy.dot(d2, d2) ) )

def findTarget(rectIndex, hierarchy): # traverses list of rectangles, tries to reach depth for two concentric rects (3 layers in).
	# 4 [ 8  3  5 -1]
	# 5 [-1 -1  6  4]
	# 6 [-1 -1  7  5]
	# 7 [-1 -1 -1  6]
	depth = 0 # add for every layer it goes down. Looking for 3 concentric contours
	i = 0
	while i < len(rectIndex):
		if hierarchy[0][rectIndex[i]][2] in rectIndex: # if the child exists in rect hierarchy (-1 (no child) will not)
			depth = depth + 1
			if depth == 3:
				return i # return the index of target within list of rectangular contours

			i = rectIndex.index(hierarchy[0][rectIndex[i]][2])  # proceed to child and repeat process
		else: # if there isn't a child or if it doesn't exist, move to next in index
			i = i + 1

	return -1

def drawCentroid(img, contour): #draws the centroid, returns centroid coordinate values
	mean = contour.mean(axis = 0)
	# moments = cv2.moments(contour)
	cx = int(mean[0])
	cy = int(mean[1])
	cv2.circle(img, (cx,cy), 5, (0,0,255), -1)
        return {"x": cx, "y": cy}

def processImage(img): #Looks for target. Returns target coordinates, if one is found.
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.bilateralFilter(gray, 5, 25, 25)

        edges = cv2.Canny(gray, 100, 150)

	cnts, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# cnts = sorted(cnts, key = cv2.contourArea) #don't sort to keep contours & hierarchy lined up
	screenCnt = []
	rectCnt = []
	rectIndex = []

	# print len(cnts)
	# if len(cnts) != 0:
	# 	print hierarchy[0]
	print "________________________"

	for c in xrange(0,len(cnts)):
		peri = cv2.arcLength(cnts[c], True)
		approx = cv2.approxPolyDP(cnts[c], 0.02 * peri, True)

		if len(approx) == 4: # and cv2.isContourConvex(approx):
			cnts[c] = approx.reshape(-1, 2)
			max_cos = numpy.max([angle_cos(cnts[c][i], cnts[c][(i+1) % 4], cnts[c][(i+2) % 4]) for i in xrange(4)])
			#print max_cos

			screenCnt.append(cnts[c])

			if max_cos < 0.2:  #if absolute cosine b/w contours is close to 0, so angle close to 90 degrees
				# print str(c) + " " + str(hierarchy[0][c])
				rectCnt.append(cnts[c])
				rectIndex.append(c)
	


	# print len(screenCnt)

        cv2.drawContours(img, screenCnt, -1, (0, 255, 0), 2)
	targetIndex = findTarget(rectIndex,hierarchy) # returns index of target in list of rectangular contours
	# print targetIndex
        center = None

	if targetIndex != -1:
            # cv2.drawContours(img, rectCnt, targetIndex, (0, 0, 255), 2)
            # ISSUE: This will pick the first target if there are multiple
            center = drawCentroid(img, rectCnt[targetIndex])

        if args.d:
            cv2.imshow("Contour!", img)
            cv2.imshow("Modified", gray)
        return center


using_pi_camera = False


try:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    using_pi_camera = True

    print "Pi camera detected"

    # initialize connection to turret
    try:
        a = TurretRotator(portName = "/dev/ttyACM1", baud = 9600)
    except:
        print "Serial connection failed"

    noneCount = 0 # variable for handling idle behavior
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (320, 240)
    # camera.framerate = 10
    # camera.exposure_mode = 'sports'
    camera.shutter_speed = 8000
    rawCapture = PiRGBArray(camera, size=camera.resolution)
    
    # allow the camera to warmup
    time.sleep(0.1)

    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        start = time.clock()
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array

	# process image
        
        cv2.waitKey(1)

        procStart = time.clock()
        targetCoords = processImage(image)
        print targetCoords
        procFinish = time.clock()
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
        finish = time.clock()
        print (procFinish - procStart)

        if targetCoords == None:
            noneCount = noneCount + 1
            print noneCount
            if noneCount < 100:
                # set turret speed
                try:
                    a.setRotation(-1)
                except:
                    None
            else:
                # set turret speed
                try:
                    a.setRotation(1)
                except:
                    None
            if noneCount > 200:
                noneCount = 0
        else:
            print "seen"
            print numpy.sign(targetCoords["x"] - camera.resolution[0]/2)
            a.setRotation(2*numpy.sign(targetCoords["x"] - camera.resolution[0]/2))
            
except ImportError, e:
    print "No Pi camera module detected, not running on a Pi"
    using_pi_camera = False
    cap = cv2.VideoCapture(0)

    while True:
        img = cap.read()[1]
        procStart = time.clock()
        targetCoords = processImage(img)
        print targetCoords
        procFinish = time.clock()
        print (procFinish - procStart)
	cv2.waitKey(150)

