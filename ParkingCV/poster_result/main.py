import cv2
import pickle
import cvzone
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("D:/Desktop/Class/Senior Design/senior_project-main/dev/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client();

# Video feed
#cap = cv2.VideoCapture('data/videos/snow1.mp4')
img = cv2.imread("data/images/small2.png")  # change your source here
pivot = 500

with open('poster_result/small2', 'rb') as f:
    posList = pickle.load(f)

def checkParkingSpace(imgPro):
    spaceCounter = 0

    for pos in posList:

        smallX = pos[0][0]
        bigX = pos[0][0]
        smallY = pos[0][1]
        bigY = pos[0][1]

        for j in range(1, 4):
            if pos[j][0] < smallX:
                smallX = pos[j][0]
            if pos[j][1] < smallY:
                smallY = pos[j][1]

        for j in range(1, 4):
            if pos[j][0] > bigX:
                bigX = pos[j][0]
            if pos[j][1] > bigY:
                bigY = pos[j][1]

        # x, y = pos

        imgCrop = imgPro[smallY:bigY, smallX:bigX]
        # cv2.imshow(str(x * y), imgCrop)
        count = cv2.countNonZero(imgCrop)

        if count < pivot:
            color = (0, 255, 0)
            thickness = 2
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        for i in range(0,4):
            cv2.line(img, pos[0], pos[1], color, thickness)
            cv2.line(img, pos[1], pos[2], color, thickness)
            cv2.line(img, pos[2], pos[3], color, thickness)
            cv2.line(img, pos[3], pos[0], color, thickness)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))

while True:
    
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 3)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    #cv2.imshow("ImageBlur", imgBlur)
    cv2.imshow("ImageThres", imgMedian)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()