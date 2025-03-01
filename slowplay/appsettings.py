import os
import sys, pathlib
import json

USER_HOME_DIR = os.path.expanduser("~")
USER_CFG_DIR = f"{USER_HOME_DIR}/.config"
APP_CFG_DIR = f"{USER_CFG_DIR}/slowplay"
APP_CFG_FILENAME = f"{APP_CFG_DIR}/slowplaycfg.json"

MAX_RECENTFILE_LIST = 3

class AppSettings(object):
    def __init__(self, filename = ""):

        self.bUpdateForbidden = False     # Disallow setting new values

        self.settings = {
            "App" : {
                "LastOpenDir": USER_HOME_DIR,
                "LastSaveDir": USER_HOME_DIR,
                "MaxRecentFileList": MAX_RECENTFILE_LIST
            },
            "Files": {}
        }
    
    # Fetches a value from the settings dict
    # If value is not present return defval
    def getVal(self, Section, Subsection, defval = None):
        if(Section in self.settings):
            if(Subsection in self.settings[Section]):
                return(self.settings[Section][Subsection])
        
        return(defval)

    # Saves a value in the settings dict
    # Optionally saves the settings on disk
    def setVal(self, Section, Subsection, Newval, saveSettings = True):
        if(self.bUpdateForbidden == True):
            return(True)

        self.settings[Section][Subsection] = Newval

        if(Section in self.settings):
            if(Subsection in self.settings[Section]):
                if(self.settings[Section][Subsection] == Newval):
                    if(saveSettings == True):
                        return(self.saveSettings())
                    else:
                        return(True)
        
        return(False)

    # Gets an entire section of the settings dict (top level)
    def getSection(self, Section):
        if(Section in self.settings):
            return(self.settings[Section])
        else:
            return(None)

    # Gets the playback options for a recent opened file
    # If no file is found returns None
    def getRecentFile(self, filename):
        if(filename == ""):
            return(None)
        
        return(self.getVal("Files", filename, None))
   
    # Add playback options to the list of recent files
    def addRecentFile(self, filename, data, saveSettings = True):
        if(self.bUpdateForbidden == True):
            return(True)

        if(filename == ""):
            return(True)

        # Checks the max number of recent files and
        # pops out the first in case maximum is reached
        if(filename not in self.settings["Files"] and
                     self.recentFilesNum() >= self.getVal("App", "MaxRecentFileList", MAX_RECENTFILE_LIST)):
            self.popFirstItem()
        
        self.settings["Files"][filename] = data

        # Optionally saves the config on disk
        if(saveSettings == True):
            return(self.saveSettings())
        else:
            return(True)
    
    # Gets the number of recent files in the list
    def recentFilesNum(self):
        if("Files" in self.settings and isinstance(self.settings["Files"], dict)):
            return(len(self.settings["Files"]))
        else:
            return(0)
    
    # Pops out the first file in the recent list
    # to make room for a new one.
    def popFirstItem(self):
        if(isinstance(self.settings["Files"], dict) and len(self.settings["Files"]) > 0):
            first_key = next(iter(self.settings["Files"]))
            del(self.settings["Files"][first_key])
            return(True)
        else:
            return(False)
    
    def saveSettings(self):
        if(self.bUpdateForbidden == True):
            return(True)
        print(json.dumps(self.settings, indent = 2))
        return(True)
