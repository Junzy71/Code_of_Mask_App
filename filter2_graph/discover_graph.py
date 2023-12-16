import numpy as np
import torch
import time

class GraphInconsistencies:
    def __init__(self, profile_matrix_path, comm_matrix_path, app2node_path, pred_path):
        self.profile_matrix_path = profile_matrix_path
        self.comm_matrix_path = comm_matrix_path
        self.app2node_path = app2node_path
        self.app2node = np.load(app2node_path, allow_pickle='TRUE').item()
        self.pred_path = pred_path

    # get category vector from description
    def get_profile_class(self):
        self.df_p = torch.load(self.profile_matrix_path)
        classes = [ '主题壁纸', '体育赛事', '便民服务', '借贷', '出行打车', '办公类工具', '医疗', '地铁公交', '外卖购物', '外语学习', 
                    '天气', '学习', '定位导航', '报刊新闻', '文档类工具', '棋牌', '浏览器', '游戏', '漫画', '照片相机', 
                    '生活服务', '生活类工具', '社交', '租房招聘', '网络类工具', '美食菜谱', '育儿', '视频直播', '记事记账', '设备管理工具', 
                    '设计绘画', '购票旅行', '软件开发工具', '输入法', '运动健康', '金融服务', '阅读', '音乐', '音频编辑工具']
        class2label = { '主题壁纸': 0,
                        '体育赛事': 1,
                        '育儿': 2,
                        '便民服务': 3, '生活服务': 3, '生活类工具': 3, '租房招聘': 3,
                        '外卖购物': 4,
                        '美食菜谱': 5,
                        '记事记账': 6,
                        '天气': 7,
                        '出行打车': 8, '地铁公交': 8, '定位导航': 8, '购票旅行': 8,
                        '医疗': 9,
                        '运动健康': 10,
                        '借贷': 11,
                        '金融服务': 12,
                        '社交': 13,
                        '视频直播': 14,
                        '音乐': 15, '音频编辑工具': 15,
                        '设计绘画': 16, '照片相机': 16, 
                        '漫画': 17,
                        '阅读': 18,
                        '报刊新闻': 19,
                        '学习': 20, '外语学习': 20, 
                        '游戏': 21, '棋牌': 21,
                        '文档类工具': 22, '输入法': 22,
                        '办公类工具': 23,
                        '设备管理工具': 24, '网络类工具': 24, '浏览器': 24, '软件开发工具': 24,
                        }
        def class39_25(prob_39):
            prob_25 = [0]*25
            for i in range(len(prob_39)):
                prob_25[class2label[classes[i]]] += prob_39[i]
            return prob_25
        self.df_p['prob'] = self.df_p['prob'].apply(class39_25)

    # get category vector from reviews
    def get_comm_class(self):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load GCN prob from comm')
        self.df_c = torch.load(self.comm_matrix_path)
        self.df_c['pred'] = self.df_c['matrix']

    # get label using category overlap
    def get_label(self, thred_p, thred_c):
        import pandas as pd
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Merge Data')
        df = pd.merge(self.df_p, self.df_c, on='appid', how='right')
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Top Class')
        classes = [ '主题壁纸', '体育赛事', '育儿', '便民服务-生活服务-生活类工具-租房招聘', '外卖购物', 
                    '美食菜谱', '记事记账', '天气', '出行打车-地铁公交-定位导航-购票旅行', '医疗',
                    '运动健康', '借贷', '金融服务', '社交', '视频直播',
                    '音乐-音频编辑工具', '设计绘画-照片相机', '漫画', '阅读', '报刊新闻', 
                    '学习-外语学习', '游戏-棋牌', '文档类工具-输入法', '办公类工具', '设备管理工具-网络类工具-浏览器-软件开发工具']
        def get_top_class(pred):
            return sorted([(classes[i], pred[i]) for i in range(len(pred))], key=lambda x:x[1], reverse=True)
        df['p2c'] = df['prob'].apply(get_top_class)
        df['c2c'] = df['pred'].apply(get_top_class)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Same Class')
        def is_same_top_n(p, c):
            p_top = set()
            p_top.add(p[0][0])
            for (class_, prob) in p:
                if len(p_top) == 5: break
                if prob > thred_p: p_top.add(class_)
            c_top = set()
            c_top.add(c[0][0])
            for (class_, prob) in c:
                if len(c_top) == 5: break
                if prob > thred_c: c_top.add(class_)
            same = p_top & c_top
            return same
        df['same_class'] = df.apply(lambda row: is_same_top_n(row['p2c'], row['c2c']), axis=1)
        df['same'] = df.apply(lambda row: len(row['same_class']), axis=1)
        df.sort_values(by=['same'], axis=0, ascending=[True], inplace=True)
        df[['appid', 'name', 'same_class', 'p2c', 'c2c']].to_csv(self.pred_path, index=False)



