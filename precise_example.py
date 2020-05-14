import pyaudio
import time
import collections
from ctypes import *
from contextlib import contextmanager
from precise_runner import PreciseRunner, ReadWriteStream, PreciseEngine


def py_error_handler(filename, line, function, err, fmt):
    pass

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


class Precise():
    
    def __init__(self):
        # engine data:      https://github.com/mycroftai/precise-data/tree/dist
        # precise models:   https://github.com/MycroftAI/precise-data/tree/models?files=1

        sensitivity = float(0.5)
        trigger_level = int(3)
        model_path = "hey-mycroft-2.pb"
        engine_path = "precise-engine/precise-engine"

        engine = PreciseEngine(
            engine_path, model_path, chunk_size=2048)

        self.ring_buffer = RingBuffer(16000 * 5)
        with no_alsa_error():
            self.audio = pyaudio.PyAudio()

        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(16 / 8),
            channels=1,
            rate=16000,
            frames_per_buffer=1024,
            stream_callback=self.audio_callback)

        self.stream = ReadWriteStream()

        runner = PreciseRunner(
            engine,
            stream=self.stream,
            sensitivity=sensitivity,
            trigger_level=trigger_level,
            on_activation=self.on_activation
        )
        print("Starting precise")
        runner.start()
        while True:
            data = self.ring_buffer.get()

            if len(data) == 0:
                time.sleep(0.03)
                continue
            self.update_runner(data)

    def update_runner(self, data):
        self.stream.write(data)

    def on_activation(self):
        print("Activation!")
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        self.ring_buffer.extend(in_data)
        play_data = chr(0) * len(in_data)
        return play_data, pyaudio.paContinue
        

Precise()
