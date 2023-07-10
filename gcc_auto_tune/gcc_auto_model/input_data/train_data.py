#
# file: train_data.py
# function: generate train data set
#


from perf_config import perf_counter
from result_handle import result_handler
from PCA import pca_model 
import csv
import os


# 27 cBench test
cBench_list = [
    "automotive_bitcount",
    "automotive_qsort1",
    "automotive_susan_c",
    "automotive_susan_e",
    "automotive_susan_s",
    "bzip2d",
    "bzip2e",
    "consumer_jpeg_c",
    "consumer_jpeg_d",
    "consumer_lame",
    "consumer_tiff2bw",
    "consumer_tiff2rgba",
    "consumer_tiffdither",
    "consumer_tiffmedian",
    "network_dijkstra",
    "network_patricia",
    "office_rsynth",
    "office_stringsearch1",
    "security_blowfish_d",
    "security_blowfish_e",
    "security_rijndael_d",
    "security_rijndael_e",
    "security_sha",
    "telecom_adpcm_c",
    "telecom_adpcm_d",
    "telecom_CRC32",
    "telecom_gsm"
]


def run_cbench_script(counter) -> None:
    root_dir = os.getcwd()
    counter.get_root_dir(root_dir)
    for benchmark in cBench_list:
        run_path = "./benchmark/cBench/" + benchmark + "/src_work"
        os.chdir(run_path)
        print(os.getcwd())
        cmd = "./__run 1"
        counter.run_perf(cmd)
        os.chdir(root_dir)


def data2csv(vector) -> None:
    with open("train_data.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(vector)



counter = perf_counter()
handler = result_handler()
run_cbench_script(counter)
handler.get_vector(counter.cnt)
print(handler.vec)
data2csv(handler.vec)

