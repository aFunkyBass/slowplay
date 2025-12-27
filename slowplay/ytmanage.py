import customtkinter as ctk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *
import subprocess
import os
import utils
import webbrowser
import json
import yt_dlp
import json

from sp_constants import *

import gettext
_ = gettext.gettext

YTDLP_CMD = "yt-dlp"
AUDIO_FORMAT_EXTENSION = "mp3"

class ytDialog(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        WIDTH = 600
        HEIGHT = 300

        # YouTube Manager object
        self.manager = ytManage()

        # Mark app directories
        working_dir = os.path.dirname(__file__)
        resources_dir = os.path.join(working_dir, "resources")
                
        self.wm_title(_("Open YouTube Video..."))
        
        #self.after(10)

        #self.attributes("-topmost", True)
        #self.overrideredirect(True)

        x = (self.winfo_screenwidth() / 2) - (WIDTH / 2)
        y = (self.winfo_screenheight() / 2) - (HEIGHT / 2)

        self.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))
        self.resizable(width=False, height=False)
        #self.minsize(width = 400, height = 300)

        self.TopFrame = ctk.CTkFrame(self, width=400, height=200)
        self.TopFrame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.dlButton = ctk.CTkButton(self, text=_("Open"), font=("", 14))
        self.dlButton.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")

        self.cancelButton = ctk.CTkButton(self, text=_("Cancel"), font=("", 14), command=self.destroy)
        self.cancelButton.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="w")

        self.rowconfigure(0, weight=1)
        self.columnconfigure([0, 1], weight=1)

        # Widgets in TopFrame
        self.URL_lbl = ctk.CTkLabel(self.TopFrame, text=_("URL: "))
        self.URL_lbl.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.URL_var = ctk.StringVar(self, value="")
        self.URL_entry = ctk.CTkEntry(self.TopFrame, placeholder_text=_("Paste a YouTube URL here..."))
        self.URL_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=8)

        self.searchBtn = ctk.CTkButton(self.TopFrame, width=40, text=_("S"), font=("", 14), 
                                       command= lambda: self.searchVideo())
        self.searchBtn.grid(row=0, column=2, sticky="e", padx=8, pady=8)

        self.InfoFrame = ctk.CTkFrame(self.TopFrame)
        self.InfoFrame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.TopFrame.columnconfigure(1, weight=1)
        self.TopFrame.rowconfigure(1, weight=1)

        # Widget on InfoFrame
        self.thumbNail = ctk.CTkLabel(self.InfoFrame, width=300, height=168)
        self.thumbNail.grid(row = 0, column = 0, rowspan = 3, sticky = "n")

        self.title = ctk.CTkLabel(self.InfoFrame, anchor = "w", wraplength=100,
                                  justify="left", font=("", LBL_FONT_SIZE, "bold"))
        self.title.grid(row = 0, column = 1, sticky = "nwe")

        self.author = ctk.CTkLabel(self.InfoFrame, justify="left", anchor = "w")
        self.author.grid(row = 1, column = 1, sticky = "nwe")

        self.views = ctk.CTkLabel(self.InfoFrame, justify="left", anchor = "w")
        self.views.grid(row = 2, column = 1, sticky = "nwe")

        self.InfoFrame.columnconfigure(1, weight=1)
        self.InfoFrame.rowconfigure(2, weight=1)

        self.bind("<Configure>", self.adjust_wrap)

    def adjust_wrap(self, event):
        self.title.configure(wraplength=self.title.winfo_width())
    
    def searchVideo(self):
        if(self.URL_entry.get() == ""):
            CTkMessagebox(master = self, title = _("Error: no URL specified"), 
                          message=_("Please paste a YouTube URL into the edit box"),
                          icon = "cancel", font = ("", LBL_FONT_SIZE))
            return(False)

        videoInfo = self.manager.getVideoInfoFields(self.URL_entry.get(),
                                            ["title", "description", "uploader",
                                             "timestamp", "view_count"])
        
        if(videoInfo is None or not isinstance(videoInfo, dict)):
            CTkMessagebox(master = self, title = _("Error: unable to find the video..."), 
                          message=_("Unable to retrieve the required video\n\n"+
                                    "Please make sure you entered a valid YouTube URL."),
                          icon = "cancel", font = ("", LBL_FONT_SIZE))
            return(False)
        else:
            #print(videoInfo)
            self.title.configure(text = videoInfo["title"])
            self.author.configure(text = _("by: ") + videoInfo["uploader"])
            self.views.configure(text = _("Views: ") + f"{videoInfo["view_count"]}")
        
        return(True)
    
    def show(self):
        self.deiconify()
        self.grab_set()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind_all(sequence="<KeyPress>", func=self._keybind_)
        #self.after(10)
        self.lift()
        self.attributes('-topmost',True)
        self.after_idle(self.attributes, '-topmost', False)
        self.wait_window(self)
        return(True)
    
    def _keybind_(self, event):
        key = event.keysym
        state = event.state
        #print("Key: ", key, " - State: ", state)

        if(key == "Escape" or key == "KP_Enter" or key == "Return"):
            self.destroy()

