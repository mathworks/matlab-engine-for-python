#Copyright 2014 MathWorks, Inc.

from matlab.engine import pythonengine

class EngineSession():
    def __init__(self):
        try:      
            pythonengine.createProcess()
            self._process_created = True
        except:
            raise
        
    def __del__(self):
        self.release()
        
    def release(self):
        if self._process_created:
            try:
                pythonengine.closeProcess()
                self._process_created = False
            except:
                pass
