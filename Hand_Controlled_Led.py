import cv2  # OpenCV
import mediapipe  # For the hand module
import numpy  # Good Old Numpy
import time  # To track the time
import serial

ArduinoSerial = serial.Serial('com10', 9600, timeout=1)
time.sleep(2)
print("connection_established")

# CONSTANTS
motorSpeed = 1
thumbTipId = 4
indexTipId = 8

# VARIABLES
rightSpeed = 0.0
leftSpeed = 0.0
speedRatio = 0.0

# cap2 = cv2.VideoCapture('http://192.168.1.54:8080/video')  # Defining the USB camera
cap = cv2.VideoCapture(0)  # Defining the Video Recording device(Webcam)
initHand = mediapipe.solutions.hands  # Initializing mediapipe
# Object of mediapipe with "arguments for the hands module"
mainHand = initHand.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
draw = mediapipe.solutions.drawing_utils  # Object to draw the connections between each finger index


def handLandmarks(colorImg):
    landmarkList = []  # Default values if no landmarks are tracked
    landmarkPositions = mainHand.process(colorImg)  # Object for processing the video input
    landmarkCheck = landmarkPositions.multi_hand_landmarks  # Stores the out of the processing object (returns False on empty)
    if landmarkCheck:  # Checks if landmarks are tracked
        for hand in landmarkCheck:  # Landmarks for each hand
            for index, landmark in enumerate(
                    hand.landmark):  # Loops through the 21 indexes and outputs their landmark coordinates (x, y, & z)
                draw.draw_landmarks(img, hand,
                                    initHand.HAND_CONNECTIONS)  # Draws each individual index on the hand with connections
                h, w, c = img.shape  # Height, width and channel on the image
                centerX, centerY = int(landmark.x * w), int(
                    landmark.y * h)  # Converts the decimal coordinates relative to the image for each index
                landmarkList.append([index, centerX, centerY])  # Adding index and its coordinates to a list
    return landmarkList

# Variables initialization
t_FPS_prev = 0  # For counting FPS: Frames per Second


def calculate_FPS(t_FPS_prev):
    t_FPS = time.time()
    FPS = 1 / (t_FPS - t_FPS_prev)  # Calculate FPS
    t_FPS_prev = t_FPS
    return FPS, t_FPS_prev


def caluculateSpeedRatio():
    # CHANGE THE DISTANCE BETWEEN YOUR THUMB AND INDEX TO CHANGE THE SPEED RATIO
    thumbTip = numpy.array(lmList[thumbTipId])
    indexTip = numpy.array(lmList[indexTipId])
    distance = numpy.linalg.norm(thumbTip-indexTip)
    ratio = min(max(distance - 20, 0), 100)/100
    return ratio


def calculateTurningRatio():
    # MOVE YOUR THUMB RIGHT AND LEFT HORIZONTALLY TO CHANGE LEFT AND RIGHT SPEED RATIOS
    thumbTip = lmList[4]
    rightRatio = ((640/2)-thumbTip[1])/100+0.5
    if(rightRatio > 1):
        rightRatio = 1
    if(rightRatio < 0):
        rightRatio = 0
    leftRatio = 1-rightRatio
    return leftRatio, rightRatio

while True:
    # Calculate FPS
    FPS, t_FPS_prev = calculate_FPS(t_FPS_prev)
    # Reads frames from the camera
    check, img = cap.read()
    # check2, img2 = cap2.read()
    # Changes the format of the frames from BGR to RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Print a pink rectangle that limits the uable mouse region
    cv2.rectangle(img, (75, 0), (640 - 75, 480 - 150), (255, 0, 0),2)
    # Stores the Hand Landmark result
    lmList = handLandmarks(imgRGB)

    # Extracting Information from hand landmarks
    if len(lmList) != 0:  # Check to see if any fingers are detected

        speedRatio = caluculateSpeedRatio()
        leftSpeedRatio, rightSpeedRatio = calculateTurningRatio()
        rightSpeed = speedRatio * rightSpeedRatio * motorSpeed
        leftSpeed = speedRatio * leftSpeedRatio * motorSpeed

        message = '<'+ str(leftSpeed) + ',' + str(rightSpeed) + '>'
    else:
        message = "<0,0>"
    ArduinoSerial.write(message.encode())
    # print((leftSpeed, rightSpeed))

    # Video Display
    img = cv2.flip(img, 1)
    cv2.putText(img, str(round(FPS)), (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, [0, 150, 0], 3)  # Prints FPS
    img = cv2.resize(img, (1280, 720))
    # img2 = cv2.resize(img2, (360, 240))
    cv2.imshow("Webcam", img)
    # cv2.imshow("camera", img2)
    if cv2.waitKey(10) & 0xFF == ord('q'):  # Closes the window if Q is pressed
        break

cap.release()  # Releasing the video recording device
cv2.destroyAllWindows()  # Destroying all the opened windows
