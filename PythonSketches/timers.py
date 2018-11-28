

from threading import Timer

# Base RepeatedTimer class from:
# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        # self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def set_interval(self, interval):
        self.interval = interval
        if self.is_running:
            self._timer.cancel()
        self._timer = Timer(self.interval, self._run)
        if self.is_running:
            self._timer.start()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def _bpm_call_rate_to_interval(bpm, calls_per_beat):
    return 60 / bpm / calls_per_beat

# Wrapper based on bpm
class MeteredTimer(RepeatedTimer):

    def __init__(self, bpm, calls_per_beat, function, *args, **kwargs):
        self.calls_per_beat = calls_per_beat
        self.bpm            = bpm
        self.interval       = _bpm_call_rate_to_interval(bpm, calls_per_beat)
        RepeatedTimer.__init__(self, self.interval, function, *args, **kwargs)

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.set_interval(_bpm_call_rate_to_interval(bpm, self.calls_per_beat))

    def set_call_freq(self, bpm, calls_per_beat):
        self.calls_per_beat = calls_per_beat
        self.bpm            = bpm
        self.set_interval(_bpm_call_rate_to_interval(bpm, calls_per_beat))
