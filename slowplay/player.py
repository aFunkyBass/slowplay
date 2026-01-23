from CTkMessagebox import CTkMessagebox
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst # type: ignore

import gettext
_ = gettext.gettext

Gst.init(None)

TIME_FORMAT = Gst.Format(Gst.Format.TIME)
PERCENT_FORMAT = Gst.Format(Gst.Format.PERCENT)

NANOSEC = 1000000000

GST_DEFAULT_SINK = "autoaudiosink"

WAV_ENCODER = "wavenc"
MP3_ENCODER = "lamemp3enc"

class slowPlayer():
    def __init__(self, customsink = None):

        # Creates a pipeline
        self.pipeline = Gst.Pipeline.new()

        # Use the Playbin3 element
        self.audiosrc = Gst.ElementFactory.make("playbin3", "player")
        self.pipeline.add(self.audiosrc)
        self.bin = Gst.Bin()

        #self.audiosrc = Gst.ElementFactory.make("filesrc")
        #self.decoder = Gst.ElementFactory.make("decodebin")
        #self.converter = Gst.ElementFactory.make("audioconvert")

        self.tempopitch = Gst.ElementFactory.make("pitch")
        self.converter = Gst.ElementFactory.make("audioconvert")
        self.pipevolume = Gst.ElementFactory.make("volume")
        
        if self.tempopitch is None:
            CTkMessagebox(title=_("Error"), icon="cancel", 
                          message=_("You need to install the Gstreamer soundtouch elements for this program to work."))
            raise SystemExit()

        #self.resampler = Gst.ElementFactory.make("audioresample")

        # Use a custom sink if specified on the command line
        if(customsink is not None):
            self.sink = Gst.ElementFactory.make(customsink)
            if(self.sink is None):
                print(_("Error: impossible to instantiate sink: '{}'. Reverting to default sink").format(customsink))
                self.sink = Gst.ElementFactory.make(GST_DEFAULT_SINK)
        else:
            self.sink = Gst.ElementFactory.make(GST_DEFAULT_SINK)
        
        self.bin.add(self.tempopitch)
        self.bin.add(self.converter)
        self.bin.add(self.pipevolume)
        self.bin.add(self.sink)

        self.converter.link(self.tempopitch)
        self.tempopitch.link(self.pipevolume)
        self.pipevolume.link(self.sink)

        sink_pad = Gst.GhostPad.new("sink", self.converter.get_static_pad("sink"))
        self.bin.add_pad(sink_pad)

        self.audiosrc.set_property("audio-sink", self.bin)

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
        self.startPoint = 0
        self.endPoint = 0
        self.loopEnabled = False

        self.title = ""
        self.artist = ""

    def handle_message(self):
        message = self.bus.timed_pop_filtered(self.updateInterval * Gst.MSECOND,
            Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR |
            Gst.MessageType.TAG | Gst.MessageType.EOS)# | Gst.MessageType.DURATION_CHANGED)

        if(message):
            t = message.type
            #print(t)
            if t == Gst.MessageType.EOS:
                #self.pipeline.set_state(Gst.State.NULL)
                self.Pause()
                self.Rewind()
            elif t == Gst.MessageType.TAG:
                if(self.artist == "" and self.title == ""):
                    tags = message.parse_tag()
                    
                    ret = tags.get_string("artist")
                    if(ret[0]):
                        self.artist = ret[1]
                    
                    ret = tags.get_string("title")
                    if(ret[0]):
                        self.title = ret[1]
                #tagsNum = tags.n_tags()
                #for i in range(0, tagsNum):
                #    print(tags.nth_tag_name(i))

            #elif t ==  Gst.MessageType.DURATION_CHANGED:
                #print("Duration changed")
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

    def getState(self):
        return(self.pipeline.get_state(Gst.CLOCK_TIME_NONE))

    def get_speed(self):
        return self.tempopitch.get_property("tempo")

    def set_speed(self, speed):
        self.tempopitch.set_property("tempo", speed)

    def set_pitch(self, pitch):
        self.tempopitch.set_property("pitch", (2 ** (pitch / 12.0)))

    def set_volume(self, volume):
        self.pipevolume.set_property("volume", volume)

    # Convert from song position to pipeline time
    def pipeline_time(self, t):
        if(t):
            return(t / self.get_speed() * NANOSEC)
        else:
            return(None)

    # Convert from pipetime time to song position
    def song_time(self, t):
        if(t):
            return(t * self.get_speed() / NANOSEC)
        else:
            return(None)

    def MediaLoad(self, mediafile):
        self.pipeline.set_state(Gst.State.NULL)
        self.title = ""
        self.artist = ""

        if(str(mediafile).startswith('/')):
            mediafile = "file://" + mediafile
        self.audiosrc.set_property("uri", mediafile)
        
        #self.audiosrc.set_property("location", mediafile)

    def ReadyToPlay(self):
        self.canPlay = True
        return

    def fileSave(self, src, dest, callback = None):
        #print(f"Src: {src} - Dest: {dest}")

        if(str(dest).endswith("wav")):
            encoder = WAV_ENCODER
        else:
            encoder = MP3_ENCODER
        
        save_pipeline = Gst.Pipeline.new()
        
        save_audiosrc = Gst.ElementFactory.make("playbin3")
        save_pipeline.add(save_audiosrc)
        
        save_bin = Gst.Bin()

        save_tempopitch = Gst.ElementFactory.make("pitch")
        save_audioconvert = Gst.ElementFactory.make("audioconvert")
        save_audioresample = Gst.ElementFactory.make("audioresample")
        save_encoder = Gst.ElementFactory.make(encoder)
        save_mux = Gst.ElementFactory.make("id3v2mux")
        save_sink = Gst.ElementFactory.make("filesink")

        save_bin.add(save_tempopitch)
        save_bin.add(save_audioconvert)
        save_bin.add(save_audioresample)
        save_bin.add(save_encoder)
        save_bin.add(save_mux)
        save_bin.add(save_sink)

        save_tempopitch.link(save_audioconvert)
        save_audioconvert.link(save_audioresample)
        save_audioresample.link(save_encoder)
        save_encoder.link(save_mux)
        save_mux.link(save_sink)

        save_sink_pad = Gst.GhostPad.new("sink", save_tempopitch.get_static_pad("sink"))
        save_bin.add_pad(save_sink_pad)
        save_audiosrc.set_property("audio-sink", save_bin)

        save_bus = save_pipeline.get_bus()

        save_audiosrc.set_property("uri", src)
        save_tempopitch.set_property("tempo", self.tempopitch.get_property("tempo"))
        save_tempopitch.set_property("pitch", self.tempopitch.get_property("pitch"))
        save_sink.set_property("location", dest)

        # Sets the encoder to constant bitrate
        if(encoder == MP3_ENCODER):
            save_encoder.set_property("target", "bitrate")
            save_encoder.set_property("bitrate", 192)
            save_encoder.set_property("cbr", "true")

        save_pipeline.set_state(Gst.State.PLAYING)

        while True:
            if(callback):
                qp = save_pipeline.query_position(PERCENT_FORMAT)
                if(qp[0] and qp[1] >= 0):
                    curperc = qp[1] / 1000000
                    if(callback(curperc) == False):
                        save_pipeline.set_state(Gst.State.PAUSED)
                        save_pipeline.set_state(Gst.State.NULL)
                        break
  
            message = save_bus.timed_pop_filtered(self.updateInterval * Gst.MSECOND,
                        Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR |
                        Gst.MessageType.EOS)

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
        if(self.loopEnabled):
            self.seek_absolute(self.startPoint)
        else:
            self.seek_absolute(0)

    def Play(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.isPlaying = True

    def Pause(self):
        self.pipeline.set_state(Gst.State.PAUSED)
        self.isPlaying = False