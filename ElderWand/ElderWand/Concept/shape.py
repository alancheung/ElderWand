import numpy as np
import cv2

img = cv2.imread('C:/Users/cheun/Desktop/CodeLibrary/ElderWand/ElderWand/ElderWand/WandTracker/Shapes/circle/shape1-1.png')
canvas = np.zeros(img.shape, np.uint8)

count = 0

n = 1
while True:
    img = cv2.imread('C:/Users/cheun/Desktop/CodeLibrary/ElderWand/ElderWand/ElderWand/WandTracker/Shapes/circle/shape1-' + str(n) + '.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret,thresh = cv2.threshold(gray,127,255,1)
    cv2.imshow('thresh', thresh)

    contours, h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1:]
    cImage = cv2.drawContours(canvas, contours, -1, (255, 0, 0), 3)
    cv2.imshow('contours', cImage)

    lengths = []
    found = False
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)

        approximationLength = len(approx)
        lengths.append(approximationLength)
        # print('Approximation of image ' + str(n) + ' has contour length of ' + str(approximationLength))

        shapeText = 'NO SHAPE'
        if approximationLength == 5:
            shapeText = 'Pentagon'
        elif approximationLength == 3:
            shapeText = 'Triangle'
        elif approximationLength == 4:
            shapeText = 'Square'
        elif approximationLength == 9:
            shapeText = 'Half-circle'
        elif approximationLength >= 15:
            shapeText = 'Circle'
            
        x,y,w,h = cv2.boundingRect(cnt)
        if shapeText != 'NO SHAPE':
            # print('Image ' + str(n) + ' found a shape of ' + shapeText + ' out of ' + str(len(contours[1:])) + ' contour shapes.')
            color = (0, 255, 0)
            cv2.putText(img, f'{shapeText} ({approximationLength})', (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            count += 1
            found = True
            # break
        else:
            color = (0, 0, 255)
            cv2.putText(img, str(approximationLength), (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.rectangle(img, (x,y), (x+w,y+h), color, 1)

    if found == False:
        print('No shape, max lengths: ' + str(max(lengths)))

    cv2.imshow('img',img)
    key = cv2.waitKey(0)
    if key == ord('b'):
        n -= 1
    elif key == ord('q'):
        break
    else:
        n += 1

    if n < 1 or n > 70:
        break

cv2.destroyAllWindows()
print('Correct count: ' + str(count) + ' / 69')