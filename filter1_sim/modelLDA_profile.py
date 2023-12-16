import re
import time
import pandas as pd
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import ldamodel

class LDA_P:
    def __init__(self, num_topics, cut_profile_path, lda_model_path, dicpath, themewords_path):
        print('-----LDA-profile init-----')
        # data
        self.train_data = cut_profile_path
        self.data = None
        self.row_themewords_path = 'words/row_themewords.txt'
        self.themewords_path = themewords_path
        # model
        self.lda_path = lda_model_path
        self.dicpath = dicpath
        self.num_topics = num_topics
        self.lda = None
        self.dic = None
        # thresholds
        self.theme_throd = 0.005
        self.word_throd = 0.005

    # method: load data
    def load_data(self):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data")
        self.data = pd.read_csv(self.train_data)
        self.data['cut_profile'] = self.data.apply(lambda row: [s for s in row['cut_profile'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)

    # method: load LDA model
    def load_lda(self):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load LDA")
        self.lda = ldamodel.LdaModel.load(self.lda_path)
        self.dic = Dictionary.load(self.dicpath)

    # method: train LDA model
    def train(self, hasDic=False):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Train LDA")
        words = np.array(self.data['cut_profile']).tolist()
        # establish dictionary and corpus
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Dictionary")
        if hasDic:
            self.dic = Dictionary.load(self.dicpath)
        else:
            self.dic = Dictionary(words)
            self.dic.save(self.dicpath)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Corpus")
        corpus = [self.dic.doc2bow(text) for text in words]
        # train model
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Trained")
        self.lda = ldamodel.LdaModel(corpus=corpus, id2word=self.dic, num_topics=self.num_topics, passes=10)
        # save model
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Saved in "+self.lda_path+"")
        self.lda.save(self.lda_path)

    # method: using LDA to generate topic words list
    def get_theme_words_list(self, num_words):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Get Theme Words")
        themewords = [line.strip() for line in open(self.row_themewords_path, 'r', encoding='utf-8').readlines()]
        theme_words_set = set(themewords)
        for (theme, theme_words) in self.lda.print_topics(num_topics=self.num_topics, num_words=num_words):
            for (prob, word) in re.findall('([0-9\.]+)\*"([\u4e00-\u9fa5a-z0-9]+)"', theme_words):
                if float(prob) >= self.word_throd:
                    theme_words_set.add(word)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Saved in "+self.themewords_path)
        with open(self.themewords_path, 'w', encoding='utf-8') as f:
            for word in theme_words_set:
                f.write(word+'\n')

    # method: extract functionalities of descriptions using topic words list
    # datapath: input; themepath: output
    # cut → theme: 'appid','name','themes'
    def profile2theme(self, datapath, themepath):
        # load data
        self.data = pd.read_csv(datapath)
        self.data['cut_profile'] = self.data.apply(lambda row: [s for s in row['cut_profile'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        # extract functionalities
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Profile to Theme Words", end='')
        themewords = [line.strip() for line in open(self.themewords_path, 'r', encoding='utf-8').readlines()]
        self.data['themes'] = self.data.apply(lambda row: [word for word in row['cut_profile'] for themeword in themewords if themeword in word], axis=1)
        # remove nan
        print('\tlen: '+str(len(self.data)), end=' → ')
        self.data['themes_len'] = self.data['themes'].apply(len)
        removed = self.data[self.data['themes_len']==0]
        self.data = self.data[self.data['themes_len']>0]
        print(str(len(self.data)))
        if len(removed) > 0: print(removed)
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Saved Data in "+self.theme_path+"")
        self.data[['appid','name','genre','themes']].to_csv(themepath, index=False)