#
# Class to manage all the operation to be done on YouTube Video 
# with yt-dlp 
#
class ytManage:
    def __init__(self):
        self.bExternalCall = self.checkYTDLP()

    # Checks to see if yt-dlp is installed on the systme     
    def checkYTDLP(self):
        curEnv = utils.__get_env__()

        try:
            subprocess.run([YTDLP_CMD, "-h"], env = curEnv, capture_output = True, text = True)
            return(True)
        except:
            return(False)
    
    # Actually performs download the audio from the YouTube url
    def downloadAudioFile(self, ytURL = "", ouput_file = "", process_callback = None, show_output = False):
        #print("Url: " + ytURL)
        if(ytURL is None):
            return(False)

        # If no output filename is specified it generate a temporary filename
        o_fname = utils.__generate_random_temp_filename__("." + AUDIO_FORMAT_EXTENSION) if ouput_file == "" else ouput_file
        command = [
            YTDLP_CMD,
             '-x',                                      # Extract audio
             '--audio-format', AUDIO_FORMAT_EXTENSION,  # Audio format
             '-o', o_fname,                             # Output filename
             ytURL                                      # Video URL
        ]

        # Performs the os call and capture the stdout
        ret, ytOut = utils.capture_subprocess_output(command, process_callback, show_output)

        return(ytOut if ret != False else False)

        '''
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            errs = []
            for line in proc.stderr:
                print(command[0], line)
                errs.append(line)

            stdout, _ = proc.communicate()
        
        ytReturn = subprocess.CompletedProcess(command, proc.returncode, stdout, "\n".join(errs))
        '''

        #ytReturn = subprocess.run(command, capture_output=True)
        #print(ytReturn)

    # Retrieves the info from a Video and 
    # returns a dict with the fields requested in the list
    #
    # Example: getVideoInfoFields(["Title", "Author, Descritpion"]
    # -> {"Title" : "Video title", "Author": "The author"....}
    def getVideoInfoFields(self, ytURL = "", fieldList = []):
        if(len(fieldList) == 0):
            return(None)

        #print(fieldList)
        
        # Download the information about video in JSON format
        ytJson = self.getVideoInfo(ytURL)
        if(ytJson is None):
            return(None)

        # Transform the JSON into a Python dict        
        infoData = json.loads(ytJson)

        # Retrieves the required fields and put them into a new dict
        retDict = {}
        for field in fieldList:
            try:
                retDict[field] = infoData[field]
            except:
                continue
        
        return(retDict)
        

    # Get video info and returns it into a Json object
    def getVideoInfo(self, ytURL = ""):
        if(ytURL is None):
            return(None)

        command = [
            YTDLP_CMD,
             '-J', 
             ytURL
        ]
        
        ret, ytOut = utils.capture_subprocess_output(command)

        return(ytOut if ret != False else None)


#def gpOut(stream, mask):
#    print("GP: ", stream.readline())

#process = ["yt-dlp", "https://www.youtube.com/watch?v=iwI6qiL8Ofo"]

#capture_subprocess_output(process, gpOut)
#capture_subprocess_output(process)
