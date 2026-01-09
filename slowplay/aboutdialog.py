import customtkinter as ctk
from PIL import Image, ImageTk
import os
import webbrowser

from sp_constants import *

import gettext
_ = gettext.gettext

class imgDialog(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        WIDTH = 400
        HEIGHT = 500

        self.master = master

        working_dir = os.path.dirname(__file__)
        resources_dir = os.path.join(working_dir, "resources")

        self.wm_title(_("Numeric Keypad Map"))
        
        self.after(10)

        self.attributes("-topmost", True)
        #self.overrideredirect(True)

        x = (self.winfo_screenwidth() / 2) - (WIDTH / 2)
        y = (self.winfo_screenheight() / 2) - (HEIGHT / 2)

        self.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))
        self.resizable(width=False, height=False)

        self.lift()

        self.pad = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT)
        self.pad.pack(expand = True, fill = "both")

        self.img_key = ctk.CTkImage(dark_image=Image.open(os.path.join(resources_dir, "Keypad_about.png")), 
                                light_image=Image.open(os.path.join(resources_dir, "Keypad_about.png")),
                                size=(WIDTH, HEIGHT))

        self.keypad = ctk.CTkLabel(self.pad, text="", image=self.img_key)
        self.keypad.pack(expand = True, fill = "both")

    def show(self):
        self.deiconify()
        self.transient(self.master)
        self.grab_set()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind_all(sequence="<KeyPress>", func=self._keybind_)
        self.bind_all(sequence="<1>", func=self._keybind_)
        self.after(10)
        self.wait_window(self)
        return(True)
    
    def _keybind_(self, event):
        key = event.keysym
        state = event.state
        #print("Key: ", key, " - State: ", state)
        self.destroy()

