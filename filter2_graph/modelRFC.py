import time
import pandas as pd
import numpy as np
from gensim.models import word2vec
from sklearn.ensemble import RandomForestClassifier
import joblib

class RFC:
    def __init__(self, profile_path, label_path, W2VModel_path, rfc_path):
        print('-----RandomForestClassifier init-----')
        # data
        self.graph_profile_path = profile_path
        self.label_path = label_path
        self.data = None
        # Qord2Vec model
        self.W2VModel_path = W2VModel_path
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Word2Vec Model '+self.W2VModel_path)
        self.w2v = word2vec.Word2Vec.load(self.W2VModel_path)
        # Random Forest Classifier model
        self.rfc_path = rfc_path
        self.rfc = None
        # classes list
        self.classes = ['主题壁纸','便民服务','租房招聘','外卖购物','美食菜谱',
                        '生活服务','生活类工具','天气','出行打车','定位导航',
                        '地铁公交','购票旅行','外语学习','学习','报刊新闻',
                        '阅读','漫画','视频直播','音乐','社交',
                        '照片相机','设计绘画','音频编辑工具','育儿','医疗',
                        '运动健康','金融服务','借贷','记事记账','文档类工具',
                        '办公类工具','输入法','网络类工具','浏览器','设备管理工具',
                        '软件开发工具','棋牌','游戏','体育赛事']
        # keywords of classes
        self.name2keyword= {'主题壁纸': ['组件','壁纸','铃声','主题'],
                            '便民服务': ['查询','税','电信','移动','联通','营业厅','监管','政务','人社','市民','国家'],
                            '租房招聘': ['聘','找工作','求职','装修'],
                            '外卖购物': ['外卖','快送','快递','优鲜','电商','超市','购','商城','生鲜','买菜','商家','二手','收银','跑腿','点餐'],
                            '美食菜谱': ['菜谱','下厨','厨房','做饭'],
                            '生活服务': ['按摩','美妆','充电'],
                            '生活类工具': ['变声器','LED','抽签','决定','随机','计算器'],
                            '天气': ['天气','预报','温度计','潮汐','月相'],
                            '出行打车': ['打车','代驾','车主','司机','顺风车','etc'],
                            '定位导航': ['定位','导航','地图'],
                            '地铁公交': ['地铁','公交'],
                            '购票旅行': ['酒店','机票','火车票','航班','旅游','旅行','民宿','酒店'],
                            '外语学习': ['翻译','词典','英语','四六级','雅思','托福'],
                            '学习': ['考','学习','辅导','作业','学生','教育','题库'],
                            '报刊新闻': ['新闻','周刊','杂志','日报','早报','电子报','资讯'],
                            '阅读': ['阅读','小说','读书','电子书','听书','文学'],
                            '漫画': ['动漫','漫画','追漫'],
                            '视频直播': ['影视','tv','电影','直播','播放器','剧'],
                            '音乐': ['音乐','节奏','dj','钢琴','乐器','吉他','节拍','调音'],
                            '社交': ['社交','约会','交友','聊天','恋爱','相亲','社区'],
                            '照片相机': ['相机','拍照','自拍','图片处理','拼图','抠图'],
                            '设计绘画': ['海报','设计','绘画','绘图','插画','色卡'],
                            '音频编辑工具': ['剪辑','视频制作','视频转换','视频编辑','音频'],
                            '育儿': ['宝宝','孕','启蒙','育儿','儿歌','早教','儿童','起名'],
                            '医疗': ['医保','医院','医生','挂号','就诊'],
                            '运动健康': ['运动','跑步','减肥','体重','健身','瑜伽','睡眠'],
                            '金融服务': ['银行','中银','工银','证券','股票','投资','农商','建行','邮储','支付'],
                            '借贷': ['借钱','分期','贷款','借款'],
                            '记事记账': ['记账','存钱','账单','手账','提醒','记录','计划','日历','便签'],
                            '文档类工具': ['扫描','录音','转文字','二维码','截屏'],
                            '办公类工具': ['办公','会议','考勤','网盘','云盘','邮箱'],
                            '输入法': ['输入法'],
                            '网络类工具': ['抓包','wifi','加密','遥控器','加速器','VPN'],
                            '浏览器': ['浏览器'],
                            '设备管理工具': ['清理','同步','拦截','克隆','换机'],
                            '软件开发工具': ['代码','编程','编译','算法','shell','程序员'],
                            '棋牌': ['棋'],
                            '游戏': ['游戏','手游'],
                            '体育赛事': ['体育','足球','篮球','赛事']
                            }
        self.keyword2class = {keyword: class_ for class_ in self.name2keyword for keyword in self.name2keyword[class_]} 

    # func: get vectors using w2v
    def get_vecs_w2v(self, words):
        if type(words) == str:
            return self.w2v.wv[words]
        vecs = [0]*64
        count = 0
        for word in words:
            try:
                vec = self.w2v.wv[word]
                vecs = [vecs[i]+vec[i] for i in range(64)]
                count += 1
            except Exception as e:
                continue
        if count > 0:
            vecs = [vecs[i]/count for i in range(64)]
            return vecs
        else:
            return []

    # method: load profile data
    def load_data(self):
        # label files: manual category
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Data', end='')
        label = pd.read_csv(self.label_path)[['appid', 'class']]
        label['label'] = label.apply(lambda row: self.classes.index(row['class']) if row['class'] in self.classes else -1, axis=1)
        # connecting to data files
        self.data = pd.read_csv(self.graph_profile_path)
        self.data = pd.merge(self.data, label, on='appid', how='left')
        self.data['themes'] = self.data.apply(lambda row: [s for s in row['themes'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        print('\tlen: '+str(len(self.data)))
        # generate vectors
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Theme to Vec')
        self.data['vecs'] = self.data['themes'].apply(self.get_vecs_w2v)
        # remove the 0 vector
        self.data['len_vecs'] = self.data['vecs'].apply(len)
        print(self.data[self.data['len_vecs']==0])
        self.data = self.data[self.data['len_vecs']>0]
        print('\tlen: '+str(len(self.data)))

    # method: train rfc model
    def train(self):
        # Load data and vectorize
        self.load_data()
        # keep only labeled data and randomly disrupted top 80% to train
        train = self.data[self.data['label'] >= 0].sample(frac=0.8, replace=False)
        test = self.data.drop(train.index)
        x = np.array(train['vecs']).tolist()
        y = np.array(train['class']).tolist()
        # train model
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Bulding")
        self.rfc = RandomForestClassifier(max_features = 64, max_depth =32, min_samples_split = 5, min_samples_leaf = 5, oob_score=True)
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Trained")
        self.rfc.fit(x, y)
        # save model
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Saved in " + self.rfc_path)
        joblib.dump(self.rfc, self.rfc_path)
        # effects on the training set
        train['pred_class'] = self.rfc.predict(x)
        train['is_correct'] = train.apply(lambda row: row['class'] == row['pred_class'], axis=1)
        c = len(train[train['is_correct'] == True])
        print('Train acc: {}/{}={:.4f}'.format(c, len(train), c/len(train)))
        # effects on the test set
        x = np.array(test['vecs']).tolist()
        test['pred_class'] = self.rfc.predict(x)
        test['is_correct'] = test.apply(lambda row: row['class'] == row['pred_class'], axis=1)
        c = len(test[test['is_correct'] == True])
        print('Test acc: {}/{}={:.4f}'.format(c, len(test), c/len(test)))

    # func: load model
    def load(self):
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load RFC from " + self.rfc_path)
        rfc = joblib.load(self.rfc_path)
        return rfc
    
    # method: classification with the rfc model
    # profile_path: input; class_path: output
    def profile2class(self, profile_path, class_path, profile_matrix_path):
        # load and process data
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data from " + profile_path)
        data = pd.read_csv(profile_path)
        data['themes'] = data.apply(lambda row: [s for s in row['themes'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        print('\tlen: '+str(len(data)))
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Theme to Vec')
        data['vecs'] = data['themes'].apply(self.get_vecs_w2v)
        data['len_vecs'] = data['vecs'].apply(len)
        print(data[data['len_vecs']==0])
        data = data[data['len_vecs']>0]
        print('\tlen: '+str(len(data)))
        # load model
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load RFC from " + self.rfc_path)
        rfc_model = joblib.load(self.rfc_path)
        classes = list(rfc_model.classes_)
        # The probability matrix obtained from random forest classification
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Class from RFC")
        p = np.array(data['vecs']).tolist()
        prob_matrix_rfc = np.array(rfc_model.predict_proba(p))
        data['pred_rfc'] = [classes[index] for index in np.argmax(prob_matrix_rfc, axis=1)]
        # The probability matrix obtained from the genre
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get genre2class_prob from label file")
        genre2class_prob = {}
        from collections import Counter
        df = pd.read_csv('E:/vscodePython/R1_discover/label.csv')
        for genre in df['genre'].unique():
            if not type(genre)==str or genre=='unknown': continue
            count = 0
            df_g= df[df['genre']==genre]
            if len(df_g) < 3: continue
            genre2class_prob[genre] = [0] * len(classes)
            for (c, n) in Counter(df_g['class'].to_list()).most_common():
                if not type(c)==str or n<3: continue
                genre2class_prob[genre][classes.index(c)] = n
                count += n
            genre2class_prob[genre] = [p/count for p in genre2class_prob[genre]] if count > 0 else genre2class_prob[genre]
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Class from Genre")
        g = data['genre'].tolist()
        prob_matrix_genre = np.array([genre2class_prob[genre] if genre in genre2class_prob else [1/len(classes)]*len(classes) for genre in g])
        data['pred_genre'] = [classes[index] for index in np.argmax(prob_matrix_genre, axis=1)]
        # The probability matrix obtained from the keywords in the name
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Class from app name")
        prob_matrix_name = []
        keywords_matrix = []
        import re
        for name in data['name'].to_list():
            prob = [0] * len(classes)
            count = 0
            name = re.sub(r'[^\u4E00-\u9FA5]', '', name)
            keywords = []
            for keyword in self.keyword2class.keys():
                if keyword in name:
                    keywords.append(keyword)
                    prob[classes.index(self.keyword2class[keyword])] += 1
                    count += 1
            prob = [p/count for p in prob] if count > 0 else prob
            prob_matrix_name.append(prob)
            keywords_matrix.append(keywords)
        data['keywords'] = keywords_matrix
        prob_matrix_name = np.array(prob_matrix_name)
        data['pred_name'] = [classes[index] for index in np.argmax(prob_matrix_name, axis=1)]
        # The three matrices are weighted to get the final result
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Class Result")
        prob = 0.5*prob_matrix_rfc + 0.3*prob_matrix_genre + 0.2*prob_matrix_name
        def normalization(data):
            _range = np.max(data) - np.min(data)
            return (data - np.min(data)) / _range
        prob = [normalization(line) for line in prob] 
        data['pred_class'] = [classes[index] for index in np.argmax(prob, axis=1)]
        # save class
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Save in "+class_path)
        data[['pred_class','pred_rfc','pred_genre','pred_name','genre','appid','name', 'keywords']].to_csv(class_path, index=False) 
        # return matrix
        import torch
        data['prob'] = prob
        torch.save(data[['appid', 'name', 'prob']], profile_matrix_path)
        return data[['appid', 'name', 'prob']]
