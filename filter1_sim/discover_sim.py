import time
from collections import Counter
import pandas as pd
import numpy as np
from gensim.models import word2vec

class MetaDataSimilarity:
    def __init__(self, profile_path, comm_path, pred_path, w2v=''):
        print('-----MetaDataSimilarity init-----')
        # data
        self.profile_path = profile_path
        self.comm_path = comm_path
        # WordVec model
        self.W2VModel_path = 'E:/vscodePython/bigdata/model/w2v_p+c_v6.model' if w2v == '' else w2v
        # discovery result
        self.pred_path = pred_path
        # thresholds
        self.all_avg = 0.3
        self.sw_avg = 0.6
        self.hfw_avg = 0.3


    # func: load profile data
    def load_data_profile(self):
        data = pd.read_csv(self.profile_path)
        data['profile'] = data.apply(lambda row: [s for s in row['themes'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        return data[['appid','name','profile']]
    # func: load comm data
    def load_data_comm(self):
        data = pd.read_csv(self.comm_path)
        data['comm'] = data.apply(lambda row: [s for s in row['themes'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        return data[['appid','comm']]
    # method: load data and merge
    def load_data(self):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data", end='')
        profile = self.load_data_profile()
        print("\tprofile:"+str(len(profile)), end='')
        comm = self.load_data_comm()
        print("\tcomm:"+str(len(comm)), end='')
        self.data = pd.merge(profile, comm, on='appid')
        print("\tmerged data:"+str(len(self.data)))

    # func: word vectorization
    def get_vecs_w2v(self, words):
        # word: direct vectorization
        if type(words)==str:
            try:
                return self.w2v.wv[words]
            except Exception as e:
                return []
        # words list: sum and average
        vec = [0]*64
        length = 0
        for word in words:
            try:
                word_vec = self.w2v.wv[word]
                for i in range(64):
                    vec[i] += word_vec[i]
                length += 1
            except Exception as e:
                continue           
        if length > 0:
            vec = [vec[i]/length for i in range(64)]
            return vec
        else:
            return []
    # method: load the w2v model and vectorize the data
    def load_w2v(self):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Word2Vec Model '+self.W2VModel_path+"" )
        self.w2v = word2vec.Word2Vec.load(self.W2VModel_path)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Data2Vec " )
        def get_vecs(words):
            vecs = []
            if len(words) == 0:
                return []
            for (word,num) in Counter(words).most_common():
                vec = self.get_vecs_w2v(word)
                if len(vec) == 0:
                    continue
                vecs.append((word,vec,num/len(words)))
            return np.array(vecs)
        self.data['vecs_profile'] = self.data.apply(lambda row: get_vecs(row['profile']), axis=1)
        self.data['vecs_comm'] = self.data.apply(lambda row: get_vecs(row['comm']), axis=1)
        # remove nan
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove NaN", end='')
        print("\tlen:"+str(len(self.data)), end='->')
        self.data['has_NaN'] = self.data.apply(lambda row: len(row['vecs_profile'])==0 or len(row['vecs_comm'])==0, axis=1)
        removed = self.data[self.data['has_NaN']][['appid','name','profile','comm']]
        self.data = self.data.drop(self.data[self.data['has_NaN']].index)
        print(str(len(self.data)))
        if len(removed)>0: print(removed)
             
    # func: calculate cosine similarity (two vectors)
    def sim_cos_vecs(self, vec_profile, vec_comm):
        if len(vec_profile)==0 or len(vec_comm)==0 :
            return 0
        vec1 = np.array(vec_profile)
        vec2 = np.array(vec_comm)
        cos_sim = vec1.dot(vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return round(cos_sim,3)
    # func: calculate similarity (two vector lists)
    # avg
    def get_sim_avg(self, vecs_profile, vecs_comm):
        if len(vecs_profile)==0 or len(vecs_comm)==0:
            return -1
        sims = [self.sim_cos_vecs(profile[1],comm[1])*profile[2]*comm[2] for profile in vecs_profile for comm in vecs_comm]
        return sum(sims)
    # sw
    def get_sim_sw(self, vecs_profile, vecs_comm):
        if len(vecs_profile)==0 or len(vecs_comm)==0:
            return [(-1,1,'','')]
        spcs = [(self.sim_cos_vecs(profile[1],comm[1]),profile[2]*comm[2],profile[0],comm[0]) for profile in vecs_profile for comm in vecs_comm]
        spcs.sort(key=(lambda x:x[0]),reverse=True)
        return spcs[0:max(int(len(spcs)/10),10)]
    # hfw
    def get_sim_hfw(self, vecs_profile, vecs_comm):
        if len(vecs_profile)==0 or len(vecs_comm)==0:
            return [(-1,1,'','')]
        spcs = [(self.sim_cos_vecs(profile[1],comm[1]),profile[2]*comm[2],profile[0],comm[0]) for profile in vecs_profile[0:max(int(len(vecs_profile)/10),5)] for comm in vecs_comm[0:max(int(len(vecs_comm)/10),5)]]  
        return spcs

    # func: get score from the thresholds and similarity
    def get_score(self, sim, method):
        if method == 'all_avg':
            return round(sim-self.all_avg, 3)
        if method == 'sw_avg':
            return round(sim-self.sw_avg, 3)
        if method == 'hfw_avg': 
            return round(sim-self.hfw_avg, 3)
        return 0

    # method: calculating similarity
    def get_sim(self):
        # get similarity
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Similarity avg")
        self.data['all_sim'] = self.data.apply(lambda row: self.get_sim_avg(row['vecs_profile'], row['vecs_comm']), axis=1)
        self.data['all_score'] = self.data.apply(lambda row: self.get_score(row['all_sim'],'all_avg'),axis=1)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Similarity sw")
        self.data['spcs'] = self.data.apply(lambda row: self.get_sim_sw(row['vecs_profile'], row['vecs_comm']), axis=1)
        self.data['sw_sim'] = self.data.apply(lambda row: sum([sim*num for (sim,num,profile,comm) in row['spcs']])/sum([num for (sim,num,profile,comm) in row['spcs']]), axis=1)
        self.data['sw_score'] = self.data.apply(lambda row: self.get_score(row['sw_sim'],'sw_avg'),axis=1)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Similarity hfw")
        self.data['spcs'] = self.data.apply(lambda row: self.get_sim_hfw(row['vecs_profile'], row['vecs_comm']), axis=1)
        self.data['hfw_sim'] = self.data.apply(lambda row: sum([sim*num for (sim,num,profile,comm) in row['spcs']])/sum([num for (sim,num,profile,comm) in row['spcs']]), axis=1)
        self.data['hfw_score'] = self.data.apply(lambda row: self.get_score(row['hfw_sim'],'hfw_avg'),axis=1)
        # vote to get score
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Similarity vote")
        self.data['score'] = self.data.apply(lambda row: [row['all_score'], row['sw_score'], row['hfw_score']],axis=1)
        def vote(sim1,sim2,sim3):
            v1 = 1 if sim1 > 0 else -1
            v2 = 1 if sim2 > 0 else -1
            v3 = 1 if sim3 > 0 else -1
            return v1+v2+v3
        self.data['vote'] = self.data.apply(lambda row: vote(row['all_score'], row['sw_score'], row['hfw_score']),axis=1)
        self.data['score_sum'] = self.data.apply(lambda row: round(sum(row['score']),3),axis=1)
        self.data.sort_values(by=['score_sum'], axis=0, ascending=[True], inplace=True)
        # get label
        self.data['y_sim'] = self.data.apply(lambda row: 1 if row['score_sum']>0 else -1,axis=1)
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Save Result in "+self.pred_path)
        self.data[['y_sim','score_sum','vote','score','appid','name']].to_csv(self.pred_path, index=False)
