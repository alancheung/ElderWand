from collections import deque
import numpy as np
import cv2
import imutils
import time

def detectSpell(canvas):
    spell = ''

    contours, h = cv2.findContours(canvas, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1:]

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        numSides = len(approx)
        if numSides == 5:
            spell = 'pentagon'
            break
        elif numSides == 3:
            spell = 'triangle'
            break
        elif numSides == 4:
            spell = 'square'
            break
        elif numSides == 9:
            spell = 'half-circle'
            break
        elif numSides >= 15:
            spell = 'circle'
            break
    return spell

# loop over the set of tracked points so that we can draw a line for human eyes.
def drawTrackingLine(canvas):
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, draw the connecting lines
        cv2.line(canvas, pts[i - 1], pts[i], (255, 0, 0), thickness = 5)
    # Then draw the last point to the first point in case they never finished the shape.    
    cv2.line(canvas, pts[len(pts) - 1], pts[0], (0, 0, 255), thickness = 5)

# The list of currently tracked points
pts = deque(maxlen=32)
kernel = np.ones((5,5),np.uint8)
thresh = 160

# Initialize camera with 2s delay for camera to warm up
camera = cv2.VideoCapture(0)
time.sleep(2)

imageSize = (720, 720)
lastSpell = ''
spellCount = 0
while 1:
    # read from camera
    (grabbed, frame) = camera.read()
    # frame = imutils.rotate(frame, angle=0)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # TODO determine if this completely necessary
    cv2.equalizeHist(frame_gray)

    # resize image for faster processing.
    # frame_gray = cv2.resize(frame_gray, (120, 120), interpolation = cv2.INTER_CUBIC)
    frame = cv2.resize(frame, imageSize)
    frame_gray = cv2.resize(frame_gray, imageSize)

    # find the point by looking for pixels >threshold
    th, frame_gray = cv2.threshold(frame_gray, thresh, 255, cv2.THRESH_BINARY)

    # At least 1 pass is needed to create centroid for recognition
    # This approach may not be needed if Hough circles are used.
    frame_gray = cv2.dilate(frame_gray, kernel, iterations = 1)
 
    # find contours in the mask
    # countours meaning the binary area (aka in our case, the white dot).
    cnts = cv2.findContours(frame_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
 
	# only proceed if at least one contour was found
    if len(cnts) > 0:
        # TODO maybe should change this to assume the cnt that is closest to center of frame is the most applicable instead of max.
		# find the most applicable contour in the mask (in this case the largest), then use it to compute the minimum enclosing circle and if it matches a known spell.
        mostLikelyWandTip = max(cnts, key=cv2.contourArea)

        # find bounds of circle in order to show on screen. Not applicable in this sense
        # ((x, y), radius) = cv2.minEnclosingCircle(c)

        # Moments help find centers of points
        # https://www.learnopencv.com/find-center-of-blob-centroid-using-opencv-cpp-python/
        M = cv2.moments(mostLikelyWandTip)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

	# update the points queue
    pts.appendleft(center)

    # TODO change the threshold of points to be configurable value??
    # detect likely spell if the number of tracked points is >=50%
    canvas = np.zeros(imageSize, np.uint8)
    drawTrackingLine(canvas)
    numPointsTracked = sum(1 for p in pts if p is not None)
    if numPointsTracked >= 16:
        print('Shape is probable!')

        ## Get minimum image to verify
        #fullCnts = cv2.findContours(frame_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        #(x,y), radius = cv2.minEnclosingCircle(cnts[0])

        ## Debug, draw circle around image.
        #cv2.circle(frame_gray, (int(x), int(y)), int(radius), (0, 255, 255), 2)

        spell = detectSpell(canvas)
        if spell != '':
            if spellCount >= 10:
                print(f'Detected {spell} for last 32 frames!')
                cv2.waitKey(0)
                pts = deque(maxlen=32)
                spellCount = 0
                lastSpell = ''
            elif spell == lastSpell:
                spellCount += 1
            else:
                print(f'Last spell "{lastSpell}" detected for {spellCount} frames but detected new spell "{spell}"')
                spellCount = 0
                lastSpell = spell
        else:
            print('no spell detected in image')

    # loop and show frame
    cv2.imshow('raw', frame)
    cv2.imshow('grey', frame_gray)
    cv2.imshow('points', canvas)
    keyPressed = cv2.waitKey(1) & 0xFF
    if keyPressed == ord('q'):
        break
    # increase threshold if 't' is pressed, decrease for 'g'
    elif keyPressed == ord('t'):
        thresh = thresh + 10
        print('Threshold:' + str(thresh))
    elif keyPressed == ord('g'):
        thresh = thresh - 10
        print('Threshold:' + str(thresh))

    
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
