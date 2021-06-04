'''
exceptions
'''
class FFMPEG(Exception):
    '''
    ffmpeg error
    '''
    pass
class PortInUse(Exception):
    '''
    requested port already used
    '''
    pass

class NoEV3(Exception):
    '''
    no EV3 brick found
    '''
    pass

class MotorError(Exception):
    '''
    expected motor is not connected
    '''
    pass

class SensorError(Exception):
    '''
    expected sensor is not connected
    '''
    pass

class DirCmdError(Exception):
    '''
    direct command replies error
    '''
    pass

class SysCmdError(Exception):
    '''
    system command replies error
    '''
    pass
