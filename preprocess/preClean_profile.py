import re
import time
import pandas as pd

class DataPreprocessorProfile:
    def __init__(self, row, cut, clean):
        self.reservedword_path = 'words/reserved.txt'
        self.cn_stopword_path = 'words/stopwords.txt'
        self.stopword_path = 'words/stopwords_profile.txt'
        self.row_datapath = row
        self.cut_datapath = cut
        self.clean_datapath = clean

    # func: initial cleanup and division of sentences
    def cutSent(self, s):
        if not type(s) == str or len(s) == 0:
            return []
        # lower
        s = s.lower()
        # remove the URL
        s = re.sub('https?://[\w\./:]*', '', s)
        # remove the mail
        s = re.sub('[\w]+@[\w]+\.com', '', s)
        # punctuation to full angle
        s = s.strip().replace('\\', '').replace('\n', '。').replace(',', '，').replace(':', '：').replace(';', '；')
        s = s.strip().replace('<', '《').replace('>', '》').replace('[', '【').replace(']', '】')
        s = s.strip().replace('!', '！').replace('?', '？').replace('"', '“').replace("'", '‘').strip()
        s = re.sub('-{3,}', '', s)
        # remove special characters
        s = re.sub(r'[^a-zA-Z0-9\u4E00-\u9FA5\.，。、：；【】、《》！？“”——·~（）/\-]', '', s)
        # convert spaces between Chinese characters to commas
        def isChinese(char):
            return True if char >= u'/u4E00' and char<=u'/u9FA5' else False            
        for i in range(len(s)):
            if s[i] == ' ':
                if isChinese(s[i-1]) and isChinese(s[i+1]):
                    s[i] = '，'                
        # Sentences divided
        sents = re.split('[，。！？~】：；•]', s.strip())
        sent_list = []
        for sent in sents:
            serials = re.findall('([0-9a-z][\.]|[0-9]、)+[^0-9a-z]', sent)
            if not len(serials) == 0:
                for serial in serials:
                    sent = sent.split(serial, 1)
                    sent_list.append(sent[0])
                    sent = sent[1]
            if sent == '': continue
            sent_list.append(sent)
        return sent_list

    # method: file level cleanup
    # row → row: 'appid','name','genre','profile'
    def clean_file(self):
        print("profile_clean_file: row → row")
        # read data
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data", end='')
        df = pd.read_csv(self.row_datapath)
        print("\tlen:"+str(len(df)))
        # remove nan
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove NaN", end='')
        removed = df[df.isna().any(axis=1)][['appid','name','profile']]
        df = df.dropna(axis=0)
        print("\tlen:"+str(len(df)))
        if len(removed) > 0: print(removed)
        # remove duplicates
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove Duplicates", end='')
        df.drop_duplicates('appid', inplace = True)
        print("\tlen:"+str(len(df)))
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Save Data in "+str(self.row_datapath)+"")
        df[['appid','name','genre','profile']].to_csv(self.row_datapath, index=False)

    # method: content level cleanup
    # row → clean: 'appid','name','genre','profile'
    def clean_content(self):   
        print("profile_clean_content: row → clean")
        # read data
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data", end='')
        df = pd.read_csv(self.row_datapath)
        df_old = pd.read_csv(self.clean_datapath)
        processed_appid = {appid for appid in df_old['appid'].to_list()}
        print("\tlen:"+str(len(df)))
        # Clause cleanup, regular filtering
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Sentence Clean with re", end='')
        re_contact = '用户评价|(联系|加入)(我们|方式|合作)|(欢迎|请|与我们)(联系|交流)|联系方式'
        re_update = '(本次|近期|持续)更新|更新内容|敬请期待'
        re_feedback =  '反馈|获取更多内容|意见|建议|应用市场|专题推荐|获取.*信息'
        re_serve = '包[月季年]|元[0-9]{1,2}[月季年]|订阅|续订|退订|[付扣][款费]|会员回馈|(隐私|用户|服务|使用|包月|会员|许可|注册)(协议|政策|条款|策略|条件|时间)'
        re_platform = '合作电话|官方网站|官方账号|官网|客服|热线|邮箱：|电子邮件|发邮件|公众号|微信：|公众平台|生活号|服务号|视频号|微博：|qq：|qq群'
        re_only = '^(电话|联系|邮件|微博|邮箱|微信|qq)$|^.*获.*奖.*$|^.*荣获.*$'
        re_ = re_contact+'|'+re_update+'|'+re_feedback+'|'+re_serve+'|'+re_platform+'|'+re_only
        def reFilter(sent_list):
            # Remove blank sentences, clauses, spaces, punctuation, etc.
            s = ''
            for sent in sent_list:
                sent = re.sub('[^\u4E00-\u9FA50-9a-z]', '', sent)
                if len(re.sub('[^\u4E00-\u9FA5]', '', sent)) == 0:
                    continue
                if len(re.findall(re_, sent)) > 0:
                    continue
                s = s+sent+'。'
            return s
        def aaa(appid, name, profile):
            if appid in processed_appid:
                return ''
            name_list = self.cutSent(name)
            profile_list = self.cutSent(profile)
            s = reFilter(name_list + profile_list)
            return s
        df['profile'] = df.apply(lambda row: aaa(row['appid'], row['name'], row['profile']), axis=1)  
        df = pd.concat([df_old, df])
        df.drop_duplicates('appid', keep='first', inplace = True)
        print("\tlen:"+str(len(df)))     
        # remove nan
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove NaN", end='')
        df['len'] = df.apply(lambda row: len(row['profile']), axis=1)
        removed = df[df['len'] == 0][['appid','name']]
        df = df.drop(df[df['len'] == 0].index)
        print("\tlen:"+str(len(df)))     
        if len(removed) > 0: print(removed)               
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Save Data in "+str(self.clean_datapath)+"")
        df[['appid','name','genre','profile']].to_csv(self.clean_datapath, index=False)

    # method: Segmentation, filtering of stopwords
    # clean → cut: 'appid','name','genre','cut_profile'
    def cut(self):
        import jieba as jb
        import jieba.posseg as psg
        print("profile_cut: clean → cut")
        # read data
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data", end='')
        df = pd.read_csv(self.clean_datapath)
        print("\tlen:"+str(len(df)))
        # load stopwords
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Stopwords")
        stopwords = [line.strip() for line in open(self.cn_stopword_path, 'r', encoding='utf-8').readlines()] + [line.strip() for line in open(self.stopword_path, 'r', encoding='utf-8').readlines()]
        # add reserved words for jieba
        with open(self.reservedword_path, 'r', encoding='utf-8') as f:
            words = f.readlines()
            for word in words:
                word = word.strip().split(' ')[0]
                jb.add_word(word)
        # segmentation, filtering of stopwords
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove Stopwords")
        def cut_profile(s):
            words = []
            for w in list(jb.cut(s)):
                if w not in stopwords and len(w)<6:
                    words.append(w)
            return words
        df['cut_profile'] = df['profile'].apply(cut_profile)
        # remove nan
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove App without Profile", end='')
        df['len'] = df.apply(lambda row: len(row['cut_profile']), axis=1)
        removed = df[df['len'] == 0][['appid','name','cut_profile']]
        df = df.drop(df[df['len'] == 0].index)
        print("\tlen:"+str(len(df)))
        if len(removed) > 0: print(removed)
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Saved Data in "+self.cut_datapath+"")
        df[['appid','name','genre','cut_profile']].to_csv(self.cut_datapath, index=False)
