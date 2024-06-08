from pygame import mixer
from threading import Thread
from gd_constants import GDConstants
import time

mixer.init()

class AudioHandler:
    """ Does music/sfx related stuff in the game loop. Objects of this class contain a dedicated music thread,
    which is changed (recreated) every time the song/crash is played again. """
    
    CRASH_SOUND_PATH = "./assets/audio/crash.mp3"

    def __init__(self, song_filepath: str, start_offset: float = 0):
        self.song_filepath = song_filepath
        self.start_offset = start_offset
        self.song_playing = False
        self.thread: Thread = None
        """ The thread object the music is playing on. Is None until begin_playing_song is called at least once. """
        
        mixer.music.set_volume(GDConstants.AUDIO_VOLUME)

    def begin_playing_song(self) -> None:
        """ Begins playing the song from the start offset using this instance's decicated thread. """
        
        self.stop_playing_song()
        
        def play():
            mixer.music.load(self.song_filepath)
            mixer.music.play(start=self.start_offset)
            self.song_playing = True
            
            while mixer.music.get_busy() and self.song_playing:
                time.sleep(0.01)
        
        self.thread = Thread(target=play)
        self.thread.daemon = True
        self.thread.start()
        
    def stop_playing_song(self) -> None:
        """ Stops playing the current song. This also ends the thread. """
        mixer.music.stop()
        self.song_playing = False
        
    def stop_song_and_play_crash(self) -> None:
        """ Stops this instance's song and plays the crash sound. 
        Does not block the thread, so as soon as the play song func is called again, 
        this sound cuts off and the song starts immediately. """
        
        self.stop_playing_song()

        mixer.music.load(self.CRASH_SOUND_PATH)
        mixer.music.play()
