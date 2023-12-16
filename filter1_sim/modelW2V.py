import re
import time
import pandas as pd
import numpy as np
from gensim.models import word2vec

class Word2Vec:
    def __init__(self, type):
        print('-----Word2Vec init-----')
        # type：row、clean、cut、theme
        self.type = type
        self.reservedword_path = 'words/reserved.txt'

    # func: get corpus
    def get_words(self, data_path, data_name):
        df = pd.read_csv(data_path)
        # type row/clean: segment
        # type cut/theme: convert to list
        if self.type == 'row' or self.type == "clean":
           import jieba as jb
           with open(self.reservedword_path, 'r', encoding='utf-8') as f:
            words = f.readlines()
            for word in words:
                word = word.strip().split(' ')[0]
                jb.add_word(word)
            def cut(s):
                if not type(s) == str or len(s) == 0:
                    return []
                words = []
                for word in jb.cut(s):
                    if len(re.sub('[^a-z0-9\u4E00-\u9FA5]','',word)) == 0:
                        continue
                    words.append(word)
                return words
            # tyoe row: merge the two columns first
            if self.type == 'row':
                if data_name == 'comm':
                    df[data_name] = df["title"] + "。" + df["content"]
                if data_name == 'profile':
                    df[data_name] = df["name"] + "。" + df["profile"]
            df['words'] = df[data_name].apply(cut)
            df['len'] = df.apply(lambda row: len(row['words']), axis=1)
            df = df.drop(df[df['len'] == 0].index)
        else:
            df['words'] = df.apply(lambda row: [s for s in row[data_name][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
        return np.array(df['words']).tolist()

    # func: train and save
    def train(self, words_paths, W2VModel_path):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Data')
        words = []
        for (data_path, data_name) in words_paths:
            words += self.get_words(data_path, data_name)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Train Model')
        model = word2vec.Word2Vec(words, vector_size=64, sg=1, window=5, min_count=3, negative=3, sample=0.001, hs=1, workers=4)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Save Model')
        model.save(W2VModel_path)

    # func: incremental train and save
    def train(self, words_paths, W2VModel_old_path, W2VModel_new_path):
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Data')
        words = []
        for (data_path, data_name) in words_paths:
            words += self.get_words(data_path, data_name)
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Train Add Model')
        model = word2vec.Word2Vec.load(W2VModel_old_path)
        model.build_vocab(words, update=True)
        model.train(words, 
                    epochs=model.epochs,
                    total_examples=model.corpus_count
                    )
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Save Model')
        model.save(W2VModel_new_path)
    
    # method: load model
    def load(self, W2VModel_path):      
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Word2vec')
        w2v = word2vec.Word2Vec.load(W2VModel_path)
        return w2v
    
    # method: vectorized word
    def get_vec(self, word, w2v=None):
        if w2v == None:
            w2v = self.load()
        return w2v[word]
