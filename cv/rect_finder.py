import cv2
import numpy

# image = cv2.imread("rect.jpg")

# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# frame = cv2.imshow("gray image", gray)

# cv2.waitKey(0)

# gray = cv2.bilateralFilter(gray, 11, 17, 17)

# frame = cv2.imshow("filtered image", gray)

# cv2.waitKey(0)

# edges = cv2.Canny(gray, 100, 200)

# frame = cv2.imshow("edges", edges)

# cv2.waitKey(0)

# (cnts, _) = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# cnts = sorted(cnts, key = cv2.contourArea)[:10]

# screenCnt = None

# # print cnts[0]

# # for c in cnts:
# # 	peri = cv2.arcLength(c, True)
# # 	approx = cv2.approxPolyDP(c, 0.02 * peri, True)

# # 	if len(approx) == 4:
# # 		screenCnt = approx
# # 		break


# cv2.drawContours(image, cnts, -1, (0, 255, 0), 3)

# cv2.imshow("Contour!", image)
# cv2.waitKey(0)

def angle_cos(p0, p1, p2): # takes three points, finds the angle b/w two vectors formed from p0 & p1, p1 & p2
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( numpy.dot(d1, d2) / numpy.sqrt( numpy.dot(d1, d1)*numpy.dot(d2, d2) ) )



def findTarget(rectIndex, hierarchy): # traverses list of rectangles, tries to reach depth for two concentric rects (3 layers in)
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

def drawCentroid(img, contour):
	mean = contour.mean(axis = 0)
	# moments = cv2.moments(contour)
	cx = int(mean[0])
	cy = int(mean[1])
	cv2.circle(img, (cx,cy), 5, (0,0,255), -1)

def processImage(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.bilateralFilter(gray, 11, 25, 25)

	edges = cv2.Canny(gray, 100, 200)

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
				print str(c) + " " + str(hierarchy[0][c])
				rectCnt.append(cnts[c])
				rectIndex.append(c)
	


	# print len(screenCnt)

	# cv2.drawContours(img, screenCnt, -1, (0, 255, 0), 2)
	targetIndex = findTarget(rectIndex,hierarchy) # returns index of target in list of rectangular contours
	print targetIndex
	if targetIndex != -1:
		# cv2.drawContours(img, rectCnt, targetIndex, (0, 0, 255), 2)
		drawCentroid(img, rectCnt[targetIndex])
	cv2.imshow("Contour!", img)

cap = cv2.VideoCapture(0)

while True:
	img = cap.read()[1]
	processImage(img)
	cv2.waitKey(150)

