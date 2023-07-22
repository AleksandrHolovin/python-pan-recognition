import cv2
import time
import numpy as np
import HandTrakingModule as htm
import math

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# constants
cameraWidth = 1280
cameraHeight = 720

# volume controller init
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# volume constants
volumeRange = volume.GetVolumeRange()
minVolume = volumeRange[0]
maxVolume = volumeRange[1]

# video capturing setup
cap = cv2.VideoCapture(0)
cap.set(3, cameraWidth)
cap.set(4, cameraHeight)
previousTime = 0

detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = detector.findHads(img)
    landmarkList = detector.findPosition(img, draw=False)
    if len(landmarkList) !=0:

        x1, y1 = landmarkList[4][1], landmarkList[4][2]
        x2, y2 = landmarkList[8][1], landmarkList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0,255), cv2.FILLED)
        cv2.line(img,(x1,y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15,(255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        vol = np.interp(length, [50, 300], [minVolume, maxVolume])
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    currentTime = time.time()
    fps = 1 / (currentTime - previousTime)
    previousTime = currentTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 2)

    cv2.imshow('Img', img)
    cv2.waitKey(1)
