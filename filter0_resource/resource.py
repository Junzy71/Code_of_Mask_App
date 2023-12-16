import re
import pandas as pd

class labelResource:
    def __init__(self, comm, info, result):
        self.comm_datapath = comm
        self.profile_datapath = info
        self.result = result
        re1 = '资源|追.?剧|追动?漫|看电[视影]|看视频|免费|'+'跳转|变身|变不了身|解锁|隐藏|口令|暗号|懂的都懂|低[分星]保护|保护'
        re2 = '资源|剧|动?漫|电[视影]|视频|歌|音乐|小说|阅读'
        self.pattern = re.compile(re1)
        self.pattern2 = re.compile(re2)

    def hasResource(self, s):
        if not type(s) == str: return 0
        result = self.pattern.findall(s)
        return len(set(result))
    
    def isResource(self, s):
        if not type(s) == str: return 0
        result = self.pattern2.findall(s)
        return len(set(result))

    def label(self):
        comm = pd.read_csv(self.comm_datapath)
        genre_dic = {}
        def appid2profile(appid, profile):
            genre_dic[appid] = profile
        pd.read_csv(self.profile_datapath).apply(lambda row: appid2profile(row['appid'], str(row['name'])+str(row['profile'])), axis=1)
        appids = comm['appid'].unique()
        dic = {}
        count = 0
        for appid in appids:
            if appid in genre_dic and self.isResource(genre_dic[appid]) < 2: continue
            count += 1
            df = comm[comm['appid'] == appid]
            df['isResource'] = df.apply(lambda comm: self.hasResource(comm['title'])+self.hasResource(comm['content']), axis=1)
            sum_ = sum(df['isResource'].to_list())
            if sum_/len(df) > 0.3 or sum_ > 90:
                dic[appid] = (sum_, round(sum_/len(df), 2))
        print(len(dic), end='/')
        print(count, end=' -> ')
        print(round(len(dic)/count, 2))
        with open(self.result, 'w', encoding='utf-8') as f:
            f.write('appid,sum,rate\n')
            for appid in dic:
                f.write(str(appid)+','+str(dic[appid][0])+','+str(dic[appid][1])+'\n')
        r = pd.read_csv(self.result)
        r = r.sort_values(['sum', 'rate'], ascending=[False, False])
        r.to_csv(self.result, index=False)
