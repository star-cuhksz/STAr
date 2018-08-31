from datetime import datetime


class Log:
    def __init__(self, log_type=".log", log_data=[]):
        self.file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + log_type
        self.log_buffer = log_data
        self.log_add("Running Time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def log_add(self, content):
        with open(self.file_name, 'a') as file:
            file.write(str(content))
            file.write("\n\n")
        self.log_buffer = []

    def log_rewrite(self, content):
        with open(self.file_name, 'w') as file:
            file.write(str(content))
            file.write("\n\n")
        self.log_buffer = []
