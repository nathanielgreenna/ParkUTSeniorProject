import cv2
import pickle

width, height = 107, 48
clickCount = 0
posList = []
#img = cv2.imread('data/images/parking_lot_1.png')

try:
    with open('dev/CarParkPos', 'rb') as f:
        finalList = pickle.load(f)
except:
    finalList = []


def mouseClick(events, x, y, flags, params):
    global clickCount
    global finalList

    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
        clickCount += 1

        if clickCount >= 4:
            done(posList)
        elif clickCount > 1:
            inProgress(posList)
        
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(finalList):

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

            if smallX < x < bigX and smallY < y < bigY:
                finalList.pop(i)
    
    with open('dev/CarParkPos', 'wb') as f:
        pickle.dump(finalList, f)

def inProgress(posList):
    cv2.line(img, posList[-2], posList[-1], (255,0,0), 1)

def done(posList):
    global clickCount
    global finalList
    
    cv2.line(img, posList[2], posList[3], (255,0,0), 1)
    cv2.line(img, posList[3], posList[0], (255,0,0), 1)

    clickCount = 0
    posEveryFour = []

    for i in range(0, 4): 
        posEveryFour.append(posList[i])

    finalList.append(posEveryFour)
    
    for i in range(0, 4):
        posList.pop()

    # posEveryFour.clear()
    # posList.clear()

while True:    
    img = cv2.imread('data/images/capture.jpg')
    # for i in range(0, length, 4):
    #     vertices = np.array([[posList[i][0], posList[i][1]], [posList[i+1][0], posList[i+1][1]], [posList[i+2][0], posList[i+2][1]], [posList[i+3][0], posList[i+3][1]]], np.int32)
    #     pts = vertices.reshape((-1,1,2))
    #     cv2.polylines(img, [pts], isClosed=True,color=(255,0,0),thickness=5)
    
    # for pos in posList:
    #     cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)

    for i, list in enumerate(finalList):
        cv2.line(img, list[0], list[1], (255,0,0), 1)
        cv2.line(img, list[1], list[2], (255,0,0), 1)
        cv2.line(img, list[2], list[3], (255,0,0), 1)
        cv2.line(img, list[3], list[0], (255,0,0), 1)

    
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
