import logging

class CustomLogger:
    def __init__(self, log_filename):
        self.log_filename = log_filename
        logging.basicConfig(filename=self.log_filename, level=logging.INFO, format='%(asctime)s - %(message)s')
    
    def log_info(self, message):
        logging.info(message)


class HTTPLog4AI:
    from datetime import datetime
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%Y-%m-%d")
    logger_caller = CustomLogger(f"{formatted_date}-http-ai-log.txt")
    
    @staticmethod
    def log(message):
        #print (message)
        HTTPLog4AI.logger_caller.log_info(message)

    @staticmethod
    def print_log(message):
        print (message)
        HTTPLog4AI.logger_caller.log_info(message)