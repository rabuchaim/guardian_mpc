__all__ = ["ElapsedTimer","ElapsedTimeDecorator"]  

import logging
logger = logging.getLogger("django.request")

##──── A simple decorator to get the elapsed time of a function - from package etimedecorator by ricardoabuchaim@gmail.com ──────
def ElapsedTimeDecorator(decimal_places:int=6,print_args:bool=False):
    """Just displays the elapsed time on every call
    
    Output on every call: Elapsed Time for method_name(): 0.000003485 sec
    """
    arguments = ''
    def decorator(method):
        nonlocal arguments
        def decorated_method(*args, **kwargs):
            nonlocal arguments
            try:
                startTime = time.monotonic()
                result = method(*args, **kwargs)
                if print_args:
                    arguments = f'{args if args else ""}{str(kwargs).replace(": ",":") if kwargs else ""}'
                logger.info(f'\033[33mElapsed Time for {method.__name__}({arguments}): %.{decimal_places}f sec'%(time.monotonic()-startTime)+"\033[0m")
                return result
            except Exception as ERR:
                logger.info('\033[91m'+f"[ELAPSED_TIME_EXCEPTION] {method.__name__}(): {str(ERR)}"+'\033[0m')
        return decorated_method
    return decorator
    
##──── ElapsedTimer ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
import time,math
class ElapsedTimer:
    """A simple context manager to measure the elapsed time in seconds - by ricardoabuchaim@gmail.com

       Usage:
            with ElapsedTimer() as elapsed:
                print(elapsed.text(decimal_places=6, end_text=" seconds.", with_brackets=False))
    """
    def __init__(self):
        self.start = time.monotonic()
        self.time = None
    def __enter__(self):
        return self
    def __exit__(self,_type,value,traceback):
        self.time = time.monotonic() - self.start
    def time_as_float(self,decimal_places:int=6)->float:
        return math.trunc((time.monotonic()-self.start)*(10**decimal_places))/(10**decimal_places)
    def text(self,decimal_places:int=6,end_text:str="",begin_text:str="",with_brackets=True):
        if self.time is None:
            self.time = time.monotonic() - self.start
        timer_string = f"[{begin_text}{f'%.{decimal_places}f'%(self.time)}{end_text}]"
        try:
            return timer_string if with_brackets else timer_string[1:-1]
        finally:
            self.time = None