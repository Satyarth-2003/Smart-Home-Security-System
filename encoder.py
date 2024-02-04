import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate("smarthomesecuritysystem.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smarthomesecuritysystem-7e9a0-default-rtdb.firebaseio.com/',
    'storageBucket': 'smarthomesecuritysystem-7e9a0.appspot.com'
})

imagePath = os.listdir('Images')
imageList = []
ids = []
folderPath = 'Images'
for path in imagePath:
    imageList.append(cv2.imread(os.path.join('Images', path)))
    ids.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    send = bucket.blob(fileName)
    send.upload_from_filename(fileName)
print(ids)


def encoding(imageList):
    encodeList = []
    for img in imageList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


encodings = encoding(imageList)
print(encodings)
mapping = [encodings, ids]
print("Encoding Complete")

file = open('Encode.p', 'wb')
pickle.dump(mapping, file)
file.close()
print("Mapping Saved")
