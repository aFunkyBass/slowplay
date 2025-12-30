#
# https://gist.github.com/nawatts/e2cdca610463200c12eac2a14efc0bfb
#
import customtkinter as ctk
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
from CTkToolTip import *
import subprocess
import os
import utils
import json
import json
import hashlib

from sp_constants import *

import gettext
_ = gettext.gettext

YTDLP_CMD = "yt-dlp"
AUDIO_FORMAT_EXTENSION = "mp3"
THUMB_FORMAT_EXTENSION = "png"

class ytDialog(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        WIDTH = 600
        HEIGHT = 300

        # YouTube Manager object
        self.manager = ytManage()

        self.retValue = False

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

        self.dlButton = ctk.CTkButton(self, text=_("Open"), font=("", 14), 
                                      state = ctk.DISABLED, command = self.onDownload)
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

        YTIcon = ctk.CTkImage(light_image=Image.open(f"{resources_dir}/YT_ico.png"),
                                 dark_image=Image.open(f"{resources_dir}//YT_ico.png"), size=(23, 16))

        self.searchBtn = ctk.CTkButton(self.TopFrame, width=40, text="", font=("", 14), 
                                       image=YTIcon, command= lambda: self.searchVideo())
        self.searchBtn.grid(row=0, column=2, sticky="e", padx=8, pady=8)
        self.searchBtn_tt = CTkToolTip(self.searchBtn, message=_("Click to search YouTube video"),
                                        delay=0.8, alpha=0.5, justify="left", follow=False)
        self.InfoFrame = ctk.CTkFrame(self.TopFrame)
        self.InfoFrame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.TopFrame.columnconfigure(1, weight=1)
        self.TopFrame.rowconfigure(1, weight=1)

        # Widget on InfoFrame
        self.thumbnail = ctk.CTkLabel(self.InfoFrame, width=300, height=168, text="")
        self.thumbnail.grid(row = 0, column = 0, rowspan = 3, sticky = "n", padx = 10, pady = 10)

        self.title = ctk.CTkLabel(self.InfoFrame, anchor = "w", wraplength=100,
                                  justify="left", font=("", LBL_FONT_SIZE, "bold"),
                                  text="")
        self.title.grid(row = 0, column = 1, sticky = "nwe", pady=10)

        self.author = ctk.CTkLabel(self.InfoFrame, justify="left", anchor = "w", text="")
        self.author.grid(row = 1, column = 1, sticky = "nwe")

        self.views = ctk.CTkLabel(self.InfoFrame, justify="left", anchor = "w", text="")
        self.views.grid(row = 2, column = 1, sticky = "nwe")

        self.InfoFrame.columnconfigure(1, weight=1)
        self.InfoFrame.rowconfigure(2, weight=1)

        self.bind("<Configure>", self.adjust_wrap)

    # Function to adjust the wraplength of title entry
    def adjust_wrap(self, event):
        self.title.configure(wraplength=self.title.winfo_width())

    # Reset all the search parameters
    def resetSearch(self):
        self.thumbnail.configure(image = None)
        self.title.configure(text = "")
        self.author.configure(text = "")
        self.views.configure(text = "")
        
        self.manager.reset()
        self.dlButton.configure(state = ctk.DISABLED)
    
    def searchVideo(self):
        if(self.URL_entry.get() == ""):
            CTkMessagebox(master = self, title = _("Error: no URL specified"), 
                          message=_("Please paste a YouTube URL into the edit box"),
                          icon = "cancel", font = ("", LBL_FONT_SIZE))
            return(False)

        # Reset search parameters and blank all the result fields
        self.resetSearch()
        self.update()
        self.update_idletasks()

        # set the URL and prepare the search
        self.manager.setURL(self.URL_entry.get())
        
        # Download the required info and fill the fields
        videoInfo = self.manager.getVideoInfoFields(["title", "description", "uploader",
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

        # Download and display the video thumbnail
        thmb = self.manager.getVideoThumbnail()
        if(thmb == False):
            CTkMessagebox(master = self, title = _("Error: unable to download the thumbnail..."), 
                          message=_("Unable to retrieve the video thubnail\n\n"+
                                    "Uhmmmmm... This is very strange"),
                          icon = "cancel", font = ("", LBL_FONT_SIZE))
            return(False)
        else:
            img = Image.open(self.manager.thumbnail)
            thumbImage = ctk.CTkImage(dark_image = img, light_image = img,
                                size=[self.thumbnail.winfo_width(), self.thumbnail.winfo_height()])
            self.thumbnail.configure(image = thumbImage)

        # Enable the download button
        self.dlButton.configure(state=ctk.NORMAL)

        return(True)
    
    # Close the dialog and returns the current URL
    def onDownload(self):
        self.retValue = self.manager.curURL
        self.destroy()
    
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
        return(self.retValue, self.manager.videoMetadata)
    
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
    def __init__(self, aUrl: str = ""):

        # URL of the video
        self.curURL = ""

        # Output filename
        self.outFile = ""

        # Output audio filename
        self.audioFile = ""

        # Video info storage
        self.videoInfo = {}

        # Video selected metadata
        self.videoMetadata = {}

        # Video thumbnail
        self.thumbnail = None

        if(aUrl != ""):
            self.setURL(aUrl)

        self.bExternalCall = self.checkYTDLP()

    # Checks to see if yt-dlp is installed on the system
    def checkYTDLP(self):
        curEnv = utils.__get_env__()

        try:
            subprocess.run([YTDLP_CMD, "-h"], env = curEnv, capture_output = True, text = True)
            return(True)
        except:
            return(False)
    
    # Actually performs download the audio from the YouTube url
    def downloadAudioFile(self, process_callback = None, show_output = False):
        #print("Url: " + ytURL)
        if(self.curURL is None):
            return(None)

        command = [
            YTDLP_CMD,
             '-x',                                      # Extract audio
             '--audio-format', AUDIO_FORMAT_EXTENSION,  # Audio format
             '--no-playlist',                           # Only consider the single file
             '-o', self.outFile,                        # Output filename
             self.curURL                                # Video URL
        ]

        # Performs the os call and capture the stdout
        ret, ytOut = utils.capture_subprocess_output(command, process_callback, show_output)

        return(ytOut if ret != False else False)

    # Retrieves the info from a Video and 
    # returns a dict with the fields requested in the list
    #
    # Example: getVideoInfoFields(["Title", "Author, Descritpion"]
    # -> {"Title" : "Video title", "Author": "The author"....}
    def getVideoInfoFields(self, fieldList = []):
        if(self.curURL is None):
            return(None)

        if(len(fieldList) == 0):
            return(None)

        #print(fieldList)
        
        # Download the information about video in JSON format
        if(self.videoInfo is None or len(self.videoInfo) == 0):
            if(self.getVideoInfo() == False):
                return(None)

        # Retrieves the required fields and put them into a new dict
        self.videoMetadata = {}
        for field in fieldList:
            try:
                self.videoMetadata[field] = self.videoInfo[field]
            except:
                continue

        return(self.videoMetadata)

    # Download the thumbnail for the Video and saves it into a temporary PNG file
    def getVideoThumbnail(self, process_callback = None, show_output = False):
        if(self.curURL is None):
            return(False)

        if(self.thumbnail is not None):
            return(True)

        command = [
            YTDLP_CMD,
             '--skip-download',                             # Doesn't download the video
             '--write-thumbnail',                           # Write thumbnail on disk
             '--convert-thumbnail', THUMB_FORMAT_EXTENSION, # Audio format
             '--no-playlist',                               # Only consider the single file
             '-o', self.outFile,                            # Output filename
             self.curURL                                    # Video URL
        ]

        # Performs the os call and capture the stdout
        ret, _ = utils.capture_subprocess_output(command, process_callback, show_output)

        if(ret):
            self.thumbnail = '.'.join([self.outFile, THUMB_FORMAT_EXTENSION])
            return(True)
        else:
            return(False)


    # Get video info and returns it into a Json object
    def getVideoInfo(self):
        if(self.curURL is None):
            return(None)

        command = [
            YTDLP_CMD,
             '-J', 
             '--no-playlist',                  # Only consider the single file
             self.curURL
        ]
        
        ret, ytOut = utils.capture_subprocess_output(command)

        if(ret):
            self.videoInfo = json.loads(ytOut)
            return(True)
        else:
            return(False)

    # Set the specified the URL and prepares the class to work on iy
    def setURL(self, newURL):
        if(newURL == ""):
            return(False)

        # Reset all values
        self.reset()

        # Makes a SHA256 hash of the specified URL and uses it as 
        # name for temporary files. 
        # This is done because if the same URL is specified twice in a
        # session, the files is not downloaded again.
        self.curURL = newURL
        self.outFile = utils.__generate_temp_filename__(
                                hashlib.sha256(str(newURL).encode('ASCII')).hexdigest())
        self.audioFile = '.'.join([self.outFile, AUDIO_FORMAT_EXTENSION])

    def reset(self):
        self.curURL = ""
        self.outFile = ""
        self.videoInfo = {}
        self.thumbnail = None