class aboutDialog(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        WIDTH = 500
        HEIGHT = 300

        # Mark app directories
        working_dir = os.path.dirname(__file__)
        resources_dir = os.path.join(working_dir, "resources")
                
        self.wm_title(_("About"))
        
        #self.after(10)

        #self.attributes("-topmost", True)
        #self.overrideredirect(True)

        x = (self.winfo_screenwidth() / 2) - (WIDTH / 2)
        y = (self.winfo_screenheight() / 2) - (HEIGHT / 2)

        self.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))
        self.resizable(width=False, height=False)
        #self.minsize(width = 400, height = 300)


        img = ctk.CTkImage(dark_image=Image.open(os.path.join(resources_dir, "Icona-64.png")), 
                                light_image=Image.open(os.path.join(resources_dir, "Icona-64.png")),
                                size=(64, 64))

        self.ico = ctk.CTkLabel(self, text="", image=img)
        self.ico.grid(row=0, column=0, rowspan=2, padx=10, sticky="ns")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=10, pady=10, sticky="ewsn")
        
        self.closeButton = ctk.CTkButton(self, text=_("Close"), font=("", 14), command=self.destroy)
        self.closeButton.grid(row=1, column=1, pady=(8, 8), sticky="s")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        tab1 = self.tabview.add(_("About"))
        tab2 = self.tabview.add(_("Shortcuts"))
        #tab3 = self.tabview.add(_("Donate"))

        # Widget on tab 1: "About"
        self.mainLabel = ctk.CTkLabel(tab1, text=APP_TITLE, justify="center", anchor="center", 
                                      compound="center", font=("", 28, "bold"))
        self.mainLabel.grid(row=0, column=0, pady=(10, 0), sticky="n")

        self.versLabel = ctk.CTkLabel(tab1, text=APP_VERSION, justify="center", anchor="center", 
                                      compound="center", font=("", 20))
        self.versLabel.grid(row=1, column=0, pady=(8, 0), sticky="n")

        self.authLabel = ctk.CTkLabel(tab1, text=_("Created by") + " Guido Pietrella", justify="center", anchor="center", 
                                      compound="center", font=("", LBL_FONT_SIZE))
        self.authLabel.grid(row=2, column=0, sticky="n")

        self.linkLabel = ctk.CTkLabel(tab1, text=APP_URL, justify="center", anchor="center", 
                                      compound="center", text_color="#1f538d", font=("", LBL_FONT_SIZE), cursor="hand2")
        self.linkLabel.grid(row=3, column=0, sticky="n")
        self.linkLabel.bind("<1>", lambda e: self.openUrl(APP_URL))

        # Widget on tab 2: "Shorcuts"
        SC_SECTION_TITLE = "-TITLE-"

        sc_list = [
            (SC_SECTION_TITLE, _("GENERAL SHORTCUTS:")),
            ("CTRL+R", _("Open recent files list")),
            ("CTRL+Y", _("Open YouTube dialog")),
            ("CTRL+Q", _("Quit")),
            (SC_SECTION_TITLE, _("PLAYBACK SHORTCUTS:")),
            ("N. Keypad 0", _("Play/Pause")),
            ("N. Keypad .", _("Stop and rewind")),
            ("N. Keypad 1", _("Rewind 5 seconds")),
            ("N. Keypad 4", _("Rewind 10 seconds")),
            ("N. Keypad 7", _("Rewind 15 seconds")),
            ("N. Keypad 3", _("Forward 5 seconds")),
            ("N. Keypad 6", _("Forward 10 seconds")),
            ("N. Keypad 9", _("Forward 15 seconds")),
            ("Home", _("Rewind")),
            ("N. Keypad 2", _("Playback speed +5%")),
            ("N. Keypad 8", _("Playback speed -5%")),
            ("N. Keypad 5", _("Reset playback speed to 100%")),
            ("N. Keypad +", _("Transpose +1 semitone")),
            ("N. Keypad -", _("Transpose -1 semitone")),
            (SC_SECTION_TITLE, _("LOOP SHORTCUTS:")),
            ("L", _("Toggle loop playing")),
            ("A", _("Set loop start")),
            ("B", _("Set loop end")),
            ("CTRL+A", _("Reset loop start")),
            ("CTRL+B", _("Reset loop end")),
        ]

        scrollFrame = ctk.CTkScrollableFrame(tab2)
        scrollFrame.grid(row = 0, column = 0, padx = (0), pady = (0), sticky="nsew")
        
        scLabels = []
        i = 0
        for sc in sc_list:
            if (sc[0] == SC_SECTION_TITLE):
                scLabels.append(ctk.CTkLabel(scrollFrame, text=sc[1], font=("", LBL_FONT_SIZE, "bold")))
                scLabels[i].grid(row = i, column = 0, sticky = "ew", columnspan = 2, pady=(10, 0))
                i = i + 1
            else:
                scLabels.append(ctk.CTkLabel(scrollFrame, text=f"{sc[0]}: ", font=("", LBL_FONT_SIZE, "bold")))
                scLabels.append(ctk.CTkLabel(scrollFrame, text=sc[1], font=("", LBL_FONT_SIZE)))
    
                scLabels[i].grid(row = i, column = 0, sticky = "w", pady=(0, 0))
                scLabels[i + 1].grid(row = i, column = 1, sticky = "w", pady=(0, 0))
                i = i + 2

        kpLabel = ctk.CTkButton(scrollFrame, text=_("SHOW NUM. KEYPAD MAP"), command=self.imgShow)
        kpLabel.grid(row = i + 1, column = 0, columnspan = 2, sticky = "w", pady=(10, 0))

        scrollFrame.grid_columnconfigure(0, weight=1)

        # Widget on tab 3: "Donate"
        """
        self.donateMainLabel = ctk.CTkLabel(tab3, text=_("Show your love..."), justify="center", anchor="center", 
                                      compound="center", font=("", 20, "bold"))
        self.donateMainLabel.grid(row=0, column=0, pady=(10, 0), sticky="n")

        self.donateSubLabel = ctk.CTkLabel(tab3, text=_("...donate some satoshi!"), justify="center", anchor="center", 
                                      compound="center")
        self.donateSubLabel.grid(row=1, column=0, sticky="n")

        self.donateBtcAddess = ctk.CTkLabel(tab3, text=_("...donate some satoshi!"), justify="center", anchor="center", 
                                      compound="center")
        self.donateBtcAddess.grid(row=4, column=0, pady=(8, 0), sticky="n")
        """
        
        tab1.grid_columnconfigure(0, weight=1)
        tab2.grid_columnconfigure(0, weight=1)
        tab2.grid_rowconfigure(0, weight=1)
        #tab3.grid_columnconfigure(0, weight=1)
    
    def openUrl(self, url):
        webbrowser.open_new(url)

    def imgShow(self):
        imgPopup = imgDialog(self)
        imgPopup.show()


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