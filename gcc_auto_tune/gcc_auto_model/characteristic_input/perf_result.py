#
# file: perf_result.py
# function: read and handle perf result data 
#


import re
import numpy as np
from perf_config import perf_counter


class result_handler():
    
    def __init__(self) -> None:
        self.hardware_event_data = None
        self.software_event_data = None
        self.hardware_cache_event_data = None
        self.result_path = "./perf_results/"
        self.events = ["Hardeware_event", "Software_event", "Hardware_cache_event"]
        self.pattern = r' +([0-9,]+) +[A-Za-z:\-]+.+[\(\d+\.\d+\%\)]* *'
        self.raw_vec = None
        self.vec = None

    def get_file_path(self, event) -> str:
        file_path = self.result_path + event + ".data"
        return file_path

    def get_event_data(self, key) -> list:
        file_path = self.get_file_path(key)
        with open(file_path, 'r') as fd:
            content = fd.read()
            matches = re.findall(self.pattern, content)
            raw_data = map(lambda x: int(x.replace(',', '')), matches)
            return list(raw_data)

    def get_raw_data(self) -> list:
        self.hardware_event_data = self.get_event_data("Hardware_event")
        self.software_event_data = self.get_event_data("Software_event")
        self.hardware_cache_event_data = self.get_event_data("Hardware_cache_event")
        self.raw_vec = self.hardware_event_data + self.software_event_data + self.hardware_cache_event_data
        # print(self.raw_vec)
        return self.raw_vec
    
    def vec_normalized(self) -> None:
        raw_vec = np.array(self.raw_vec)
        self.vec.append((raw_vec - np.mean(raw_vec, axis=0)) / np.std(raw_vec, axis=0))

    def get_vector(self) -> None:
        self.get_raw_data()
        self.vec_normalized()


if __name__ == "__main__":
    counter = perf_counter()
    for i in range(2):
        counter.run_perf("/home/lslab/cpu2006-v1.1/run.sh")
        handler = result_handler()
        handler.get_vector()
    print(handler.vec)


