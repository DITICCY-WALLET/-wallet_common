import abc
import atexit
import fcntl
import os
from log import logger_attr


@logger_attr
class ProcessLock(metaclass=abc.ABCMeta):

    def __init__(self, func, path='/var/tmp', filename='ProcessDefault.lock'):
        self.func = func
        self.filename = filename
        self.path = path
        self.fb = None

        self.__create_file()

    def __create_file(self):
        fn = os.path.join(self.path, self.filename)
        self.fb = open(fn, 'wb')
        self.logger.info("创建 {} 文件锁句柄成功".format(fn))

    def lock_run(self):
        self.safe_unlock()
        try:
            fcntl.flock(self.fb, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.func()
        except BlockingIOError as e:
            if e.args[0] == 35 or 'Resource temporarily unavailable' in e.args[1]:
                self.logger.warning("{} 文件锁已加, 无法多重入锁".format(self.func.__name__))
            else:
                self.logger.error("文件锁加锁失败, 原因: {}".format(e))
        except Exception as e:
            self.logger.error("文件锁加锁失败, 原因: {}".format(e))

    def unlock(self):
        if self.fb is not None:
            fcntl.flock(self.fb, fcntl.LOCK_UN)
            self.fb.close()
        self.fb = None

    def safe_unlock(self):
        """安全解锁, 使用 atexit 模块, 无论哪种无出, 都会将锁解开"""
        atexit.register(self.unlock)

    def register(self, func):
        self.func = func










