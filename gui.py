from moviepy.editor import *
import pygame
from random import *
from tkinter import *
from tkinter.messagebox import _show

import json
import pyrebase
from datetime import date

from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import playsound
import imutils
import time
import dlib
import cv2
import time


firebaseConfig = {'apiKey': "AIzaSyDdqZKZMQhSWO8KFiO-8azjyH42N91UuLg",
                  'authDomain': "focus-bda7e.firebaseapp.com",
                  'projectId': "focus-bda7e",
                  'databaseURL': "https://focus-bda7e-default-rtdb.firebaseio.com/",
                  'storageBucket': "focus-bda7e.appspot.com",
                  'messagingSenderId': "999898533530",
                  'appId': "1:999898533530:web:c60c6c9e5f3db3ef5f9923",
                  'measurementId': "G-95VXE5XTS9"}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()

global emailThing

global BLINK_NUMBER
BLINK_NUMBER = 0
global NAPPING_NUMBER
NAPPING_NUMBER = 0

def login():
    global emailThing
    loginEmail = email.get()
    loginPassword = password.get()
    try:
        user = auth.sign_in_with_email_and_password(loginEmail, loginPassword)
        notif.config(fg="green", text="Successful Sign-in")
        emailThing = loginEmail
        open()
        #root.destroy()
    except Exception as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']
        notif.config(fg="red", text=error['message'])


def signup():
    signupEmail = email.get()
    signupPassword = password.get()
    confirmPass = password.get()
    if signupPassword == confirmPass:
        try:
            auth.create_user_with_email_and_password(signupEmail, signupPassword)
            notif.config(fg="green", text="Successful Sign-up")
            login()
        except Exception as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']
            notif.config(fg="red", text=error['message'])
    else:
       notif.config(fg="red", text="Passwords do not match")

def updateDatebase():
    global emailThing
    global NAPPING_NUMBER
    global BLINK_NUMBER

    userID = emailThing.replace(".", ",")
    today = date.today()
    db.child("users").child(userID).child("Data").child(today).update({"Blink Count": BLINK_NUMBER, "Nap Count": NAPPING_NUMBER})

def getDatabaseNumbers():
    global emailThing
    global BLINK_NUMBER
    global NAPPING_NUMBER
    userID = emailThing.replace(".", ",")
    today = date.today()
    tempDict = db.child("users").child(userID).child("Data").child(today).get()

    if tempDict.each() is not None:
        tempList = []
        for i in tempDict.each():
            tempList.append(i.val())
    
        BLINK_NUMBER = tempList[0]
        NAPPING_NUMBER = tempList[1]

    
global napTime
napTime = 0
global defaultNapTime
defaultNapTime = True

def open_settings():
    top = Toplevel()
    top.title('Settings')
    top.geometry('400x100')
    naptime = StringVar()
    Label(top, text="Nap Time:", font=("Helvetica", 20)).grid(sticky=N,padx=60)
    Entry(top, width=50,textvariable=naptime).grid(sticky=N,pady=10,padx=60, row=1) 
    defaultNapTime = False

root = Tk()
root.title('EyeSpy')
root.geometry('800x400')
email = StringVar()
password = StringVar()

Label(root, text="User ID:", font=("Helvetica", 20)).grid(sticky=N,padx=250)
Entry(root, width=50,textvariable=email).grid(sticky=N,pady=10,padx=250, row=1)
Label(root, text="Password:", font=("Helvetica", 20)).grid(sticky=N,padx=250, row=2)
Entry(root, width=50,textvariable=password, show="*").grid(sticky=N,pady=10, row=3)
Button(root, text="Sign up", command=signup).grid(sticky=N,pady=10, row=4)
Button(root, text="Log in", command=login).grid(sticky=N,pady=10, row=5)
notif = Label(root, font=("Helvetica", 20))
notif.grid(sticky=N,pady=1,row=6)
Button(root, text="Settings", command=open_settings).grid(sticky=N,pady=10, row=7)


def play_vid():
    pygame.display.set_caption('Eye Exercises')

    value = randint(0, 12)
    value = str(value)

    clip = VideoFileClip('Exercises/' + value + '.mp4')
    clip.preview()



