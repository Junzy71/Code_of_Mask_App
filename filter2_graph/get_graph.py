import pandas as pd
import numpy as np
import time

class GraphBuilding:
    def __init__(self, class_path, edges_path, app2node_dic_path, src2dst_dic_path):
        self.class_profile_path = class_path
        self.edges_path = edges_path
        self.app2node_path = app2node_dic_path
        self.src2dst_path = src2dst_dic_path

    # func: constructing a node dictionary and an edge dictionary
    def get_node_and_edge(self):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Graph')
        # Node: all apps with descriptions
        appids = set(pd.read_csv(self.class_profile_path)['appid'].to_list())
        app2node ={}
        node_index = 0
        src2dst = {}
        # extract edges and convert nodes to indexes
        with open(self.edges_path, 'r', encoding='utf-8') as f:
            f.readline()
            for line in f.readlines():
                [src, dsts] = line.strip().replace('"','').split(',[')
                if not int(src) in appids:
                    continue
                dsts = dsts[1:-2].split('\', \'')
                dsts = {dst for dst in dsts if int(dst) in appids}
                if len(dsts) == 0:
                    continue
                if not src in app2node:
                    app2node[src] = node_index
                    node_index += 1
                if not src in src2dst:
                    src2dst[src] = []
                for dst in dsts:
                    if not dst in app2node:
                        app2node[dst] = node_index
                        node_index += 1
                    src2dst[src].append(dst)
        # 存储字典
        np.save(self.app2node_path, app2node)
        np.save(self.src2dst_path, src2dst)
