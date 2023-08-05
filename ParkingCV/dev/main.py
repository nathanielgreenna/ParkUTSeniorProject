import cv2
import pickle
import cvzone
import numpy as np
import firebase_admin
from datetime import datetime, timedelta
from firebase_admin import credentials
from firebase_admin import firestore
import pytz
import math

# load custom shape parking lot
with open('CarParkProject/dev/CarParkPos', 'rb') as f:
    posList = pickle.load(f)

def checkParkingSpace(imgPro):
    spaceCount = 0
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

        if count < 5:
            color = (0, 255, 0)
            thickness = 2
            spaceCount += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        for i in range(0,4):
            cv2.line(camera_capture, pos[0], pos[1], color, thickness)
            cv2.line(camera_capture, pos[1], pos[2], color, thickness)
            cv2.line(camera_capture, pos[2], pos[3], color, thickness)
            cv2.line(camera_capture, pos[3], pos[0], color, thickness)

        # cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        # cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
        #                    thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(camera_capture, f'Free: {spaceCount}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))
    return spaceCount

def get_image():
    retval, img = cap.read()
    return img

def round_dt(dt, delta):
    return (datetime.min + math.floor((dt - datetime.min) / delta) * delta).time()

# Video feed
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) 

if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

img_counter = 0

# for i in range (30):
#     temp = get_image()
#     img_name = "opencv_frame_{}.png".format(img_counter)
#     cv2.imwrite(img_name, frame)

camera_capture = get_image()
file = 'CarParkProject/data/images/capture.jpg'
cv2.imwrite(file, camera_capture)  

imgGray = cv2.cvtColor(camera_capture, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY_INV, 25, 16)
imgMedian = cv2.medianBlur(imgThreshold, 3)
kernel = np.ones((3, 3), np.uint8)
imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

spaceCounter = checkParkingSpace(imgDilate)  
file = 'CarParkProject/data/images/result.jpg'
cv2.imwrite(file, camera_capture)  

# cv2.imshow("Image", out)
# cv2.imshow("ImageBlur", imgBlur)
# cv2.imshow("ImageThres", imgMedian)

## write data to database
cred = credentials.Certificate("CarParkProject/dev/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

## Name of the document 
backendname = 'UTLotEngineerJan'
## Name that displays on the app
displayname = 'UT Lot 20'
## You'll need to add a 'coords' field of type GeoPoint manually- it seems like Google isn't proactive on this one

data = {
    'name': displayname, 
    'spotsfilled': len(posList) - spaceCounter,    # will replace this 
    'capacity': len(posList)      # will replace this
}

tz_NY = pytz.timezone('America/New_York') 
datetime_NY = datetime.now(tz_NY)
naive_datetime = datetime_NY.replace(tzinfo=None)
naive_datetime_string = str('%02d' % naive_datetime.time().hour) + ":" + str('%02d' % naive_datetime.time().minute) + ":00"
time_string = str(datetime_NY.weekday())+" "+naive_datetime_string
delta = timedelta(minutes=15)
time_to_update = str(datetime_NY.weekday())+" "+round_dt(naive_datetime,delta).isoformat(timespec='auto')
docs_to_iterate = db.collection('ParkingPlaces').document(backendname).get().to_dict()

for doc in docs_to_iterate:
  if (time_string == time_to_update):
    if (time_to_update == doc):
            docs_to_iterate[time_to_update].pop(2)
            docs_to_iterate[time_to_update].insert(0, len(posList) - spaceCounter)
            data[time_to_update]= docs_to_iterate[time_to_update]
    elif doc != 'capacity' and doc != 'spotsfilled':
        data[doc] = docs_to_iterate[doc]
  elif doc != 'capacity' and doc != 'spotsfilled':
        data[doc] = docs_to_iterate[doc]

db.collection('ParkingPlaces').document(backendname).set(data)