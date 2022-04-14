#Copyright 2014 MathWorks, Inc.

class RejectedExecutionError(Exception):
    """Exception raised from MATLAB engine"""
    
    def __init__(self,  message):
        self.message = message
    def __repr__(self):
        return self.message
        
        
    