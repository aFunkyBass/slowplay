import subprocess
import os

import gettext
_ = gettext.gettext

ZEN_CMD = "zenity"

# Checks to see id Zenity is installed on the system
def __check_zenity__() -> bool:
  curEnv = __get_env__()
  try:
    subprocess.run([ZEN_CMD, "-h"], env = curEnv, capture_output = True, text = True)
    return(True)
  except:
    return(False)


# Function to restore the original LD_LIBRARY_PATH environment
# if the app is running as a frozen app with pyinstaller
def __get_env__():
  env = dict(os.environ)

  lp_key = 'LD_LIBRARY_PATH'

  lp_orig = env.get(lp_key + '_ORIG')

  if lp_orig is not None:
      env[lp_key] = lp_orig  # restore the original, unmodified value
  else:
      env.pop(lp_key, None)

  return(env)

# Start a file open dialog box
# if zenity is installed calls it it falls back on 
# Tkinter otherwise
def openFileDialog(title = None, filter = None, initialdir = None, initialfile = None):
  if(__check_zenity__()):
    return(__z_dialog__(**locals()))
  else:
    return(__tk_dialog__(**locals()))

# Start a file save as dialog box
# if zenity is installed calls it it falls back on 
# Tkinter otherwise
def saveFileDialog(title = None, filter = None, initialdir = None, initialfile = None, overwrite = False):
  save = True
  if(__check_zenity__()):
    return(__z_dialog__(**locals()))
  else:
    return(__tk_dialog__(**locals()))

# Pops up the zenity file selection
def __z_dialog__(title = None, filter = None, initialdir = None, initialfile = None, save = False, overwrite = False):
  # prepares the command array
  cmd = [ZEN_CMD, "--file-selection"]

  if(title is not None):
    cmd.append('--title')
    cmd.append(title)

  if(initialdir is None):
    initialdir = os.getcwd()

  if(initialfile is None):
    initialfile = ""
  
  filename = os.path.join(initialdir, initialfile)

  cmd.append('--filename')
  cmd.append(filename)

  # if save is true it open a save as dialgo box instead
  if(save):
    cmd.append("--save")
    # enables the overwrite warning
    if(overwrite):
      cmd.append("--confirm-overwrite")

  # creates a complex admitted extensions array starting from a simple tuple
  if(filter is not None):
    # example: mp3 -> MP3 files: *.mp3
    filetypes = [f"{str(x).upper()} files: *.{x}" for x in filter]
    
    # Insert all the extension together as the first available filter
    filetypes.insert(0, _("Supported files: ") + ' '.join(["*." + x for x in filter]))

    # Append the "All files: *" at the end of filter
    filetypes.append(_("All files: *"))
    
    # traverse the array and adds the extension to filter
    for f in filetypes:
      cmd.append("--file-filter")
      cmd.append(f)
  
  # restores the original LD_LIBRARY_PATH environment
  # Pyinstaller safe
  curEnv = __get_env__()

  # Launch zenity through a subprocess.run()
  try:
    result = subprocess.run(cmd, capture_output = True, text = True, env = curEnv)
    return(result.stdout.strip())
  except:
    return(None)

# Pops up the TKInter file selection
def __tk_dialog__(title = None, filter = None, initialdir = None, initialfile = None, save = False, overwrite = False):
  from tkinter import Tk
  import tkinter.filedialog

  # creates a complex admitted extensions array starting from a simple tuple
  filetypes = []

  # Insert all the extension together as the first available filter
  filetypes.append((_("Supported files:"),  ' '.join(["*." + x for x in filter])))

  # example: mp3 -> (MP3 files), (*.mp3)
  for x in filter:
    filetypes.append((f"{str(x).upper()} files", f"*.{x}"))

  # Append the "All files: *" at the end of filter
  filetypes.append((_("All files"), "*.*"))

  # Creates a parent window without displaying it
  root = Tk()
  root.withdraw()

  # Launch the selected file dialog
  if(save):
    f = tkinter.filedialog.asksaveasfilename(parent = root, initialdir = initialdir,
                                             initialfile = initialfile, title = title,
                                             filetypes =  filetypes, confirmoverwrite = overwrite)
  else:
    f = tkinter.filedialog.askopenfilename(parent = root, initialdir = initialdir,
                                           initialfile = initialfile, title = title, 
                                           filetypes = filetypes)

  if(len(f) == 0):
    retFile = None
  else:
    retFile = f

  root.destroy()
  return(retFile)