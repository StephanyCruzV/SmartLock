import cv2
from time import sleep
from PIL import Image 
from picamera.array import PiRGBArray
from picamera import PiCamera

def main_app(name):

    face_cascade = cv2.CascadeClassifier('./data/haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(f"./data/classifiers/{name}_classifier.xml")

    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    pred = 0

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]

            id, confidence = recognizer.predict(roi_gray)
            confidence = 100 - int(confidence)
            pred = 0

            if confidence > 50:
                pred += 1
                text = name.upper()
                font = cv2.FONT_HERSHEY_PLAIN
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                image = cv2.putText(image, text, (x, y-4), font, 1, (0, 255, 0), 1, cv2.LINE_AA)
            else:   
                pred -= 1
                text = "UnknownFace"
                font = cv2.FONT_HERSHEY_PLAIN
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                image = cv2.putText(image, text, (x, y-4), font, 1, (0, 0,255), 1, cv2.LINE_AA)

        cv2.imshow("image", image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(pred)
            if pred > 0 : 
                dim =(124,124)
                img = cv2.imread(f".\\data\\{name}\\{pred}{name}.jpg", cv2.IMREAD_UNCHANGED)
                resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
                cv2.imwrite(f".\\data\\{name}\\50{name}.jpg", resized)
                Image1 = Image.open(f".\\2.png") 

                # make a copy the image so that the  
                # original image does not get affected 
                Image1copy = Image1.copy() 
                Image2 = Image.open(f".\\data\\{name}\\50{name}.jpg") 
                Image2copy = Image2.copy() 

                # paste image giving dimensions 
                Image1copy.paste(Image2copy, (195, 114)) 

                # save the image  
                Image1copy.save("end.png") 
                frame = cv2.imread("end.png", 1)

                cv2.imshow("Result",frame)
                cv2.waitKey(5000)
            break

        rawCapture.truncate(0)

    cv2.destroyAllWindows()
