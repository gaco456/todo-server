import logging
import logging.handlers
import datetime
from pathlib import Path

# devlope mode 일시만 ... -> after deploy env add Sys argv
logDir = '../logs'
logFile_max_bytes = 10 * 1024 * 1024

class LogAgent():
    # 차후 기능 강화. code argv 추가.
    def __init__(self , loggerName , LogToFile = True , LogToStream = True):

        defalutFomatter = logging.Formatter('[%(asctime)s | LV:%(levelname)s | %(filename)s:%(lineno)s ] %(message)s')

        self.logger = logging.getLogger(loggerName)
        self.logger.setLevel(logging.DEBUG)

        if LogToFile:

            logFilePath = logDir + "/" +loggerName +".log"

            logFile = Path(logFilePath)
            if logFile.is_file() and logFile.exists():
                pass
            else:
                file = open(logFilePath, 'w')
                file.close()
                pass


            # logFileHandler = logging.FileHandler(logFilePath) <-- if u want no limit log file bytes .. use this .
            # limit 200mb log files on devide 20 pis to log
            logFileHandler = logging.handlers.RotatingFileHandler(filename=logFilePath , maxBytes=logFile_max_bytes , backupCount= 20)
            logFileHandler.setFormatter(defalutFomatter)

            self.logger.addHandler(logFileHandler)
            self.logger.debug("----------------------------------------------------")
            self.logger.debug(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        if LogToStream:
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(defalutFomatter)
            self.logger.addHandler(streamHandler)

    def get_logger(self):
        return self.logger