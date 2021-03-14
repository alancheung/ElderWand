import numpy as np
import cv2

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret,thresh = cv2.threshold(gray,127,255,1)
cv2.imshow('thresh', thresh)

contours, h = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cImage = cv2.drawContours(img, contours, -1, (255, 0, 0), 3)
cv2.imshow('contours', cImage)


for cnt in contours:
    area = cv2.contourArea(cnt)
    x,y,w,h = cv2.boundingRect(cnt)
    wip = img
    cv2.rectangle(wip,(x,y),(x+w,y+h),(0,255,0),2)

    shapeText = 'NO SHAPE'

    approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    print(len(approx))
    if len(approx) == 5:
        shapeText = 'Pentagon'
        cv2.drawContours(img,[cnt],0,255,1)
    elif len(approx) == 3:
        shapeText = 'Triangle'
        cv2.drawContours(img,[cnt],0,(0,255,0),1)
    elif len(approx) == 4:
        shapeText = 'Square'
        cv2.drawContours(img,[cnt],0,(0,0,255),1)
    elif len(approx) == 9:
        shapeText = 'Half-circle'
        cv2.drawContours(img,[cnt],0,(255,255,0),1)
    elif len(approx) > 15:
        shapeText = 'Circle'
        cv2.drawContours(img,[cnt],0,(0,255,255),1)
        
    if shapeText != 'NO SHAPE':
        cv2.putText(wip, shapeText,(x,y-5), cv2.FONT_HERSHEY_SIMPLEX, .5,(255,255,255),1,cv2.LINE_AA)
    cv2.imshow('WIP', wip)
    cv2.waitKey(0)

cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()