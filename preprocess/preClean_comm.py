import re
import csv
import time
import pandas as pd

class DataPreprocessorComm:
    def __init__(self, row, cut, clean, cuts, cleans):
        self.reservedword_path = 'words/reserved.txt'
        self.cn_stopword_path = 'words/stopwords.txt'
        self.stopword_path = 'words/stopwords_comm.txt'
        self.row_datapath = row
        self.cut_datapath = cut
        self.clean_datapath = clean
        self.cuts_datapath = cuts
        self.cleans_datapath = cleans
        re_noInfo_0 = '[^\u4E00-\u9FA5]'
        re_noInfo_1 = '[很挺不还太大无真针超蛮没有快特只纯多少越爆最全较'+'别慎给能求来去望请使说'+'好行赞棒牛爱可夸强绝谢謝推荐酷高爽'+'错差烂烦卸删难坑死病搞假孬害破中'+'评论用试说做过会买'+'啊阿吖嗯恩哦呵哈呀吗吧哇呢嗨嘛咳呜吼哼唧嗷哎哟哒呃呼嘻嘿啦呸啥额的得了么之矣然所而个款些'+'也才都在要来后已被但完'+'零一二三四五六七八九十几两俩'+'谁你我他她它们这样里那哪咋如此该人就'+'超很太大小真巨最特有无别慎如还不都远挺多少越老总蛮爆极就先共更全新旧'+'好推荐喜欢棒点赞完佳秀乐趣牛爽值对满意行可爱笑亲强绝逗顶'+'差错垃圾恶心郁闷烂缺错錯害气死坑怕瞎废渣土烦没慢贱愤傻乱丢难滚赖凑败亏嫌破虚假累伤心疯'+'中'+'评论价语感恩支持劝请祝改推卸问望求吐槽惜删弃下谢謝般拜托託做冲罢能用办需要找想试干待给凑比会'+'各种款段颗星分个次些久日月年句元'+'哈呵啊阿呀呼嗯呐嘻嘿啦吗嘎吧哪哇哦呢嗨嘛啥哟咳吼呜哼唧呃嗷哎呦呗哒嘤咋'+'零一二两俩三仨四五六七八九十百千万第几为怎什么之人入了子儿也又以在已其何矣然到所而的地得着这那哪你您我他她它咱们是来去再等被'+'今昨前明后天]'
        re_noInfo_1 = '['+''.join(set(re_noInfo_1[1:-1]))+']'
        re_noInfo_2 = '非常|特别|可以|超级|至极|[墙强][烈裂力]|[极大]力|从不|千万|必须|绝对|所有|真[的心]|根本|更多|确实|直接|经常|整体|狂魔|唯一'+'|还行|[阔可]以|一般|.星'+'|牛[逼皮批掰比]|厉害|精彩|完美|完善|开心|优秀|良心|免费|喜欢|满意|宝藏|有趣|好用|耐用|给力|无敌|靠谱|值得|[奶奈][思斯]|.好'+'|垃圾|辣鸡|乐色|差劲|糟糕|头疼|服了|佛了|忍了|投诉|救命|快跑|无聊|问题|可惜|恼火|恶心|生气|气死|严重|失望|遗憾|缺点|无语|搞毛|咋地'+'|发现|希望|需要|要求|告诉|回复|点赞|加油|信赖|期待|鼓励|支持|保持|吸引|感[谢恩]|麻烦|犹豫|求求|溜了|再见|举报|拒绝|下载|使用|拥有|改进|修复|感觉|体验|分享|建议|晓得|体[验会]|[平评][分论价]|拜[拜托託]'+'|软件|产品|应用|平台|内容|功能|玩意|套路|意思|大家|东西|自己|[无如]题|[比例]如|.分'+'|什么|怎么|其实|虽然|但是|总之|最后'+'|回事|再也|以后|中的|个字|阵子|以上|已经|总体|来讲|继续|懂[得的]|都懂|现在|有待|里面|不.|.是|一.'+'|简直|特别|[非灰]常|十分|[超炒][级鸡]|爆炸|根本|相对|经常|严重|[总整]体|顺便|比较|尽快|其余|直接|早日|相当|的确|果断|完全|确实|实在|必须|极力|强烈|墙裂|谨慎|一直|至极'+'|依旧|但是|同时|如果|已经|首先|另外|目前|现在|之前|既然|而且|当然'+'|一般|给力|[奶奈][思斯]|成功|值得|信赖|优秀|理解|厉害|良心|表扬|开心|完美|简单|好样|靠谱|手软|神器|宝藏|力荐|安利|牛[皮批逼掰马]'+'|[垃辣腊拉][圾鸡]|[沙傻][x瓜子鸟雕叼币逼比鼻避痹批杯闭狗勾沟]?|乐色|失望|弱智|晦气|有病|麻烦|退[钱款]|卸载|举报|删除|期待|救命|没有|告辞|服了|西内|栓|无语|坑爹|废物|无奈|差劲|失败|鸡肋|难用|后悔|讨厌|浪费|劝退|再见|无耻|难受|醉了|哭了|有毒|生气|坑货|意见|算了|避雷|离谱|问题|疑问|解决|别买|[我卧][草槽擦]|拉胯|糟糕|去死|倒闭'+'|觉得|感觉|解释|建议|使用|投诉|求助|申诉|反馈|采纳|申请|加油|[如同][标主]?题|希望|改进|拥有|努力|打开|知道|小心|要钱|大家|家人|注意|赶[快紧]|无法|标题'+'|套路|软件|版本|更新|升级|下载|修复|安装|下架|客服|结果|平台|应用|产品|公司|东西|玩意|时间|服务|态度|实话|免费|用户|体验'+'|不了|以及|想给|已经|继续|阿巴|关于|神马|[^小]说|[外为歪y]?瑞|古德|不止|没法|个字|字数|回事|无门|早点|我去|真实|及时|坚持|没谁|一批'
        re_noInfo_2 = '|'.join(set(re_noInfo_2.split('|')))
        re_noInfo_3 = '第.次|一般般|有意思|写评论|试试看|为什么|对不起|受不了|什么鬼|一句话|不知道|不解释|越来越|性价比|球球[了啦你您]|[给点]个赞|总的来说|什么情况|.来.去|说句?实话|一.接一.|垃圾中的战斗机'+'|越.越.|凭什么|搞什么|什么鬼|就是说|[没有]意思|没毛病|没办法|试试看|搞不懂|不要买|不要脸|[针真]不戳|死[我人]了|开发者|开玩笑|一生黑|没[话法]说|整明白|奥利给|.{0,2}[如同][上下].{0,2}|.起来|求解[决答]?'+'|美中|不足|莫名|其妙|持续|优化|取消|订阅|除此|之外|什么情况|变本加厉|再接再厉|滚出中国|什么意思|不好意思|什么原因|不吐不快|一目了然|乱七八糟|花里胡哨|一如既往|真的会谢|应有尽有'+'|开什么玩笑|[想缺]?.{0,2}[想缺]?疯了|吃相.{0,3}难看|提.{0,3}建议|红红火火恍恍惚惚|谁用谁知道|朋友推荐|给朋友|重要的事情说三遍|中华人民大团结|中的战斗机|谁用谁.{0,2}'
        re_noInfo_3 = '|'.join(set(re_noInfo_3.split('|')))
        re_noInfo_4 = '^.*(浪费|上当|卸载|退[款钱订]|推荐[的给]).*$'
        re_noInfo_5 = '^.*(吃相.*难看).*$'
        re_other_1 = '[欺骗诈胡乱扣收续付人费钱款]'
        re_other_2 = '原来|强制|自动|恶意|无法|虚假|霸王|无良|黑心|疯狂|频繁|泄露|诱导|浪费'+'|闪退|广告|流氓|黑屏|白屏|上当|崩溃|骚扰|消费|隐私|封号'+'|登[陆录]|注册|宣传|条款|商家|加载|功能|'+'强制|乱|自动|恶意|诱导|[收扣浪消续付圈][费钱款]|流氓|水军|闪退|广告|[骗骟坑][子纸人钱]|[诈欺][诈骗]|骗|公司|下载|下|无法|注册|登[录陆]|骚扰.{1,2}|'+'界面|画面|服务|更新|提示|页面|画质'+'|方便|简[洁单]|大方|实用|美观|贴心|干净|丰富|细致|强大|齐全|全面|单一|快捷|精美|适配|靠谱'
        re_other_2 = '|'.join(set(re_other_2.split('|')))
        re_other_3 = '(.都)?(.不[开去掉]|.不上去?|不出来)'+'|消费者|个人信息|一大堆|满天飞|转圈圈?|后面?加'+'|打不开|.{1,2}不了|进不去'
        self.re_all = '^('+re_noInfo_5+'|'+re_noInfo_4+'|'+re_other_3+'|'+re_noInfo_3+'|'+re_other_2+'|'+re_noInfo_2+'|'+re_other_1+'|'+re_noInfo_1+'|'+re_noInfo_0+')+$'
        self.pattern_p = re.compile(self.re_all)
        self.re_ch = re.compile(re_noInfo_0)
        self.re1 = re.compile('['+re_noInfo_1[1:-1]+re_other_1[1:-1]+']')
        self.re2 = re.compile('^([一太就虽只不].|.[就一个下着来住]|.不[开去掉]|.不上去?|不出来)$')

