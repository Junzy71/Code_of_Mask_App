import re
import time
import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import ldamodel

class LDA_C:
    def __init__(self, num_topics):
        print('-----LDA-comm init-----')
        # model
        self.num_topics = num_topics
        self.lda = None
        self.dic = None
        # thresholds
        self.theme_throd = 0.01
        self.word_throd = 0.005      

    # func: train LDA model
    def train(self, words):
        dic = Dictionary(words)
        corpus = [dic.doc2bow(text) for text in words]
        lda = ldamodel.LdaModel(corpus=corpus, id2word=dic, num_topics=self.num_topics, passes=10)
        return lda

    # func: using LDA to generate topic words list
    def get_theme_words_list(self, lda):
        theme_words_dic = {}
        for (theme, theme_words) in lda.print_topics(num_topics=self.num_topics, num_words=50):
            for (prob, word) in re.findall('([0-9\.]+)\*"([\u4e00-\u9fa5a-z0-9]+)"', theme_words):
                theme_words_dic[word] = theme_words_dic[word]+float(prob) if word in theme_words_dic else float(prob)
        theme_words = [word for word in theme_words_dic if theme_words_dic[word] > self.num_topics*self.word_throd] 
        return theme_words

    # method: train LDA models for each app's reviews and extract functionalities
    # cut_path: input; theme_path: output
    # cut → theme/themes: 'appid','themes'    
    def comm2themes_app(self, cut_path, theme_path):
        print("Comm to Theme Words with APP")
        # load data
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data")
        data = pd.read_csv(cut_path)
        data['cut_comm'] = data.apply(lambda row: [s for s in row['cut_comm'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        # training and extracting functionalities separately by apps
        data_theme = None
        appids = data['appid'].unique()
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Train LDA with each appid and Comms to Theme Words")
        count = 1
        for appid in appids:
            if count%(len(appids)/5) == 0 or count == len(appids):
                print('\t\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- "+str(count)+'('+str(count/(len(appids))*100)+"%%) Finished")
            count += 1
            df = data[data['appid'] == appid]
            lda = self.train(list(df['cut_comm']))
            theme_words_set = self.get_theme_words_list(lda)
            df['themes'] = df.apply(lambda row: [word for word in row['cut_comm'] for themeword in theme_words_set if themeword in word], axis=1)
            data_theme = pd.concat([data_theme, df], ignore_index=True)
            words = []
            for row in df.iterrows():
                words += row[1]['themes']
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Saved Data in "+theme_path+"")
        data_theme[['appid','themes']].to_csv(theme_path, index=False)                   