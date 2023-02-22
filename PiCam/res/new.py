import cv2
from PIL import Image
import pytesseract
 
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print(pytesseract.get_tesseract_version())

 
while(True):
     
    ret, frame = capture.read()

    
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 5)
    # gray_img = cv2.convertScaleAbs(gray_img, alpha=3, beta=-100)
    ret, thresh1 = cv2.threshold(gray_img, 127, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    thresh1 = cv2.medianBlur(thresh1, 11)
    
    # Specify structure shape and kernel size. 
    # Kernel size increases or decreases the area 
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect 
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 100))
    
    # Appplying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    
    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, 
                                                    cv2.CHAIN_APPROX_NONE)

    cont = max(contours, key = cv2.contourArea)

    x, y, w, h = cv2.boundingRect(cont)
    c_img = gray_img[y:y+h, x:x+w]

    # c_img = cv2.bitwise_not(c_img)

    cv2.imshow('b', c_img)
                                                
    cv2.imshow('1', gray_img)
    cv2.imshow('2', thresh1)
    cv2.imshow('3', dilation)

    print(pytesseract.image_to_data(c_img, config=("-c tessedit"
                  "_char_whitelist=HSU"
                  " --psm 10")))

    if cv2.waitKey(1) == 27:
        break
 
capture.release()
cv2.destroyAllWindows()