#SlowPlay

---

==SlowPlay== is a simple audio player with speed/pitch change capabilities, based on GStreamer. It is meant to help music students/teachers transcribe music and play along with it.

###Inspiration
This software is heavily inspired, although not forked, by [Play It Slowly](https://github.com/jwagner/playitslowly) by Jonas Wagner.

I've been using Play It Slowly as my music classes companion for ages, but unfortunately it is no longer mantained and I started experiencing problems since I've updated my laptop OS, so I decided to rewrite it.

Thank you Jonas for your work.

##Features
==SlowPlay== can speed down/up songs or change their pitch independently "on the fly". It is possible export modified songs by using the "Save as..." button. 

You can import the most common audio files format (mp3, wav, flac, aif...). You can save your files either in mp3 or wav format, based on the extension of file to me be saved. Currently saved audio files are in the format of 44.1K 16bit stereo. Mp3 are saved as variable bitrate quality=4. Volume setting and metadata are ignored in the export operation.

###Requirements

For SlowPlay to work you need to have GStreamer along with Soundtouch plugins. While GStreamer is probably installed by default on your Linux box, you probably have to manually install the gstreamer-plugins-bad package. Please refer to your Linux distribution for the installation.

##Shortcuts

SlowPlay offers the following shortcuts:

- **NUM_KEYPAD_0**: Toggle Play/Pause
- **NUM_KEYPAD_.**: Stop and Rewind

- **NUM_KEYPAD_1**: Rewind 5 seconds
- **NUM_KEYPAD_4**: Rewind 10 seconds
- **NUM_KEYPAD_7**: Rewind 15 seconds

- **NUM_KEYPAD_3**: Forward 5 seconds
- **NUM_KEYPAD_6**: Forward 10 seconds
- **NUM_KEYPAD_9**: Forward 15 seconds

- **NUM_KEYPAD_8**: Increase speed by 5%
- **NUM_KEYPAD_2**: Decrease speed by 5%
- **NUM_KEYPAD_5**: Reset speed

- **NUM_KEYPAD_+**: Transpose +1 semitone
- **NUM_KEYPAD_-**: Transpose -1 semitone