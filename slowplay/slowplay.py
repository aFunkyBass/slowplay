#!/usr/bin/python3
#
# https://lazka.github.io/pgi-docs/#Gst-1.0/classes/Element.html
# https://tkinterexamples.com/
#
#import tkinter as tk
import player as pl
from tkinter import ttk
from tkinter import messagebox
from tkinter import PhotoImage
import customtkinter as ctk
import datetime as dt
from ttkthemes import ThemedTk
import os
import argparse
from PIL import Image
import re
import filedialpy

INITIAL_GEOMETRY = "800x350"
APP_TITLE = "SlowPlay"

THEME_NAME = "clam"
LBL_FONT_SIZE = 14

DEFAULT_SPEED = 100
MIN_SPEED_PERCENT = 50
MAX_SPEED_PERCENT = 150
STEPS_SPEED = 5

DEFAULT_SEMITONES = 0
MIN_PITCH_SEMITONES = -12
MAX_PITCH_SEMITONES = 12
STEPS_SEMITONES = 1

DEFAULT_CENTS = 0
MIN_PITCH_CENTS = -50
MAX_PITCH_CENTS = 50

DEFAULT_VOLUME = 100
MIN_VOLUME = 0
MAX_VOLUME = 100

STEPS_SEC_MOVE_1 = 5
STEPS_SEC_MOVE_2 = 10
STEPS_SEC_MOVE_3 = 15

UPDATE_INTERVAL = 50

OPEN_EXTENSIONS_FILTER = (
    'mp3',
    'wav',
    'flac',
    'aif',
    'ogg',
    'aac',
    'alac',
    'wma',
    'm4a'
)

SAVE_EXTENSIONS_FILTER = (
    'mp3',
    'wav',
)

SAVE_DEFAULT_EXTENSION = "mp3"

