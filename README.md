	# SmartLock
Proyecto de Robótica	

Testing Remote

Addding new line
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


Traceback (most recent call last):
  File "/home/smartlock/Documents/SmartLock/main.py", line 1, in <module>
    from Detector import main_app
  File "/home/smartlock/Documents/SmartLock/Detector.py", line 4, in <module>
    import picamera
  File "/usr/local/lib/python3.9/dist-packages/picamera/__init__.py", line 72, in <module>
    from picamera.exc import (
  File "/usr/local/lib/python3.9/dist-packages/picamera/exc.py", line 41, in <module>
    import picamera.mmal as mmal
  File "/usr/local/lib/python3.9/dist-packages/picamera/mmal.py", line 49, in <module>
    _lib = ct.CDLL('libmmal.so')
  File "/usr/lib/python3.9/ctypes/__init__.py", line 374, in __init__
    self._handle = _dlopen(self._name, mode)
OSError: libmmal.so: cannot open shared object file: No such file or directory
