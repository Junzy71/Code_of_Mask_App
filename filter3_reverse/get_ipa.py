import os
import json
import time
import numpy as np
import pandas as pd
import urllib.request

def get_ipa_files(appids, ipatool, ipa_path):
    for appid in appids:
        # get bundle
        url = 'https://itunes.apple.com/lookup?id='+appid
        response = urllib.request.urlopen(url=url, timeout=5)
        myjson = response.read().decode()
        if not myjson == '':
            myjson = json.loads(myjson)
            if not len(myjson['results']) == 0:
                bundle = myjson['results'][0]['bundleId']
                # download ipa
                cmd = ipatool+' download -b '+bundle+' -o '+ipa_path+' --purchase'
                os.system(cmd)