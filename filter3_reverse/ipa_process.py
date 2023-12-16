import os
import zipfile
import shutil

class ipaProcess:
    def __init__(self, ida, ipa_dir, machO_dir, i64_dir, BinExport_tmp_dir):
        # file dir
        self.ipa_dir = ipa_dir
        self.machO_dir = machO_dir
        self.i64_dir = i64_dir
        self.BinExport_tmp_dir = BinExport_tmp_dir
        # IDA Pro path
        self.ida = ida
        # idc script
        self.i64_idc_path = 'filter3_reverse/get_i64.idc'
        self.binExport_idc_path = 'filter3_reverse/get_binExport.idc'

    # func: extract mach-o from ipa file
    def extract_machO(self):
        for root, dirs, files in os.walk(self.ipa_dir):
            for f in files:
                if f.endswith('.ipa'):
                    ipa_name = str(root)+'/'+f
                    zip_name= str(root)+'/'+f+'.zip'
                    os.rename(ipa_name, zip_name)
                    f = f+'.zip'
                if f.endswith('.ipa.zip'):
                    zip_name = str(root)+'/'+f
                    ipa_name= str(root)+'/'+f[:-4]
                    unzip = zipfile.ZipFile(str(root)+'/'+f)
                    unzip_file_names = [file for file in unzip.namelist()]
                    machO_name = unzip_file_names[1].split('/')[1][:-4]
                    machO_path = unzip_file_names[1]+machO_name
                    unzip.extract(machO_path, self.machO_dir)
                    unzip.close()
                    row_macho = self.machO_dir+'/'+machO_path
                    new_macho = self.machO_dir+'/'+f.split('.')[0]+'_'+machO_path.split('/')[-1]
                    shutil.move(row_macho, new_macho)
                    os.rename(zip_name, ipa_name)
        shutil.rmtree(self.machO_dir+'/Payload')

    # func: get i64 file from mach-o file using IDA Pro
    def get_i64(self):
        for root, dirs, files in os.walk(self.machO_dir):
            for f in files:
                name = name.replace(' ', '')
                machO_path = self.machO_dir+'/'+name
                log_path = './log.txt'
                cmd = self.ida+' -A -S'+self.i64_idc_path+' -L'+log_path+' '+machO_path
                os.system(cmd)

    # func: get BinExport file from i64 file using IDA Pro
    def i642BinExport(self, i64_file):
        cmd = self.ida+' -S'+self.binExport_idc_path+' '+i64_file
        os.system(cmd)
        for root, dirs, files in os.walk(self.BinExport_tmp_dir):
            filenames = [f for f in files if f.endswith('.BinExport')]
        if len(filenames) == 0: return
        row_path = self.BinExport_tmp_dir+'/'+filenames[0]
        new_path = '.'.join(i64_file.split('.')[:-1])+'.BinExport'
        shutil.move(row_path, new_path)
    def i642BinExport_batch(self, i64_dir):
        for root, dirs, files in os.walk(i64_dir):
            BinExport_names = {'.'.join(f.split('.')[:-1])+'.i64' for f in files if f.endswith('.BinExport')}
            i64_names = {f for f in files if f.endswith('.i64')}
        i64_names = i64_names - BinExport_names
        for name in i64_names:
            self.i642BinExport(i64_dir+'/'+name)
