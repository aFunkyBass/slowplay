import os
import json

USER_HOME_DIR = os.path.expanduser("~")
USER_CFG_DIR = os.path.join(USER_HOME_DIR, ".config")
APP_CFG_DIR = os.path.join(USER_CFG_DIR, "slowplay")
APP_CFG_FILENAME = os.path.join(APP_CFG_DIR, "slowplaycfg.json")

MAX_RECENTFILE_LIST = 16

CFG_APP_SECTION = "App"
CFG_RECENTFILE_SECTION = "Files"

### Definitions of the JSON keys in the configuration file
PBO_DEF_SPEED = "Speed"
PBO_DEF_SEMITONES = "Semitones"
PBO_DEF_CENTS = "Cents"
PBO_DEF_VOLUME = "Volume"

PBO_DEF_METADATA = "Metadata"
PBO_DEF_YOUTUBE = "YouTube"

YOUTUBE_METADATA_PREFIX = "(YT) - "

class AppSettings(object):
    def __init__(self, filename = ""):

        # Check for the existence of the config directory
        # and creates it if not
        if(not os.path.exists(APP_CFG_DIR)):
            os.makedirs(APP_CFG_DIR)

        self.bUpdateForbidden = False     # Disallow setting new values

        # Dictionary containing all the app settings
        self.settings = {
            CFG_APP_SECTION : {
                "LastOpenDir": USER_HOME_DIR,
                "LastSaveDir": USER_HOME_DIR,
                "MaxRecentFileList": MAX_RECENTFILE_LIST
            },
            CFG_RECENTFILE_SECTION: {}
        }

        if(filename == ""):
            self.settingsFilename = APP_CFG_FILENAME
        else:
            self.settingsFilename = filename

    
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
    
    # Gets the entire block of recent files as a dictionary
    def getRecentFiles(self):
        return(self.getSection(CFG_RECENTFILE_SECTION))

    # Gets the playback options for a recent opened file
    # If no file is found returns None
    def getRecentFile(self, filename):
        if(filename == ""):
            return(None)
        
        return(self.getVal(CFG_RECENTFILE_SECTION, filename, None))
   
    # Returns the name of the last played file
    # If no recent file is present returns none
    def getLastPlayedFilename(self):
        filelist = self.getRecentFiles()

        if(filelist is None):
            return(None)

        if(isinstance(filelist, dict)):
            if(len(filelist) <= 0):
                return(None)

            lastfile = list(filelist)[-1]
            
            #print(json.dumps(filelist, indent=2))
            #print(lastfile)
            return(lastfile)
   
    # Add playback options to the list of recent files
    def addRecentFile(self, filename, data, saveSettings = True):
        if(self.bUpdateForbidden == True):
            return(True)

        if(filename == ""):
            return(True)

        # Checks the max number of recent files and
        # pops out the first in case maximum is reached
        #
        # If the file is already present deletes the old entry
        # and adds it again, to make it the last one
        if(filename not in self.settings[CFG_RECENTFILE_SECTION]):
            if(self.recentFilesNum() >= self.getVal(CFG_APP_SECTION, "MaxRecentFileList", MAX_RECENTFILE_LIST)):
                self.popFirstItem()
        else:
            self.delRecentFile(filename)
        
        self.settings[CFG_RECENTFILE_SECTION][filename] = data

        # Optionally saves the config on disk
        if(saveSettings == True):
            return(self.saveSettings())
        else:
            return(True)
    
    # Deletes a recent file from the list
    def delRecentFile(self, filename):
        if(filename not in self.settings[CFG_RECENTFILE_SECTION]):
            return(False)
        
        del(self.settings[CFG_RECENTFILE_SECTION][filename])
        return(True)
    
    # Gets the number of recent files in the list
    def recentFilesNum(self):
        if(CFG_RECENTFILE_SECTION in self.settings and isinstance(self.settings[CFG_RECENTFILE_SECTION], dict)):
            return(len(self.settings[CFG_RECENTFILE_SECTION]))
        else:
            return(0)
    
    # If present, deletes the recent file from the list
    # and adds it again to make it the last item
    def moveToLastPosition(self, filename, saveSettings = True):
        data = self.getRecentFile(filename)
        
        if(data is None):
            return(False)

        del(self.settings[CFG_RECENTFILE_SECTION][filename])

        self.addRecentFile(filename, data, saveSettings)

    # Pops out the first file in the recent list
    # to make room for a new one.
    def popFirstItem(self):
        if(isinstance(self.settings[CFG_RECENTFILE_SECTION], dict) and len(self.settings[CFG_RECENTFILE_SECTION]) > 0):
            first_key = next(iter(self.settings[CFG_RECENTFILE_SECTION]))
            del(self.settings[CFG_RECENTFILE_SECTION][first_key])
            return(True)
        else:
            return(False)
    
    # Saves the current settings on the cfg file
    def saveSettings(self):
        if(self.bUpdateForbidden == True):
            return(True)
        
        #print(json.dumps(self.settings, indent = 2))
        #print("SCRITTURA")

        try:
            with open(self.settingsFilename, mode="w", encoding="utf-8") as outfile:
                json.dump(self.settings, outfile, ensure_ascii = False, indent = 2)

            return(True)
        except:
            return(False)

    # Saves settings from the cfg file
    def loadSettings(self):
        try:
            with open(self.settingsFilename, mode="r", encoding="utf-8") as infile:
                loadedSettings = json.load(infile)

                self.settings.update(loadedSettings)
                
                #print(json.dumps(self.settings, indent = 2))
                #print("LETTURA")
            return(True)
        except:
            return(False)