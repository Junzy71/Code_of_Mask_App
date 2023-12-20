import csv
import time
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

class RFC:
    def __init__(self,row_result_path, rfc_input_path, rfc_model):
        print('-----RandomForestClassifier init-----')
        self.row_result_path = row_result_path
        self.rfc_input_path = rfc_input_path
        self.rfc_model = rfc_model

    def process_data(self):
        with open(self.rfc_input_path, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['label','app','sims'])
            df = pd.read_csv(self.row_result_path)
            app_names = df['susp'].unique()
            for app_name in app_names:
                data = df[df['susp'] == app_name]
                sims = [float(sim) for sim in data['sim'].to_list()]
                if app_name.split('_')[0] == '0': label = 0
                else: label = 1
                w.writerow([label,app_name, sims])
    
    def load_data(self):
        self.data = pd.read_csv(self.rfc_input_path)
        self.data['sims'] = self.data.apply(lambda row: [float(sim) for sim in row['sims'][1:-1].split(', ')], axis=1)

    def train(self):
        self.load_data()
        from sklearn.model_selection import train_test_split
        train, test = train_test_split(self.data, train_size=0.6, stratify=self.data['label'])
        x = np.array(train['sims']).tolist()
        y = np.array(train['label']).tolist()
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Bulding")
        self.rfc = RandomForestClassifier(max_features = 23, max_depth =64, min_samples_split = 2, min_samples_leaf = 1, oob_score=True)
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Trained")
        self.rfc.fit(x, y)
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Model Saved in " + self.rfc_model)
        joblib.dump(self.rfc, self.rfc_model)
        # effects on the training set
        train['pred'] = self.rfc.predict(x)
        train['is_correct'] = train.apply(lambda row: row['label'] == row['pred'], axis=1)
        c = len(train[train['is_correct'] == True])
        print('Train acc: {}/{}={:.4f}'.format(c, len(train), c/len(train)))
        # effects on the test set
        x = np.array(test['sims']).tolist()
        test['pred'] = self.rfc.predict(x)
        test['is_correct'] = test.apply(lambda row: row['label'] == row['pred'], axis=1)
        c = len(test[test['is_correct'] == True])
        print('Test acc: {}/{}={:.4f}'.format(c, len(test), c/len(test)))

    def load(self):
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load RFC from " + self.rfc_model)
        rfc = joblib.load(self.rfc_model)
        return rfc
    
    def get_label(self, input_file, result_file):
        df = pd.read_csv(input_file)
        app_names = df['susp'].unique()
        vecs = []
        for app_name in app_names:
            data = df[df['susp'] == app_name]
            sims = [float(sim) for sim in data['sim'].to_list()]
            vecs.append(sims)
        self.load()        
        labels = self.rfc.predict(vecs)
        data = {'app':app_names,'label':labels}
        df = pd.DataFrame(data)
        df.to_csv(result_file, index=False)
