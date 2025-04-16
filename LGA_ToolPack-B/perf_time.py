import nuke
import nukescripts

class PerfTime(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'Performance Timer', 'com.lega.perfTime')
        self.knob_start = nuke.PyScript_Knob('start', label='Start', command="nuke.startPerformanceTimers()")
        self.knob_reset = nuke.PyScript_Knob('reset', label='Reset', command="nuke.resetPerformanceTimers()")
        self.knob_stop = nuke.PyScript_Knob('stop', label='Stop', command="nuke.stopPerformanceTimers()")
        self.addKnob(self.knob_start)
        self.addKnob(self.knob_reset)
        self.addKnob(self.knob_stop)

def show_panel():
    p = PerfTime()
    p.show()


def add_perf_time_panel():
    global perf_time_panel
    perf_time_panel = PerfTime()
    return perf_time_panel.addToPane()