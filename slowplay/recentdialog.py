import customtkinter as ctk
from CTkListbox import *
import os

import gettext
_ = gettext.gettext

class recentDialog(ctk.CTkToplevel):
    def __init__(self, parent, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title(_("Select recent file..."))
        
        self.attributes("-topmost",True)
        
        self.data = data
        self.geometry("600x300")
        self.minsize(width = 400, height = 200)

        self.LFrame = ctk.CTkFrame(self)
        self.RFrame = ctk.CTkFrame(self, width=120)

        self.LFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.RFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.ListBox = CTkListbox(self.LFrame, font=("", 16))
        self.ListBox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.ListBox.bind("<Double-1>", self.onOk)

        self.LFrame.grid_rowconfigure(0, weight=1)
        self.LFrame.grid_columnconfigure(0, weight=1)

        self.okButton = ctk.CTkButton(self.RFrame, text=_("OK"), font=("", 18), command=self.onOk)
        self.okButton.grid(row=0, column=0, pady=(8, 0), sticky="w")

        self.cancelButton = ctk.CTkButton(self.RFrame, text=_("Cancel"), font=("", 18), command=self.destroy)
        self.cancelButton.grid(row=1, column=0, pady=(8, 0), sticky="w")

        self.togglePath = ctk.CTkCheckBox(self.RFrame, text=_("Show full path"), command=self.checkBoxToggle)
        self.togglePath.grid(row=2, column=0, pady=(8, 0), sticky="w")

        self.selection = ""

    def checkBoxToggle(self):
        self.fillListbox()

    def fillListbox(self):
        self.ListBox.delete("all")

        if(self.togglePath.get() == 0):
            for k in reversed(self.data):
                self.ListBox.insert(k, os.path.basename(k))
        else:
            for k in reversed(self.data):
                self.ListBox.insert(k, k)
        
        self.ListBox.activate(0)

    def onOk(self, event = None):
        self.selection = list(self.data)[(len(self.data) - 1) - self.ListBox.curselection()]
        self.destroy()

    def show(self):
        self.fillListbox()
        self.deiconify()
        self.grab_set()
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return(self.selection)