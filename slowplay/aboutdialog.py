import customtkinter as ctk
from PIL import Image, ImageTk
import os
import webbrowser

from sp_constants import *


class imgDialog(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        WIDTH = 400
        HEIGHT = 500

        self.master = master

        working_dir = os.path.dirname(__file__)
        resources_dir = os.path.join(working_dir, "resources")

        self.wm_title("Numeric Keypad Map")
        
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
                
        self.wm_title("About")
        
        #self.after(10)

        #self.attributes("-topmost", True)
        #self.overrideredirect(True)

        x = (self.winfo_screenwidth() / 2) - (WIDTH / 2)
        y = (self.winfo_screenheight() / 2) - (HEIGHT / 2)

        self.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))
        self.resizable(width=False, height=False)
        #self.minsize(width = 400, height = 300)


        img = ctk.CTkImage(dark_image=Image.open(os.path.join(resources_dir, "Icona-96.png")), 
                                light_image=Image.open(os.path.join(resources_dir, "Icona-96.png")),
                                size=(96, 96))

        self.ico = ctk.CTkLabel(self, text="", image=img)
        self.ico.grid(row=0, column=0, rowspan=2, padx=10, sticky="ns")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=10, pady=10, sticky="ewsn")
        
        self.closeButton = ctk.CTkButton(self, text="Close", font=("", 14), command=self.destroy)
        self.closeButton.grid(row=1, column=1, pady=(8, 8), sticky="s")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        tab1 = self.tabview.add("About")
        tab2 = self.tabview.add("Shortcuts")
        #tab3 = self.tabview.add("Donate")

        # Widget on tab 1: "About"
        self.mainLabel = ctk.CTkLabel(tab1, text=APP_TITLE, justify="center", anchor="center", 
                                      compound="center", font=("", 28, "bold"))
        self.mainLabel.grid(row=0, column=0, pady=(10, 0), sticky="n")

        self.versLabel = ctk.CTkLabel(tab1, text=APP_VERSION, justify="center", anchor="center", 
                                      compound="center", font=("", 20))
        self.versLabel.grid(row=1, column=0, pady=(8, 0), sticky="n")

        self.authLabel = ctk.CTkLabel(tab1, text="Created by Guido Pietrella", justify="center", anchor="center", 
                                      compound="center", font=("", LBL_FONT_SIZE))
        self.authLabel.grid(row=2, column=0, sticky="n")

        self.linkLabel = ctk.CTkLabel(tab1, text=APP_URL, justify="center", anchor="center", 
                                      compound="center", text_color="#1f538d", font=("", LBL_FONT_SIZE), cursor="hand2")
        self.linkLabel.grid(row=3, column=0, sticky="n")
        self.linkLabel.bind("<1>", lambda e: self.openUrl(APP_URL))

        # Widget on tab 2: "Shorcuts"
        sc_list = [
            ("CTRL+R", "Open recent files list"),
            ("CTRL+Q", "Quit"),
            ("N. Keypad 0", "Play/Pause"),
            ("N. Keypad .", "Stop and rewind"),
            ("N. Keypad 1", "Rewind 5 seconds"),
            ("N. Keypad 4", "Rewind 10 seconds"),
            ("N. Keypad 7", "Rewind 15 seconds"),
            ("N. Keypad 3", "Forward 5 seconds"),
            ("N. Keypad 6", "Forward 10 seconds"),
            ("N. Keypad 9", "Forward 15 seconds"),
            ("Home", "Rewind"),
            ("N. Keypad 2", "Playback speed +5%"),
            ("N. Keypad 8", "Playback speed -5%"),
            ("N. Keypad 5", "Reset playback speed to 100%"),
            ("N. Keypad +", "Transpose +1 semitone"),
            ("N. Keypad -", "Transpose -1 semitone"),
        ]

        scrollFrame = ctk.CTkScrollableFrame(tab2)
        scrollFrame.grid(row = 0, column = 0, padx = (4), pady = (4), sticky="nsew")
        
        kpLabel = ctk.CTkButton(scrollFrame, text="SHOW NUM. KEYPAD MAP", command=self.imgShow)
        kpLabel.grid(row = 0, column = 0, columnspan = 2, sticky = "w", pady=(0, 10))

        scLabels = []
        i = 0
        for sc in sc_list:
            scLabels.append(ctk.CTkLabel(scrollFrame, text=f"{sc[0]}: ", font=("", LBL_FONT_SIZE, "bold")))
            scLabels.append(ctk.CTkLabel(scrollFrame, text=sc[1], font=("", LBL_FONT_SIZE)))
 
            scLabels[i].grid(row = i + 1, column = 0, sticky = "w")
            scLabels[i + 1].grid(row = i + 1, column = 1, sticky = "w")
            i = i + 2

        # Widget on tab 3: "Donate"
        """
        self.donateMainLabel = ctk.CTkLabel(tab3, text="Show your love...", justify="center", anchor="center", 
                                      compound="center", font=("", 20, "bold"))
        self.donateMainLabel.grid(row=0, column=0, pady=(10, 0), sticky="n")

        self.donateSubLabel = ctk.CTkLabel(tab3, text="...donate some satoshi!", justify="center", anchor="center", 
                                      compound="center")
        self.donateSubLabel.grid(row=1, column=0, sticky="n")

        self.donateBtcAddess = ctk.CTkLabel(tab3, text="...donate some satoshi!", justify="center", anchor="center", 
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