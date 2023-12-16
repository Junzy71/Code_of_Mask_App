import csv
import json
import time
import requests
import urllib.request
from bs4 import BeautifulSoup

class APPStore:
    def __init__(self, appids, profile_path, comm_path, recommend_path, info_path):
        self.appid_list = appids
        self.appid_set = set(appids)
        self.visited = set()
        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        self.profile_path = profile_path
        self.comm_path = comm_path
        self.recommend_path = recommend_path
        self.info_path = info_path
        self.screenshot_dir = '/'.join(info_path.split('/')[:-1])+'/screenshot/'
        self.error_path = 'spider/error.txt'
        self.print_path = 'spider/print.txt'

    # init result file:
    # profile：'appid','name','profile'
    # comment：'appid','title','content'
    # recommendation：'appid','recommend'
    # other information：
    def init_file(self):
        with open(self.profile_path,'w',encoding='utf-8',newline='') as f:
            csv.writer(f).writerow(['appid','name','profile'])
        with open(self.comm_path,'w',encoding='utf-8',newline='') as f:
            csv.writer(f).writerow(['appid','title','content'])
        with open(self.recommend_path,'w',encoding='utf-8',newline='') as f:
            csv.writer(f).writerow(['appid','recommend'])
        with open(self.info_path,'w',encoding='utf-8',newline='') as f:
            csv.writer(f).writerow(['appid','name','developer_id','developer_name','comm_count','recomm_count','screenshots_count','rate','rate_num','version','update_content','supplier', 'size', 'genre', 'compatibility', 'language', 'age', 'copyright', 'price'])

    # init error and print file
    def init_log(self):
        with open(self.print_path,'w',encoding='utf-8') as f:
            f.write('')
        with open(self.error_path,'w',encoding='utf-8') as f:
            f.write('')
    
    # 获得app的评论，保存到文件  
    def get_comm(self, appid):
        with open(self.print_path,'a',encoding='utf-8') as f:
            f.write('\tcomm GET: ')
        count = 0
        with open(self.comm_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for page in range(10):
                myurl="https://itunes.apple.com/rss/customerreviews/page="+str(page+1)+"/id="+str(appid)+"/sortby=mostrecent/json?l=en&&cc=cn"
                try:
                    response = urllib.request.urlopen(url=myurl, timeout=5)
                    with open(self.print_path,'a',encoding='utf-8') as f:
                        f.write('page'+str(page)+' ')
                except Exception as e:
                    with open(self.print_path,'a',encoding='utf-8') as f:
                        f.write('page'+str(page)+'error ')
                    with open(self.error_path,'a',encoding='utf-8') as f:
                        f.write('Get Comm Error ----- ' + str(appid) + ' in page ' + str(page) + ' with error ' +str(e)+'\n')
                    continue
                myjson = json.loads(response.read().decode())
                if not "entry" in myjson["feed"]:
                    continue
                if type(myjson["feed"]["entry"]) == list:
                    for entry in myjson["feed"]["entry"]:
                        title = entry["title"]["label"]
                        content = entry["content"]["label"]
                        writer.writerow([appid, title if len(title)>0 else '。', content if len(content)>0 else '。'])
                        count += 1
                else:
                    title = myjson["feed"]["entry"]["title"]["label"]
                    content = myjson["feed"]["entry"]["content"]["label"]
                    writer.writerow([appid, title if len(title)>0 else '。', content if len(content)>0 else '。'])
                    count += 1
                time.sleep(1)
        with open(self.print_path,'a',encoding='utf-8') as f:
            f.write('\tsum:'+str(count)+'\n')
        return count
       
    # get metadata of app
    def get_app_metadata(self, app_id, rec=True, get_pic=False):
        url = 'https://apps.apple.com/cn/app/id'+app_id+'?platform=iphone'
        try:
            response = self.session.get(url=url, headers=self.header,timeout=5).content
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write(str(app_id)+' \'s html GET\n')
        except Exception as e:
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write(str(app_id)+' \'s html ERROR\n')
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('Get Html Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
            return
        html = BeautifulSoup(response, 'html.parser')
        # name
        try:
            app_name = html.find_all('h1', class_='app-header__title')
            app_name = app_name[0].get_text().split('\n')[1].strip()
            app_name = app_name.replace('\u202a','').replace('\u202c','')
            app_name = app_name.replace('/', '-').replace('\\', '-').replace(':', '-').replace('*', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '-').replace('?', '')
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tname GET:'+str(app_name)+'\n')
        except Exception as e:
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tname ERROR\n')
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('Get Name Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
                return
        # profile
        try:
            app_profile = html.find('p', dir="false")
            app_profile = str(app_profile)[33:-4].replace('<br/>','\n').replace('\u2028','')
            if not app_profile == '':
                with open(self.profile_path,'a',encoding='utf-8',newline='') as f:
                    csv.writer(f).writerow([app_id,app_name,app_profile])
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tprofile GET\n')
        except Exception as e:
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tprofile ERROR\n')
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('Get Profile Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
        # comment (new 500)
        comm_count = 0
        try:
            comm_count = self.get_comm(app_id)
        except Exception as e:
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tcomm ERROR\n')
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('Get Comm Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
        # recommendation
        app_recommend = html.find_all('a', class_='we-lockup targeted-link l-column small-2 medium-3 large-2 we-lockup--shelf-align-top we-lockup--in-app-shelf')
        recomm_ids = []
        for recomm in app_recommend:
            try:
                recomm_id = recomm['href'].split('/')[-1][2:].strip()
                if not recomm_id == '':
                    recomm_ids.append(recomm_id)
                if rec and recomm_id not in self.appid_set:
                    self.appid_list.append(recomm_id)
                    self.appid_set.add(recomm_id)
            except Exception as e:
                with open(self.error_path,'a',encoding='utf-8') as f:
                    f.write('Get Recommend Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')  
                continue
        with open(self.print_path,'a',encoding='utf-8') as f:
            f.write('\trecomm GET:'+str(len(recomm_ids))+'\n')
        if len(recomm_ids) > 0:
            with open(self.recommend_path,'a',encoding='utf-8',newline='') as f:
                csv.writer(f).writerow([app_id,recomm_ids])
        # screenshots
        screenshots = []
        if get_pic:
            screenshots = html.find_all('picture', class_=f'we-artwork--screenshot-platform-iphone')
            for i in range(len(screenshots)):
                screenshot_name = app_id+'_iphone_'+str(i)+'.png'
                try:
                    screenshot_url = "https" + str(screenshots[i]).split("we-artwork__source")[-1].split(".png ")[0].split("https")[-1] + ".png"
                    screenshot = self.session.get(url=screenshot_url, headers=self.header, stream=True, timeout=10)
                except Exception as e:
                    with open(self.error_path,'a',encoding='utf-8') as f:
                        f.write('Get Screenshot Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')  
                    continue
                with open(self.screenshot_dir + screenshot_name, "wb") as code:
                    code.write(screenshot.content)
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tscreenshots GET\n')
        # developer
        developer_name = 'unknown_Dname' 
        developer_id = 'unknown_Did'
        try:
            developer = html.find_all('h2', class_='product-header__identity app-header__identity')
            developer_name = developer[0].find('a').get_text().strip()
            developer_id = developer[0].find('a')['href'].split('/')[-1][2:]
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tdeveloper GET\n')
        except Exception as e:
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('Get Developer Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')   
        # rate
        try:
            rate_ = html.find_all('figcaption', class_='we-rating-count star-rating__count')
            [rate, rate_num] = rate_[0].get_text().split(' • ')
            rate_num = rate_num.split(' ')[0]
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\trate GET\n')
        except Exception as e:
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('No Rate ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
            rate = -1
            rate_num = 0  
        # update
        update_content = ''
        version = '1.0.0'
        try:
            update_content = html.find_all('div', class_='we-truncate we-truncate--multi-line we-truncate--interactive')
            update_content = update_content[0].get_text().strip()
            version = html.find_all('p', class_='l-column small-6 medium-12 whats-new__latest__version')
            version = version[0].get_text().strip()
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tupdate GET\n')
        except Exception as e:
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('No Update Info ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
        # privacies
        privacies = []
        try:
            privacies = html.find_all('span', class_='privacy-type__grid-content privacy-type__data-category-heading')
            privacies = [privacy.get_text().strip() for privacy in privacies]
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tprivacies GET\n')
        except Exception as e:
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('No Privacy Info ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
        # other informations
        [supplier, size, genre, compatibility, language, age, copyright_, price, compatibility, age] = ['unknown','unknown','unknown','unknown','unknown','unknown','unknown','unknown','unknown','unknown'] 
        try:
            items = html.find_all('dd', class_='information-list__item__definition')
            if len(items) == 8:
                [supplier, size, genre, compatibility, language, age, copyright_, price] = [item.get_text().strip() for item in items]
            elif len(items) == 9:
                [supplier, size, genre, compatibility, language, age, loc, copyright_, price] = [item.get_text().strip() for item in items]
            elif len(items) == 10:
                [supplier, size, genre, compatibility, language, age, loc, copyright_, price, inpurchase] = [item.get_text().strip() for item in items]
                price += inpurchase.replace('\n', '，')
            compatibility = ''.join([c.strip() for c in compatibility.split(' ') if not c.strip()==''])
            age = '，'.join([c.strip() for c in age.split(' ') if not c.strip()=='']).replace('\n','，')
            with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\tother Info GET\n')
        except Exception as e:
            with open(self.error_path,'a',encoding='utf-8') as f:
                f.write('Get Other Info Error ----- ' + str(app_id) + ' with error ' +str(e)+'\n')
        # save metadata
        with open(self.print_path,'a',encoding='utf-8') as f:
                f.write('\n')
        with open(self.info_path,'a',encoding='utf-8',newline='') as f:
            csv.writer(f).writerow([app_id,app_name,developer_id,developer_name,comm_count,str(len(recomm_ids)),str(len(screenshots)) if get_pic else 0,rate,rate_num,version,update_content,supplier, size, genre, compatibility, language, age, copyright_, price])

    # Cleaning up duplicates
    def clean(self):
        import pandas as pd
        log = ''
        # profile key：appid
        df = pd.read_csv(self.profile_path)
        print('profile:'+str(len(df)), end='->')
        log = log+'profile:'+str(len(df))+'->'
        df.drop_duplicates(subset=['appid'], keep='last', inplace=True)
        df.to_csv(self.profile_path, index=False)
        print(str(len(df)), end='  ')
        log = log+str(len(df))+'  '
        # comment key：all
        df = pd.read_csv(self.comm_path)
        print('comm:'+str(len(df)), end='->')
        log = log+'comm:'+str(len(df))+'->'
        df.drop_duplicates(keep='last', inplace=True)
        df.to_csv(self.comm_path, index=False)
        print(str(len(df)), end='  ')
        log = log+str(len(df))+'  '
        # recommendation key：appid
        df = pd.read_csv(self.recommend_path)
        print('recommend:'+str(len(df)), end='->')
        log = log+'recommend:'+str(len(df))+'->'
        df.drop_duplicates(subset=['appid'], keep='last', inplace=True)
        df.to_csv(self.recommend_path, index=False)
        print(str(len(df)), end='  ')
        log = log+str(len(df))+'  '
        # other information key：appid
        df = pd.read_csv(self.info_path)
        print('info:'+str(len(df)), end='->')
        log = log+'info:'+str(len(df))+'->'
        df.drop_duplicates(subset=['appid'], keep='last', inplace=True)
        df.to_csv(self.info_path, index=False)
        print(str(len(df)))
        log = log+str(len(df))+'\n'
        # save
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(log)

    # main
    # rec: crawl iteratively; pic: get screenshots
    def spider(self, rec=0, get_pic=False):
        self.session = requests.session()
        if rec > 0:
            index = 0
            for i in range(rec):
                if index >= len(self.appid_list):
                    break
                appid = self.appid_list[index].strip()
                if appid.strip() == '': continue
                if appid in self.visited:
                    index += 1
                    continue
                self.get_app_metadata(appid,True, get_pic)
                self.visited.add(appid)
                with open('visited.txt','a',encoding='utf-8') as f:
                    f.write(str(appid)+'\n')
                index += 1
        else:
            for appid in self.appid_list:
                if appid.strip() == '': 
                    break
                    # print('--------------- test unavailable app ---------------\n')
                    # continue
                self.get_app_metadata(appid.strip(),False,get_pic)
        self.session.close()