class App(ctk.CTk):
#class App(ThemedTk):
    def __init__(self, *orig_args, **orig_kwargs):
        super().__init__(className=APP_TITLE, *orig_args, **orig_kwargs)

        working_dir = os.path.dirname(__file__)
        resources_dir = "".join([working_dir, "/resources"])

        self.geometry(INITIAL_GEOMETRY)
        self.title(APP_TITLE)

        self.wm_iconphoto(False, PhotoImage(file=f"{resources_dir}/Icona-32.png"))
                                    
        self.player = pl.Replayer()
        self.player.updateInterval = UPDATE_INTERVAL

        # Imposta lo stile e il tema
        self.style = ttk.Style(self)
        #print(self.style.theme_names())
        if THEME_NAME in self.style.theme_names():
            self.style.theme_use(THEME_NAME)

        ctk.set_appearance_mode("dark")

        resetIcon = ctk.CTkImage(light_image=Image.open(f"{resources_dir}/Reset Icon.png"),
                                 dark_image=Image.open(f"{resources_dir}/Reset Icon.png"), size=(16, 16))

        # variabili automatiche
        self.songTime = ctk.StringVar(self)
        self.songTime.set(dt.timedelta(seconds = 0))
        self.songProgress = ctk.DoubleVar(self, value=0)
        self.songProgress.set(0)

        # Variabili globali
        self.media = ""
        self.mediaUri = ""
        self.mediaFileName = ""
        self.mediaPath = ""
        self.bValuesChanging = False
        self.lastOpenDir = ""
        self.lastSaveDir = ""

        # crea i tre fames principali Sinistro (espandibile), destro(pulsanti)
        # e basso (status)
        self.LFrame = ctk.CTkFrame(self, width=400, height=200)
        self.RFrame = ctk.CTkFrame(self)
        self.BFrame = ctk.CTkFrame(self, height=24)

        self.LFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.RFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.BFrame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Crea i widget del pannello di sinistra
        self.dispPosition = ctk.CTkLabel(self.LFrame, textvariable=self.songTime, font=("", 28))
        self.dispPosition.grid(row=0, column=0, pady=[10, 0], sticky="n")

        self.progress = ctk.CTkProgressBar(self.LFrame, variable=self.songProgress, height=24)
        self.progress.grid(row=1, column=0, padx=8, pady=10, sticky="ew")

        self.scale = ctk.CTkSlider(self.LFrame, command=self.songSeek)
        self.scale.grid(row=2, column=0, padx=8, sticky="ew")

        self.LFrame.grid_columnconfigure(0, weight=1)

        self.CTLFrame = ctk.CTkFrame(self.LFrame)
        self.CTLFrame.grid(row=3, column=0, padx=8, pady=8, sticky="ew")

        #vint = (self.register(self.validate_int),'%d','%i','%P','%s','%S','%v','%V','%W')
        vint = (self.register(self.validate_int),'%S')
        self.varSpeed = ctk.IntVar(self, value=DEFAULT_SPEED)
        self.varSpeed.trace_add("write", self.speedChanged)
        self.lblSpeed = ctk.CTkLabel(self.CTLFrame, text="Speed:", font=("", LBL_FONT_SIZE))
        self.lblSpeed.grid(row=0, column=0, pady=(4, 0), sticky="w")
        self.sldSpeed = ctk.CTkSlider(self.CTLFrame, from_=MIN_SPEED_PERCENT,
                                      to=MAX_SPEED_PERCENT, number_of_steps=20, variable=self.varSpeed)
        self.sldSpeed.grid(row=0, column=1, padx=8, sticky="ew")
        self.entSpeed = ctk.CTkEntry(self.CTLFrame, width=50, justify="center",
                                     validate='key', validatecommand=vint)
        self.entSpeed.grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.lblSpeedEntry = ctk.CTkLabel(self.CTLFrame, text="%", font=("", LBL_FONT_SIZE))
        self.lblSpeedEntry.grid(row=0, column=3, padx=(0, 8), pady=8, sticky="w")
        self.btnResetSpeed = ctk.CTkButton(self.CTLFrame, width=40, image=resetIcon,
                                           text=None, command= lambda: self.resetDefaultVar(self.varSpeed))
        self.btnResetSpeed.grid(row=0, column=4, padx=(0, 8), pady=8, sticky="w")
        self.entSpeed.bind('<Return>', self.checkSpeed)
        self.entSpeed.bind('<KP_Enter>', self.checkSpeed)
        self.entSpeed.bind('<FocusOut>', self.checkSpeed)
        self.speedChanged(None, None, None)

        #vnegint = (self.register(self.validate_neg_int),'%d','%i','%P','%s','%S','%v','%V','%W')
        vnegint = (self.register(self.validate_neg_int),'%S', '%P')
        self.varPitchST = ctk.IntVar(self, value=DEFAULT_SEMITONES)
        self.varPitchST.trace_add("write", self.semitonesChanged)
        self.lblPitchST = ctk.CTkLabel(self.CTLFrame, text="Pitch (semitones):", font=("", LBL_FONT_SIZE))
        self.lblPitchST.grid(row=1, column=0, pady=(4, 0), sticky="w")
        self.sldPitchST = ctk.CTkSlider(self.CTLFrame,from_= MIN_PITCH_SEMITONES,
                                        to = MAX_PITCH_SEMITONES, variable=self.varPitchST)
        self.sldPitchST.grid(row=1, column=1, padx=8, sticky="ew")
        self.entPitchST = ctk.CTkEntry(self.CTLFrame, width=50, justify="center",
                                       validate='all', validatecommand=vnegint)
        self.entPitchST.grid(row=1, column=2, padx=8, pady=8, sticky="w")
        self.lblPitchSTEntry = ctk.CTkLabel(self.CTLFrame, text="s/t", font=("", LBL_FONT_SIZE))
        self.lblPitchSTEntry.grid(row=1, column=3, padx=(0, 8), pady=8, sticky="w")
        self.btnResetPitchST = ctk.CTkButton(self.CTLFrame, width=40, image=resetIcon,
                                             text=None, command= lambda: self.resetDefaultVar(self.varPitchST))
        self.btnResetPitchST.grid(row=1, column=4, padx=(0, 8), pady=8, sticky="w")
        self.entPitchST.bind('<Return>', self.checkSemitones)
        self.entPitchST.bind('<KP_Enter>', self.checkSemitones)
        self.entPitchST.bind('<FocusOut>', self.checkSemitones)
        self.semitonesChanged(None, None, None)

        self.varPitchCents = ctk.IntVar(self, value=DEFAULT_CENTS)
        self.varPitchCents.trace_add("write", self.centsChanged)
        self.lblPitchCents = ctk.CTkLabel(self.CTLFrame, text="Pitch (cents):", font=("", LBL_FONT_SIZE))
        self.lblPitchCents.grid(row=2, column=0, pady=(4, 0), sticky="w")
        self.sldPitchCents = ctk.CTkSlider(self.CTLFrame,from_= MIN_PITCH_CENTS,
                                           to = MAX_PITCH_CENTS, variable=self.varPitchCents)
        self.sldPitchCents.grid(row=2, column=1, padx=8, sticky="ew")
        self.entPitchCents = ctk.CTkEntry(self.CTLFrame, width=50, justify="center",
                                          validate='all', validatecommand=vnegint)
        self.entPitchCents.grid(row=2, column=2, padx=8, pady=8, sticky="w")
        self.lblPitchCentsEntry = ctk.CTkLabel(self.CTLFrame, text="c.", font=("", LBL_FONT_SIZE))
        self.lblPitchCentsEntry.grid(row=2, column=3, padx=(0, 8), pady=8, sticky="w")
        self.btnResetPitchCents = ctk.CTkButton(self.CTLFrame, width=40, image=resetIcon, text=None,
                                                command= lambda: self.resetDefaultVar(self.varPitchCents))
        self.btnResetPitchCents.grid(row=2, column=4, padx=(0, 8), pady=8, sticky="w")
        self.entPitchCents.bind('<Return>', self.checkCents)
        self.entPitchCents.bind('<KP_Enter>', self.checkCents)
        self.entPitchCents.bind('<FocusOut>', self.checkCents)
        self.centsChanged(None, None, None)

        self.varVolume = ctk.IntVar(self, value=DEFAULT_VOLUME)
        self.varVolume.trace_add("write", self.volumeChanged)
        self.lblVolume = ctk.CTkLabel(self.CTLFrame, text="Volume:", font=("", LBL_FONT_SIZE))
        self.lblVolume.grid(row=3, column=0, pady=(4, 0), sticky="w")
        self.sldVolume = ctk.CTkSlider(self.CTLFrame,from_= MIN_VOLUME,
                                           to = MAX_VOLUME, variable=self.varVolume)
        self.sldVolume.grid(row=3, column=1, padx=8, sticky="ew")
        self.entVolume = ctk.CTkEntry(self.CTLFrame, width=50, justify="center",
                                          validate='all', validatecommand=vint)
        self.entVolume.grid(row=3, column=2, padx=8, pady=8, sticky="w")
        self.entVolume.bind('<Return>', self.checkVolume)
        self.entVolume.bind('<KP_Enter>', self.checkVolume)
        self.entVolume.bind('<FocusOut>', self.checkVolume)
        self.volumeChanged(None, None, None)

        self.CTLFrame.columnconfigure(1, weight=1)

        # Crea i pulsanti del pannello di destra
        self.playButton = ctk.CTkButton(self.RFrame, text="Play", font=("", 18), command=self.togglePlay)
        self.playButton.grid(row=0, column=0, pady=(8, 0), sticky="w")

        self.openButton = ctk.CTkButton(self.RFrame, text="Open", font=("", 18), command=self.openFile)
        self.openButton.grid(row=1, column=0, pady=(8, 0), sticky="w")

        self.saveasButton = ctk.CTkButton(self.RFrame, text="Save as...", font=("", 18), command=self.saveAs)
        self.saveasButton.grid(row=2, column=0, pady=(8, 0), sticky="w")

        self.fileLabel = ctk.CTkLabel(self.BFrame, text="", font=("", LBL_FONT_SIZE))
        self.fileLabel.grid(row=0, column=0, padx=(8), sticky="w")

        self.dispSongTime(Force=True)

        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        # print args
        if(args.media != None):
            self.setFile(args.media)

    def openFile(self):
        self.setFile(self.selectFileToOpen())

    def makeFileTypes(self, filter):
        filetypes = [f"{str(x).upper()} files: *.{x}" for x in filter]
        filetypes.insert(0, "Supported files: " + ' '.join(["*." + x for x in filter]))
        filetypes.append("All files: *")
        return(filetypes)

    def selectFileToOpen(self) -> str:
        filetypes = self.makeFileTypes(OPEN_EXTENSIONS_FILTER)

        if(self.lastOpenDir == ""):
            self.lastOpenDir = os.path.expanduser("~")

        self.unbind_all('<KeyPress>')
        self.unbind_all('<1>')
        try:
            filename = filedialpy.openFile(
                title='Open a file',
                initial_dir=self.lastOpenDir,
                filter=filetypes)
        finally:
            self.bind_all('<1>', self._click_manager_)
            self.bind_all('<KeyPress>', self._hotkey_manager_)
        
        return(filename)

    # Reimposta tutti i valori
    def resetValues(self):
        self.player.Pause()
        self.player.Rewind()
        self.varSpeed.set(DEFAULT_SPEED)
        self.varPitchST.set(DEFAULT_SEMITONES)
        self.varPitchCents.set(DEFAULT_CENTS)
        self.songProgress.set(0)
        self.songTime.set(dt.timedelta(seconds = 0))
        self.scale.set(0)

    def setFile(self, filename):
        #print(filename)
        if(not filename or filename == ''):
            return
        elif not os.path.isfile(filename):
            messagebox.showerror("File not found...", f"Unable to open file: {filename}")
            return

        #self.player.audiosrc.set_property("uri", "file://" + filename)

        self.media = os.path.realpath(filename)
        self.mediaFileName = os.path.basename(self.media)
        self.mediaPath = os.path.dirname(self.media)
        self.lastOpenDir = self.mediaPath
        if(str(self.media).startswith('/')):
            self.mediaUri = "file://" + self.media
        else:
            self.mediaUri = self.media

        self.player.MediaLoad(self.mediaUri)
        self.player.update_position()
        self.resetValues()

        self.fileLabel.configure(text=self.mediaFileName)
        self.title(f"{APP_TITLE} - {self.mediaFileName}")

    def saveAs(self):
        filename = self.selectFileToSave()

        if(str(filename) == '()' or str(filename) == ""):
            return

        self.player.Pause()

        if(os.path.exists(os.path.dirname(filename)) == False):
            messagebox.showerror("Filename error...", f"Unable to save file: {filename}")
            return

        if(filename.endswith(SAVE_EXTENSIONS_FILTER) == False):
            filename += "." + SAVE_DEFAULT_EXTENSION

        self.save_prg_var = ctk.DoubleVar(self, value=0)
        self.save_prg = ctk.CTkProgressBar(self.RFrame, variable=self.save_prg_var, height=10, width=10)
        self.save_prg.grid(row=4, column=0, padx=8, pady=10, sticky="ew")
        self.update_idletasks()

        self.lastSaveDir = os.path.dirname(filename)

        try:
            self.player.fileSave(self.media, filename, self.saveProgress)
        finally:
            self.save_prg.destroy()
            self.save_prg_var.__del__()

    def selectFileToSave(self) -> str:
        filetypes = self.makeFileTypes(SAVE_EXTENSIONS_FILTER)
        
        if(self.lastSaveDir == ""):
            self.lastSaveDir = os.path.expanduser("~")

        self.unbind_all('<KeyPress>')
        self.unbind_all('<1>')
        try:
            filename = filedialpy.saveFile(
                title='Save as..',
                initial_file=self.mediaFileName,
                initial_dir=self.lastSaveDir,
                filter=filetypes)
        finally:
            self.bind_all('<1>', self._click_manager_)
            self.bind_all('<KeyPress>', self._hotkey_manager_)

        return(filename)

    def saveProgress(self, value):
        self.save_prg_var.set(value)
        self.update_idletasks()

    def togglePlay(self):
        if self.player.isPlaying == False:
            self.player.Play()
        else:
            self.player.Pause()

    def songControl(self):
        dd, pp = self.player.update_position()
        if(dd and pp and dd > 0 and pp >= dd):
            self.player.Pause()
            self.player.Rewind()
            self.dispSongTime(Force=True)

    def dispSongTime(self, Force = False):
        if(self.bValuesChanging):
            return

        curpos = self.player.song_time(self.player.query_position())
        if((curpos and curpos >= 0) or Force):
            # Salva la posizione corrente in secondi
            # per poi utilizzarla in caso di cambio velocità
            if(Force):
                curpos = 0

            self.player.songPosition = curpos

            curpos = round(curpos)
            cent = dt.timedelta(seconds = curpos)
            self.songTime.set(cent)

        curperc = self.player.query_percentage()
        if((curperc and curperc >= 0) or Force):
            if(Force):
                curperc = 0

            curperc = curperc / 1000000
            self.songProgress.set(curperc)
            self.scale.set(curperc)


    #def validate_int(self, d, i, P, s, S, v, V, W):
    #    print("d=", d, " i=", i, " P=",P," s=", s," S=", S, " v=",v," V=", V, " W=",W)
    def validate_int(self, S):
        try:
            int(S)
        except:
            return False
        else:
            return True

    def validate_neg_int(self, S, P):
        #print("d=", d, " i=", i, " P=",P," s=", s," S=", S, " v=",v," V=", V, " W=",W)
        
        regex = re.compile("^(-)?[0-9]*$")
        #print(regex.match(P))
        if(regex.match(P) == None):
            return False
        else:
            return True

    def speedChanged(self, a, b, c):
        self.entSpeed.delete(0, 'end')
        self.entSpeed.insert(0, str(self.varSpeed.get()))

        newtempo = self.varSpeed.get() * 0.01
        if(newtempo == self.player.tempo):
            return

        self.bValuesChanging = True
        try:
            # converte dalla percentuale a 1x
            # es: 80% = 0.8
            self.player.tempo = self.varSpeed.get() * 0.01
            curpos = self.player.songPosition
            self.player.set_speed(self.player.tempo)
            # hack to get gstreamer to calculate the position again
            if(curpos):
                self.player.seek_absolute(self.player.pipeline_time(curpos))
        finally:
            self.bValuesChanging = False

    def checkSpeed(self, event):
        try:
            value = int(self.entSpeed.get())
            if value < MIN_SPEED_PERCENT:
                value = MIN_SPEED_PERCENT
            elif value > MAX_SPEED_PERCENT:
                value = MAX_SPEED_PERCENT

            self.entSpeed.delete(0, 'end')
            self.entSpeed.insert(0, str(value))
            self.varSpeed.set(value)
        except:
            self.entSpeed.delete(0, 'end')
            self.entSpeed.insert(0, str(self.varSpeed.get()))

    def semitonesChanged(self, a, b, c):
        value = str(self.varPitchST.get())
        self.entPitchST.delete(0, 'end')
        self.entPitchST.insert(0, value)
        self.player.semitones = self.varPitchST.get()
        self.changePitch()

    def centsChanged(self, a, b, c):
        value = str(self.varPitchCents.get())
        self.entPitchCents.delete(0, 'end')
        self.entPitchCents.insert(0, value)
        self.player.cents = self.varPitchCents.get()
        self.changePitch()

    def volumeChanged(self, a, b, c):
        value = str(self.varVolume.get())
        self.entVolume.delete(0, 'end')
        self.entVolume.insert(0, value)
        self.player.volume = self.varVolume.get() * 0.01
        self.player.set_volume(self.player.volume)

    def changePitch(self):
        # converte da semitoni + centesimi
        # a unità pitch
        curpitch = self.player.semitones + (self.player.cents * 0.01)
        self.player.pitch = curpitch
        self.player.set_pitch(self.player.pitch)

    def checkSemitones(self, event):
        try:
            value = int(self.entPitchST.get())
            if value < MIN_PITCH_SEMITONES:
                value = MIN_PITCH_SEMITONES
            elif value > MAX_PITCH_SEMITONES:
                value = MAX_PITCH_SEMITONES

            self.entPitchST.delete(0, 'end')
            self.entPitchST.insert(0, str(value))
            self.varPitchST.set(value)
        except:
            self.entPitchST.delete(0, 'end')
            self.entPitchST.insert(0, str(self.varPitchST.get()))

    def checkCents(self, event):
        try:
            value = int(self.entPitchCents.get())
            if value < MIN_PITCH_CENTS:
                value = MIN_PITCH_CENTS
            elif value > MAX_PITCH_CENTS:
                value = MAX_PITCH_CENTS

            self.entPitchCents.delete(0, 'end')
            self.entPitchCents.insert(0, str(value))
            self.varPitchCents.set(value)
        except:
            self.entPitchCents.delete(0, 'end')
            self.entPitchCents.insert(0, str(self.varPitchCents.get()))

    def checkVolume(self, event):
        try:
            value = int(self.entVolume.get())
            if value < MIN_VOLUME:
                value = MIN_VOLUME
            elif value > MAX_VOLUME:
                value = MAX_VOLUME

            self.entVolume.delete(0, 'end')
            self.entVolume.insert(0, str(value))
            self.varVolume.set(value)
        except:
            self.entVolume.delete(0, 'end')
            self.entVolume.insert(0, str(self.varVolume.get()))

    def songSeek(self, val):
        dd, pp = self.player.update_position()
        if(dd != 0):
            newPos = val * dd
            self.player.seek_absolute(newPos)

    def resetDefaultVar(self, obj):
        if obj != None:
            try:
                if obj == self.varSpeed:
                    obj.set(DEFAULT_SPEED)
                elif obj == self.varPitchST:
                    obj.set(DEFAULT_SEMITONES)
                elif obj == self.varPitchCents:
                    obj.set(DEFAULT_CENTS)
            except:
                return

    def parseHotkey(self, event):
        key = event.keysym
        state = event.state
        #print("Key: ", key, " - State: ", state)

        move = 0
        accel = 0
        if(key == 'KP_1'):
            move = -STEPS_SEC_MOVE_1
        elif(key == 'KP_4'):
            move = -STEPS_SEC_MOVE_2
        elif(key == 'KP_7'):
            move = -STEPS_SEC_MOVE_3
        elif(key == 'KP_3'):
            move = STEPS_SEC_MOVE_1
        elif(key == 'KP_6'):
            move = STEPS_SEC_MOVE_2
        elif(key == 'KP_9'):
            move = STEPS_SEC_MOVE_3
        elif(key == 'KP_8'):
            accel = STEPS_SPEED
        elif(key == 'KP_5'):
            self.resetDefaultVar(self.varSpeed)
        elif(key == 'KP_2'):
            accel = -STEPS_SPEED
        elif(key == 'space' or key == 'KP_0'):
            self.togglePlay()
        elif(key == 'KP_Decimal'):
            self.player.Pause()
            self.player.Rewind()
            self.dispSongTime(Force=True)
        elif(key == 'Home'):
            self.player.Rewind()
            self.dispSongTime(Force=True)
        elif(key == 'KP_Add'):
            if(self.varPitchST.get() < MAX_PITCH_SEMITONES):
                self.varPitchST.set(self.varPitchST.get() + STEPS_SEMITONES)
        elif(key == 'KP_Subtract'):
            if(self.varPitchST.get() > MIN_PITCH_SEMITONES):
                self.varPitchST.set(self.varPitchST.get() - STEPS_SEMITONES)

        if(move != 0):
            self.bValuesChanging = True
            try:
                self.player.seek_relative(move)
            finally:
                self.bValuesChanging = False

        if(accel != 0):
            val = self.varSpeed.get() + accel
            if(val >= MIN_SPEED_PERCENT and val <= MAX_SPEED_PERCENT):
                self.varSpeed.set(val)

    def _hotkey_manager_(self, event):
        if(event.widget.winfo_class() != 'Entry'):
            app.parseHotkey(event)

        #print("Key: ", key, " - State: ", state)
        #pass

    def _click_manager_(self, event):
        widget = event.widget
        widget.focus_set()

        #print("Widget: ", widget.winfo_class())
        #pass

    def _tasks_(self):
        self.player.handle_message()
        self.songControl()
        self.dispSongTime()

        self.after(UPDATE_INTERVAL, self._tasks_)

parser = argparse.ArgumentParser()
parser.add_argument("media", nargs="?", help="URI of the media to open")

args = parser.parse_args()

app = App()

app.bind_all('<KeyPress>', app._hotkey_manager_)
app.bind_all('<1>', app._click_manager_)

app.after(10, app._tasks_)

app.mainloop()