# func: initial cleanup and division of sentences
    def cutSent(self, s):
        if not type(s) == str or len(s) == 0:
            return ['。']
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
            sent_list.append(sent)
        return sent_list

    # Methods: sentence splitting, and regularization cleanup
    # row → clean/cleans: 'appid','comm'
    def re_clean(self, merge=False):
        print("comm_clean：row → clean/cleans")
        # read data
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Load Data", end='')
        df = pd.read_csv(self.row_datapath)
        print("\tlen:"+str(len(df)))
        # sentence splitting
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Sentence Cut", end='')
        df['comm'] = df.apply(lambda row: [sent for sent in self.cutSent(row['title'])+self.cutSent(row['content']) if len(re.sub(r'[^\u4E00-\u9FA5]', '', sent))>1], axis=1)
        df['len'] = df['comm'].apply(len)  
        df = df[(df["len"]) > 0]
        print("\tlen:"+str(len(df)))
        # regularization cleanup
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Sentence Clean with re")
        def rematch_comm(s):
            # Delete sentences of length less than 2
            s = self.re_ch.sub('', s)
            if len(s) < 2:
                return True
            # Delete a sentence with a word loop
            if len(re.sub('^'+s[0]+'+$','', s)) == 0:
                return True
            # Split the sentence into clauses of length 20
            if len(s)>20:
                sl = re.findall(r'.{20}', s)
                sl.append(s[len(sl)*20:])
            else:
                sl = [s]
            for s in sl:
                result = self.pattern_p.search(s)
                if result == None:
                    return False
            return True
        self.count = 1
        def rematch_comms(l):
            if self.count%(int(len(df)/10)) == 0 or self.count == len(df):
                print('\t\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- "+str(self.count)+'('+str(round(self.count/(len(df))*100, 2))+"%%) Finished")
            self.count += 1
            return [s for s in l if not rematch_comm(s)]
        df['comm'] = df.apply(lambda row: rematch_comms(row['comm']), axis=1)
        # remove empty list
        df['len'] = df.apply(lambda row: len(row['comm']), axis=1)
        df = df[(df["len"]) > 0]
        print("\tlen:"+str(len(df)))
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Save Data in "+str(self.clean_datapath))
        df[['appid','comm']].to_csv(self.clean_datapath, index=False)
        # combine comments from the same app into one
        if merge:
            print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Merge with APP and Save in "+str(self.cleans_datapath))
            appids = df['appid'].unique()
            with open(self.cleans_datapath, 'w', encoding='utf-8',newline='') as f:
                w = csv.writer(f)
                w.writerow(['appid','comms'])
                for appid in appids:
                    data = df[df['appid'] == appid]
                    words = []
                    for row in data.iterrows():
                        words += row[1]['comm']
                    if len(words) == 0:
                        continue
                    w.writerow([appid,words]) 

    # method: Segmentation, filtering of stopwords
    # clean → cut/cuts: 'appid','cut_comm'
    def cut(self, merge=False):
        import jieba as jb
        from jieba import posseg
        print("comm_cut：clean → cut/cuts")
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
        def cut_comm(s):
            words = []
            # 考虑词性
            for (w,flag) in list(posseg.lcut(s)):
                if not flag in ['v','vn','x','n','nr','ns','nz','nt','nrt','j']:
                    continue
                if len(w) > 6 or len(self.re_ch.sub('',w)) == 0:
                    continue
                if w in stopwords:
                    continue
                if len(self.re1.sub('',w)) == 0:
                    continue
                if len(self.re2.sub('',w)) == 0:
                    continue
                # if len(self.pattern_p.sub('', w)) == 0:
                #     continue
                words.append(w)
            return words                
        df['cut_comm'] = df['comm'].apply(cut_comm)
        # remove nan
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Remove App without Comm", end='')
        df['len'] = df.apply(lambda row: len(row['cut_comm']), axis=1)
        df = df.drop(df[df['len'] == 0].index)
        print("\tlen: "+str(len(df)))
        # save
        print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Saved Data in "+self.cut_datapath+"")
        df[['appid','cut_comm']].to_csv(self.cut_datapath, index=False)
        # combine comments from the same app into one
        if merge:
            print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Merge with APP and Save")
            appids = df['appid'].unique()
            with open(self.cuts_datapath, 'w', encoding='utf-8',newline='') as f:
                w = csv.writer(f)
                w.writerow(['appid','cut_comms'])
                for appid in appids:
                    data = df[df['appid'] == appid]
                    words = []
                    for row in data.iterrows():
                        words += row[1]['cut_comm']
                    if len(words) == 0:
                        continue
                    w.writerow([appid,words]) 
