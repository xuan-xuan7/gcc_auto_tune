#
# file: perf_config.py
# function: initial a perf counter class
#


from collections import defaultdict
import subprocess
import os

class perf_counter():

    def __init__(self) -> None:
        self.perf_list = None
        self.events = None
        self.get_perf_list()
    
    # get event from perf list
    def get_event(self, perf_list_raw) -> None:
        event_list = ["Hardware event", "Software event", "Hardware cache event"]
        self.events = defaultdict(list)
        for line in perf_list_raw.decode('utf-8').splitlines():
            for event_type in event_list:
                if event_type in line:
                    line_list = list(filter(None, line.split(' ')))
                    self.events[event_type].append(line_list[0])
                    break
        # print(self.events)
    
    # get perf list
    def get_perf_list(self) -> None:
        perf_list_raw = subprocess.check_output(["perf", "list"])
        self.get_event(perf_list_raw)
    
    # make event contain sys and user 
    def event_extend(self) -> None:
        suffix = ":u"
        for key in self.events.keys():
            user_event = [event + suffix for event in self.events[key]]
            all_events = self.events[key] + user_event
            self.events[key] = ','.join(all_events)
       # print(self.events)


    def get_perf_cmd(self, run_cmd, key) -> list:
        file_name = key.replace(' ', '_')
        output_file = "./perf_results/" + file_name + ".data"
        cmd = ["sudo", "perf", "stat", "-o"]
        cmd.append(output_file)
        cmd.append("-e")
        cmd.append(self.events[key])
        cmd.extend(run_cmd)
        return cmd

    def run_hardware_event(self, run_cmd) -> None:
        cmd = self.get_perf_cmd(run_cmd, "Hardware event")
        subprocess.call(cmd)

    def run_hardware_cache_event(self, run_cmd) -> None:
        cmd = self.get_perf_cmd(run_cmd, "Hardware cache event")
        subprocess.call(cmd)

    def run_software_event(self, run_cmd) -> None:
        cmd = self.get_perf_cmd(run_cmd, "Software event")
        subprocess.call(cmd)


    # run this perf counter by input command
    def run_perf(self, cmd) -> None:
        self.event_extend()
        run_cmd = cmd.split(' ')
        self.run_hardware_event(run_cmd)
        print("********** hardware event finish! **********")
        self.run_hardware_cache_event(run_cmd)
        print("********** hardware cache event finish! **********")
        self.run_software_event(run_cmd)
        print("********** software event finish! **********")
        print("************* perf counter run finish!*************")


if __name__ == "__main__":
    test = perf_counter()
    test.run_perf("/home/loongson/benchmark/stream/stream")
