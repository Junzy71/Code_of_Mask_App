import os
import time
from xpinyin import Pinyin

class ida2i64:
    def __init__(self):
        self.ida_path = 'D:/IDA_Pro_v7.6.210427/ida64.exe'
        self.i64_path = 'E:/vscodePython/bigdata/filter3_reverse/i64'
        self.machO_dir = 'E:/vscodePython/bigdata/filter3_reverse/machO'
        self.idc_path = 'E:/vscodePython/bigdata/filter3_reverse/ida2i64.idc'
        self.log_path = 'E:/vscodePython/bigdata/filter3_reverse/log.txt'
        self.p = Pinyin()

    # 函数：转为拼音
    def get_pinyin_name(self, name):
        row_name = name.split('_')
        row_name[1] = self.p.get_pinyin(row_name[1], tone_marks='numbers')
        pinyin_name = '_'.join(row_name)
        return pinyin_name

    # 函数：生成i64
    def get_i64(self):
        # 遍历获得所有i64文件名
        for root, dirs, files in os.walk(self.i64_path):
            visited_names_pinyin = [f for f in files if f.endswith('.i64')] # i64的名字已处理成拼音
        for root, dirs, files in os.walk(self.machO_dir):
            visited_names_pinyin += [f for f in files if f.endswith('.i64')] # i64的名字已处理成拼音
        # 遍历获得所有machO文件，去掉已处理成i64的
        names = set()
        visited_names = set()
        for root, dirs, files in os.walk(self.machO_dir):
            for f in files:
                if f.endswith('.i64'):
                    visited_names.add(f[:-4])
                else:
                    pinyin_name = self.get_pinyin_name(f)+'.i64'
                    if pinyin_name in visited_names_pinyin:
                        continue
                    names.add(f)
        names = names - visited_names
        # 顺次提取
        for name in names:
            name = name.replace(' ', '')
            machO_path = self.machO_dir+'/'+name
            log_path = './log.txt'
            # 使用命令行启动IDA并提取函数调用关系
            cmd = self.ida_path+' -A -S'+self.idc_path+' -L'+log_path+' '+machO_path
            # 输出
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+name)
            open(self.log_path, 'a').write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' '+name+'\n')
            os.system(cmd)
        # 文件名转换为拼音
        for root, dirs, files in os.walk(self.machO_dir):
            for f in files:
                if f.endswith('.i64'):
                    pinyin_name = self.get_pinyin_name(f)
                    os.rename(self.machO_dir+'/'+f, self.i64_path+'/'+pinyin_name)

if __name__ == '__main__':
    i = ida2i64()
    i.get_i64()