# importing everything from tkinter
from tkinter import *
# importing the styling module ttk from tkinter
from tkinter import ttk
from tkinter import filedialog ,messagebox
from tkinter.filedialog import askopenfile
import importlib
import librosa
import numpy as np
import joblib
import os
import time
import wave
import threading
import tkinter as tk
import pyaudio


clf=joblib.load('clf.joblib')
svm=joblib.load('svm.joblib')

def run_main(wavname=None):
    
    

    def upload_file(wavname):
        if wavname is None:

            f_types = [('wav Files', '*.wav')]
            filename = filedialog.askopenfilename(filetypes=f_types)
        else:
            filename = wavname
        l1["text"] = filename
        audio,freq= librosa.load(filename)
        S = librosa.feature.mfcc(y=audio , sr=freq, n_mfcc=40)
        inp_data = np.expand_dims(S.mean(axis=1),axis=0)
        p1 = clf.predict(inp_data)[0]
        p2 = svm.predict(inp_data)[0]

        if p1==0 and p2 ==0:
            print('Postive')
            res = 'Scream detected'
        else:
            print('Negative')
            res = 'Negative'
        l1["text"] = res

    

    def record_file():
        window.destroy()
        print("loading main")
        recorder()
        # import main
        # importlib.reload(main)



    # creates the window using Tk() fucntion
    window = Tk()
    # creates title for the window
    window.title('scream detection')
    # the icon for the application, this replaces the default icon
    window.iconbitmap(window, 'voice_recorder_icon.ico')
    # dimensions and position of the window
    window.geometry('700x350+440+180')
    # makes the window non-resizable
    window.resizable(height=FALSE, width=FALSE)
    # this will run the main window infinitely


    title_font=('times', 26, 'bold')
    l1 = Label(window,text='scream detection',width=30,font=title_font)  
    l1.grid(row=1,column=1)


    b1 = Button(window, text='Upload File', 
    width=20,command = lambda:upload_file(wavname=None))
    b1.grid(row=2,column=1,pady=30) 

    l1 = Label(window,text='result will be displayed here',width=30,font=["sans-serif",10,"bold"])  
    l1.grid(row=3,column=1,pady=20)

    b2 = Button(window, text='record', 
    width=20,command = lambda:record_file())
    b2.grid(row=4,column=1,pady=10) 

    def wait(message):
        win = Toplevel(window)
        win.transient()
        win.title('Wait')
        Label(win, text=message).pack()
        return win
    
    if wavname is not None:
        print("wait ..............")
        # win = wait('Just one second...')
        upload_file(wavname)
        # window.after(upload_file(wavname), win.destroy)
        print("finished")
    window.mainloop()
    
    

class VoiceRecorder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False,False)
        self.root.geometry("200x100")
        self.button = tk.Button(text="Mic Off!",font=["sans-serif",20,"bold"],command=self.runMic)
        self.button.pack()
        self.label = tk.Label(text="00:00:00",font=["sans-serif",20,"bold"])
        self.label.pack()
        self.recording = False 
        self.wavname = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    def on_closing(self):
        print("closing")
        self.root.destroy()
        run_main(self.wavname)


    def runMic(self):
        self.btnText = self.button.cget("text")
        if(self.btnText == "Mic Off!"):
            self.button["text"] = "Mic On!"
            self.recording = True
            threading.Thread(target=self.record).start()

        else:
            self.button["text"] = "Mic Off!"
            self.recording = False


    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=1024)
        frames = []
        start = time.time()
        while self.recording:
            data = stream.read(1024)
            frames.append(data)
            passed = time.time() - start
            secs,minutes = passed % 60,passed // 60
            hours = minutes // 60
            self.label.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d}")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        exists = True
        i =1 
        dirpath ="recorder_files"
        while exists:
            if(os.path.exists(os.path.join(dirpath,f"recording{i}.wav"))):
                i +=1
            else:
                exists = False

        self.wavname = os.path.join(dirpath,f"recording{i}.wav")
        sound_file = wave.open(self.wavname,"wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b"".join(frames))
        sound_file.close()


def recorder():
    VoiceRecorder()

if __name__ =="__main__":
    run_main()