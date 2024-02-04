import cv2
import os
import numpy as np
import pickle
import cvzone
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("smarthomesecuritysystem.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smarthomesecuritysystem-7e9a0-default-rtdb.firebaseio.com/',
    'storageBucket': 'smarthomesecuritysystem-7e9a0.appspot.com'
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

modePath = os.listdir('Resources/Modes')
modeList = []
for path in modePath:
    modeList.append(cv2.imread(os.path.join('Resources/Modes', path)))

# print(len(modeList))

file = open('Encode.p', 'rb')
mappingFaceID = pickle.load(file)
file.close()
encodings, ids = mappingFaceID
# print(ids)

modeType = 0
counter = 0
id = -1

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCF = face_recognition.face_locations(imgS)
    encodeCF = face_recognition.face_encodings(imgS, faceCF)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = modeList[modeType]

    for encodeFace, faceLocation in zip(encodeCF, faceCF):
        match = face_recognition.compare_faces(encodings, encodeFace)
        faceDistance = face_recognition.face_distance(encodings, encodeFace)
        # print("Match", match)
        # print("faceDistance", faceDistance)

        matchIndex = np.argmin(faceDistance)
        # print('Match Index', matchIndex)

        if match[matchIndex]:
            # print('Known Face Detected')
            # print(ids[matchIndex])
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            box = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, box, rt=0)
            id = ids[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1

        if counter != 0:
            if counter == 1:
                # Getting Data
                info = db.reference(f'Authorized/{id}').get()
                print(info)

                # Update data
                ref = db.reference(f'Authorized/{id}')

            if counter <= 20:
                # change the color, position and name format
                (width, height), x = cv2.getTextSize(info['name'], cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
                adjust = (414 - width) // 2
                cv2.putText(imgBackground, str(info['name']), (808 + adjust, 125), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 0), 1)

            counter += 1

            if counter > 20:
                counter = 0
                modeType = 0
                info = []
                imgBackground[44:44 + 633, 808:808 + 414] = modeList[modeType]


    cv2.imshow("Main-Interface", imgBackground)
    cv2.waitKey(1)
