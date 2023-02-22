import cv2
import numpy as np


 
def nothing(x):
    pass
 
# Open the camera
cap = cv2.VideoCapture(0) 

TH_RED_LOWER        = np.array([0, 95, 95])
TH_RED_HIGHER       = np.array([14, 255, 255])

TH_YELLOW_LOWER     = np.array([14, 95, 95])
TH_YELLOW_HIGHER    = np.array([41, 255, 255])

TH_GREEN_LOWER      = np.array([41, 60, 55])
TH_GREEN_HIGHER     = np.array([88, 255, 255])

cv2.namedWindow('image')

# cv2.createTrackbar('sigma', 'image', 0, 10, lambda: None)
# cv2.createTrackbar('ksize', 'image', 0, 40, lambda: None)

while(True):
    ret, ogframe = cap.read()
    ogframe = cv2.resize(ogframe, (300, 225))
    # print(ogframe.shape)
    frame = ogframe
    # ks = 2 * cv2.getTrackbarPos('ksize', 'image') + 1
    # sigm = cv2.getTrackbarPos('sigma', 'image')
    # frame = cv2.GaussianBlur(frame, (ks, ks), sigm)
    frame = cv2.medianBlur(frame, 23)
    # frame = cv2.medianBlur(frame, ks)

    # convert color to hsv because it is easy to track colors in this color model
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    red_mask = cv2.inRange(hsv, TH_RED_LOWER, TH_RED_HIGHER)
    yellow_mask = cv2.inRange(hsv, TH_YELLOW_LOWER, TH_YELLOW_HIGHER)
    green_mask = cv2.inRange(hsv, TH_GREEN_LOWER, TH_GREEN_HIGHER)
    
    red_frame = cv2.bitwise_and(frame, frame, mask=red_mask)
    yellow_frame = cv2.bitwise_and(frame, frame, mask=yellow_mask)
    green_frame = cv2.bitwise_and(frame, frame, mask=green_mask)

    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = max(contours, key = cv2.contourArea) if contours else []
    cv2.drawContours(ogframe, contours, -1, (0, 0, 255), 3)
    contours, hierarchy = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = max(contours, key = cv2.contourArea) if contours else []
    cv2.drawContours(ogframe, contours, -1, (0, 255, 255), 3)
    contours, hierarchy = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = max(contours, key = cv2.contourArea) if contours else []
    cv2.drawContours(ogframe, contours, -1, (0, 255, 0), 3)

    cv2.imshow('ogimage', ogframe)
    cv2.imshow('image', frame)
    cv2.imshow('red', red_frame)
    cv2.imshow('yellow', yellow_frame)
    cv2.imshow('green', green_frame)
    

    if cv2.waitKey(1) == 27:
        break
 
cap.release()
cv2.destroyAllWindows()