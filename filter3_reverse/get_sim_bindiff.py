import os
import csv
import time

class Bindiff:
    def __init__(self, bindiff, susp_file_path, library_path, row_result_path):
        # file dir
        self.susp_binExport_dir = susp_file_path
        self.library_dir = library_path
        self.row_result_library_path = row_result_path
        # bindiff path
        self.bindiff = bindiff

    def get_sim_bindiff(self):
        for root, dirs, files in os.walk(self.susp_binExport_dir):
            susp_files = {f for f in files if f.endswith('.BinExport')}
        for root, dirs, files in os.walk(self.library_dir):
            library_files = {f for f in files if f.endswith('.BinExport')}
        for susp in susp_files:
            BinExport_susp = self.susp_binExport_dir+'/'+susp
            for sample in library_files:
                BinExport_library = self.library_dir+'/'+sample
                cmd = self.bindiff + " --output_dir="+self.susp_binExport_dir+" --output_format=log "+BinExport_susp+" "+BinExport_library
                os.system(cmd)
                result_path = self.susp_binExport_dir+'/'+'.'.join(susp.split('.')[:-1])+'_vs_'+'.'.join(sample.split('.')[:-1])+'.results'
                if not os.path.exists(result_path): continue
                with open(result_path, 'r') as f:
                    lines = f.readlines()
                    for i in range(len(lines)):
                        if lines[i].startswith('similarity: ') and lines[i+1].startswith('confidence: '):
                            sim = '%.3f' %float(lines[i].strip().split(': ')[1])
                            conf = '%.3f' %float(lines[i+1].strip().split(': ')[1])
                            break
                with open(self.row_result_library_path, 'a', encoding='utf-8', newline='') as f:
                    csv.writer(f).writerow([sim,conf,susp,sample])
                os.remove(result_path)