def open():
    getDatabaseNumbers()

    global minutes 
    minutes = 0

    global eyeRunning
    eyeRunning = False

    top = Toplevel()
    top.title('Break Time')
    top.geometry('1000x600')
    
    def eyeDetectionRun(runTime):
        #Running Eye Detection
        threadEye = Thread(target=runEyeDetection, args=(time.perf_counter(), runTime))
        threadEye.deamon = True
        threadEye.start()

    def changeTime(inputTime):
        global minutes
        global eyeRunning
        if minutes > 0:
            top.after(60000, lambda: changeTime(inputTime))
            minutes -= 1 * 60000
            timer.config(text="Your timer is set for {} minutes".format(minutes / 60000))
        else:
            eyeRunning = False

    def defaultTimeInputs(inputTime):
        global minutes
        global eyeRunning
        minutes = inputTime * 60000
        timer.config(text="Your timer is set for {} minutes".format(minutes / 60000))
        top.after(minutes - (60000), lambda: _show('Break Time', 'You have been working for {} minutes. Take a break!'.format(inputTime - 1)))
        # top.after(minutes, lambda: play_vid())
        changeTime(inputTime)

        if not eyeRunning:
            eyeDetectionRun((inputTime-1) * 60)
            eyeRunning = True

        
    #creating label widgets
    Label(top, text="When would you like to take your next break?", font=("Helvetica", 20)).grid(sticky=N,padx=250)

    #creating button widgets
    Button(top, text="30 mins", command=(lambda: defaultTimeInputs(31)), width=10, height = 3, font=("Helvetica", 15)).grid(sticky=N,padx=250)
    Button(top, text="1 hour", command=(lambda: defaultTimeInputs(61)), width=10, height = 3, font=("Helvetica", 15)).grid(sticky=N,padx=250)
    Button(top, text="1.5 hour", command=(lambda: defaultTimeInputs(91)), width=10, height = 3, font=("Helvetica", 15)).grid(sticky=N,padx=250)
    Button(top, text="2 hours", command=(lambda: defaultTimeInputs(121)), width=10, height = 3, font=("Helvetica", 15)).grid(sticky=N,padx=250)
    Label(top, text="Enter Custom Break Time:", font=("Helvetica", 15)).grid(sticky=N,padx=250)
    e = Entry(top, width=50)
    e.grid(sticky=N,padx=250)
    Button(top, text="Submit", command=(lambda: defaultTimeInputs(int(e.get())+ 1)), width=10, height = 3, font=("Helvetica", 15)).grid(sticky=N,padx=250)
    timer = Label(top,  font=("Helvetica", 20))
    timer.grid(sticky=N,pady=1)


#Eye
def eyesAreClosed(breakTime):
    if breakTime == True:
        print("Your Eyes Are Closed")

def wakeUpAlarm(path):
    playsound.playsound(path)

def eyeAspectRatio(eye):
    vertOne = dist.euclidean(eye[1], eye[5])
    vertTwo = dist.euclidean(eye[2], eye[4])
    horzDistance = dist.euclidean(eye[0], eye[3])
    
    eyeAspectRatio = (vertOne + vertTwo) / (2.0 * horzDistance)
    
    return eyeAspectRatio

def loadFaceParameters(args):
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])
    
    return detector, predictor

def runEyeDetection(startTime, totalTime):    
    #-----------------------Variable Decleration-----------------------#
    EYE_AR_THRESHOLD = 0.3
    EYE_AR_CONSEC_FRAMES = 48
    COUNTER = 0
    BREAK_ON = False
    global BLINK_NUMBER
    BLINK_CONSEC_FRAMES = 5
    if defaultNapTime == False:
        NAPPING_FRAMES = napTime * 60
    else:
        NAPPING_FRAMES = 5 * 60
    global NAPPING_NUMBER

    #-----------------------Parsing Arguments-----------------------#
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", default="D:\shape_predictor.dat" , help="path to facial landmark predictor")
    
    ap.add_argument("-w", "--webcam", type=int, default=0, help="index of webcam on system")

    ap.add_argument("-b", "--break", type=bool, default=True, help="Do You want a Break Message?")

    ap.add_argument("-a", "--alarm", type=str, default="D:\sound.wav" , help="index of Alarm.Wave")

    args = vars(ap.parse_args())

    #-----------------------Initializing Face Detetor and Landmark Predictor-----------------------#
    detector, predictor = loadFaceParameters(args)

    #-----------------------DLib eye Indicies-----------------------#
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


    #-----------------------Loading the Rectangels-----------------------#
    print("[INFO] starting video stream thread...")
    vs = VideoStream(src=args["webcam"]).start()
    time.sleep(1.0)

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width = 450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:

            #-----------------------Eye Outlining-----------------------#
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftAspectRatio = eyeAspectRatio(leftEye)
            rightAspectRatio = eyeAspectRatio(rightEye)

            bothAspectRatio = (leftAspectRatio + rightAspectRatio) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            outlineColor = (0, 255, 0)
            cv2.drawContours(frame, [leftEyeHull], -1, outlineColor, 1)
            cv2.drawContours(frame, [rightEyeHull], -1, outlineColor, 1)

            #-----------------------Checking if Eyes are Closed-----------------------#    
            if bothAspectRatio < EYE_AR_THRESHOLD:
                COUNTER += 1

                if COUNTER >= EYE_AR_CONSEC_FRAMES:

                    if not BREAK_ON:
                        BREAK_ON = True

                        if args["break"] != "":
                            t = Thread(target=eyesAreClosed, args=(args["break"],))
                            t.deamon = True
                            t.start()

                    textColor = (0, 0, 255)

                    if COUNTER >= NAPPING_FRAMES:
                        cv2.putText(frame, "NAPPING!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2)
                        if args["alarm"] != "":
                            t = Thread(target=wakeUpAlarm, args=(args["alarm"],))
                            t.daemon = True
                            t.start()
            else:
                if COUNTER >= BLINK_CONSEC_FRAMES:
                    BLINK_NUMBER += 1
                if COUNTER >= NAPPING_FRAMES:
                    NAPPING_NUMBER += 1

                COUNTER = 0
                BREAK_ON = False

            textColor = (0, 0, 255)
            cv2.putText(frame, "EyeAR: {:.2f}".format(bothAspectRatio), (300,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2)
            cv2.putText(frame, "Blink: {}".format(BLINK_NUMBER), (300, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2)

        #Show Frame
        cv2.imshow("Frame", frame)

        #-----------------------Exiting Program-----------------------#
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if time.perf_counter() - startTime >= totalTime:
            break

    #-----------------------Closing Everthing Once Stopped-----------------------#
    cv2.destroyAllWindows()
    vs.stop()
    updateDatebase()
    return -1


root.mainloop()
