from tkinter import messagebox

#argv = sys.argv
# work around Gstreamer parsing sys.argv!
#sys.argv = []

import gi
gi.require_version('Gst', '1.0')

from gi.repository import Gst

Gst.init(None)

TIME_FORMAT = Gst.Format(Gst.Format.TIME)
PERCENT_FORMAT = Gst.Format(Gst.Format.PERCENT)

class Replayer():
    def __init__(self):
        self.pipeline = Gst.Pipeline.new()

        self.audiosrc = Gst.ElementFactory.make("playbin", "player")
        self.pipeline.add(self.audiosrc)
        self.bin = Gst.Bin()

        #self.audiosrc = Gst.ElementFactory.make("filesrc")
        #self.decoder = Gst.ElementFactory.make("decodebin")
        #self.converter = Gst.ElementFactory.make("audioconvert")

        self.tempopitch = Gst.ElementFactory.make("pitch")
        self.pipevolume = Gst.ElementFactory.make("volume")

        if self.tempopitch is None:
            messagebox.showerror("Error", "You need to install the Gstreamer soundtouch elements for "
                    "this program to work. They are part of Gstreamer-plugins-bad. Consult the "
                    "README if you need more information.")
            raise SystemExit()

        #self.resampler = Gst.ElementFactory.make("audioresample")

        self.sink = Gst.ElementFactory.make("autoaudiosink")
        
        self.bin.add(self.tempopitch)
        self.bin.add(self.pipevolume)
        self.bin.add(self.sink)

        self.tempopitch.link(self.pipevolume)
        self.pipevolume.link(self.sink)

        sink_pad = Gst.GhostPad.new("sink", self.tempopitch.get_static_pad("sink"))
        self.bin.add_pad(sink_pad)

        self.audiosrc.set_property("audio-sink", self.bin)
        """

        self.pipeline = Gst.parse_launch("filesrc ! decodebin ! \
                                         audioconvert ! pitch ! \
                                         audioconvert ! audioresample ! \
                                         volume ! autoaudiosink")
        
        self.audiosrc = Gst.Bin.get_by_name(self.pipeline, "filesrc0")
        self.tempopitch = Gst.Bin.get_by_name(self.pipeline, "pitch0")
        self.pipevolume = Gst.Bin.get_by_name(self.pipeline, "volume0")
        """

        self.bus = self.pipeline.get_bus()

        self.media = ""
        self.canPlay = False
        self.isPlaying = False
        self.songPosition = 0
        self.tempo = 1
        self.semitones = 0
        self.cents = 0
        self.volume = 0
        self.updateInterval = 0

    def handle_message(self):
        message = self.bus.timed_pop_filtered(self.updateInterval * Gst.MSECOND,
            Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR |
            Gst.MessageType.EOS)# | Gst.MessageType.DURATION_CHANGED)

        if(message):
            t = message.type
            #print(t)
            if t == Gst.MessageType.EOS:
                #self.pipeline.set_state(Gst.State.NULL)
                self.Pause()
                self.Rewind()
            #elif t ==  Gst.MessageType.DURATION_CHANGED:
                #self.query_duration()
                #retval, duration = self.pipeline.query_duration(TIME_FORMAT)
                #print(f"Retval: {retval} - Duration: {duration}")
                #if(retval):
                #    self.duration = self.song_time(duration)
            elif t ==  Gst.MessageType.STATE_CHANGED:
                oldState, newState, _ = message.parse_state_changed()
                #print(f"Oldstate={oldState} - Newstate={newState}")
                if(newState == Gst.State.READY):
                    self.ReadyToPlay()
            elif t == Gst.MessageType.ERROR:
                self.pipeline.set_state(Gst.State.NULL)
                err, debug = message.parse_error()
                print("Error: %s" % err, debug)

        #self.update_position()

    def update_position(self):
        return(self.query_duration(), self.query_position())

        """
        retval, duration = self.pipeline.query_duration(TIME_FORMAT)
        #print(f"Retval: {retval} - Duration: {duration}")
        if(retval):
            self.duration = self.song_time(duration)
            #self.duration = duration / 1000000000

        retval, position = self.pipeline.query_position(TIME_FORMAT)
        #print(f"Position: {position} - Duration: {duration} - Duration (song_time): {self.duration} ")
        if(retval):
            #self.position = position / 1000000000
            self.position = self.song_time(position)
            #print(f"Position: {self.position} - Duration: {self.duration} ")
            return(position)
        return(None)
        """

    def seek_relative(self, newPos):
        duration, position = self.update_position()
        newPos = position + self.pipeline_time(newPos)

        if(newPos < 0):
            newPos = 0

        if(newPos >= 0 and newPos < duration):
            self.seek_absolute(newPos)

    def seek_absolute(self, newPos):
        if(self.pipeline.seek_simple(TIME_FORMAT, Gst.SeekFlags.FLUSH, newPos)):
            self.handle_message()

    def query_position(self):
        #retval, position = self.audiosrc.query_position(TIME_FORMAT)
        retval, position = self.pipeline.query_position(TIME_FORMAT)
        if(retval):
            return(position)

        return(None)

    def query_duration(self):
        #retval, duration = self.audiosrc.query_duration(TIME_FORMAT)
        retval, duration = self.pipeline.query_duration(TIME_FORMAT)
        if(retval):
            return(duration)

        return(None)

    def query_percentage(self):
        retval, percent = self.audiosrc.query_position(PERCENT_FORMAT)
        if(retval):
            return(percent)

        return(None)

    def get_speed(self):
        return self.tempopitch.get_property("tempo")

    def set_speed(self, speed):
        self.tempopitch.set_property("tempo", speed)

    def set_pitch(self, pitch):
        self.tempopitch.set_property("pitch", (2**(pitch/12.0)))

    def set_volume(self, volume):
        self.pipevolume.set_property("volume", volume)

    def pipeline_time(self, t):
        """convert from song position to pipeline time"""
        if(t):
            return t/self.get_speed()*1000000000
        else:
            return(None)

    def song_time(self, t):
        """convert from pipetime time to song position"""
        if(t):
            return t*self.get_speed()/1000000000
        else:
            return(None)

    def MediaLoad(self, mediafile):
        self.pipeline.set_state(Gst.State.NULL)
        if(str(mediafile).startswith('/')):
            mediafile = "file://" + mediafile
        self.audiosrc.set_property("uri", mediafile)
        
        #self.audiosrc.set_property("location", mediafile)

    def ReadyToPlay(self):
        self.canPlay = True
        return

    def fileSave(self, src, dest, callback = None):
        print(f"Src: {src} - Dest: {dest}")
        save_pipeline = Gst.parse_launch("filesrc name=""save_src"" ! decodebin ! \
                                         audioconvert ! pitch name=""save_pitch"" ! \
                                         audioconvert ! \
                                         ""audio/x-raw, format=(string)S16LE, rate=(int)44100, channels=(int)2"" ! \
                                         lamemp3enc ! filesink name=""save_sink""")

        save_audiosrc = Gst.Bin.get_by_name(save_pipeline, "save_src")
        save_tempopitch = Gst.Bin.get_by_name(save_pipeline, "save_pitch")
        save_sink = Gst.Bin.get_by_name(save_pipeline, "save_sink")

        save_audiosrc.set_property("location", src)
        save_tempopitch.set_property("tempo", self.tempopitch.get_property("tempo"))
        save_tempopitch.set_property("pitch", self.tempopitch.get_property("pitch"))
        save_sink.set_property("location", dest)

        save_bus = save_pipeline.get_bus()

        save_pipeline.set_state(Gst.State.PLAYING)

        while True:
            if(callback):
                qp = save_pipeline.query_position(PERCENT_FORMAT)
                if(qp[0] and qp[1] >= 0):
                    curperc = qp[1] / 1000000
                    callback(curperc)
  
            message = save_bus.timed_pop_filtered(self.updateInterval * Gst.MSECOND,
                        Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR |
                        Gst.MessageType.EOS)# | Gst.MessageType.DURATION_CHANGED)

            if(message):
                t = message.type
                #print(t)
                if t == Gst.MessageType.EOS:
                    save_pipeline.set_state(Gst.State.NULL)
                    break
                elif t ==  Gst.MessageType.STATE_CHANGED:
                    oldState, newState, _ = message.parse_state_changed()
                    #print(f"Oldstate={oldState} - Newstate={newState}")
                elif t == Gst.MessageType.ERROR:
                    self.pipeline.set_state(Gst.State.NULL)
                    err, debug = message.parse_error()
                    print("Error: %s" % err, debug)
                    break

        save_pipeline = None
    
    def Rewind(self):
        self.seek_absolute(0)

    def Play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.isPlaying = True

    def Pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)
        self.isPlaying = False
