from GUI import *
from threading import Thread

def main():
    guiRun()

def guiRun():
    #Running the GUI
    threadMain = Thread(target=mainloop)
    threadMain.deamon = True
    threadMain.start()

