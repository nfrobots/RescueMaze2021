import cv2
from PIL import Image
import pytesseract
 
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print(pytesseract.get_tesseract_version())

 
while(True):
     
    ret, frame = capture.read()

    # frame = cv2.imread("./data/test.jpg")
    
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.medianBlur(gray_img, 11)

    thresh, bw_img = cv2.threshold(gray_img, 80, 255, cv2.THRESH_BINARY)

    new_img = bw_img

    height, width = frame.shape[:2]


    box_data = pytesseract.image_to_boxes(new_img, config='--psm 10 -c tessedit_char_whitelist=SHU')
    
    if box_data:
        box_data = box_data.split(' ')

        frame = cv2.rectangle(frame, (int(box_data[1]), height - int(box_data[2])), (int(box_data[3]), height - int(box_data[4])), thickness=2, color=(255, 0, 0))
        print(box_data)

        
    cv2.imshow('video', frame)
    cv2.imshow('2', new_img)
     
    if cv2.waitKey(1) == 27:
        break
 
capture.release()
cv2.destroyAllWindows()