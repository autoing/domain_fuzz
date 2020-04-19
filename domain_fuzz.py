import re
import time
import html
import queue
import requests
import threading
from itertools import product
from urllib.parse import urlparse
from argparse import ArgumentParser,SUPPRESS
requests.packages.urllib3.disable_warnings()

class GetUrl(object):
    def __init__(self):
        super(GetUrl, self).__init__()
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0'}

    def geturl(self,url):
        try:
            if Options == "GET":
                response = requests.get(url, verify=False, headers=self.headers, allow_redirects=False,timeout = 15)
            if Options == "HEAD":
                response = requests.head(url, verify=False, headers=self.headers, allow_redirects=False,timeout = 15)
            try:
                location = response.headers['Location']
                self.host = urlparse(url)
                self.scheme = self.host.scheme
                self.netloc = self.host.netloc
                if location.lower().startswith("http"):
                    url = location

                elif location.lower().startswith("/"):
                    url = f'{self.scheme}://{self.netloc}{location}'

                elif location.lower().startswith("/") == False and self.netloc.split(':')[0] in location.lower():
                    url = f'{self.scheme}://{location}'

                elif location.lower().startswith("/") == False and self.netloc.split(':')[0] not in location.lower():
                    url = f'{self.scheme}://{self.netloc}/{location}'
                return self.geturl(url)
            except Exception as e:
                return response
        except Exception as e:
            pass

class Asset(threading.Thread):
    def run(self):
        while True:
            while not waittask.empty():
                url = args.url.replace('$$',f'{waittask.get()}')
                response = GetUrl().geturl(url)
                if response:
                        backurl = response.url
                        title = get_title(response)
                        if title:
                            print('进度：{:.2%} 原始链接：{} 跳转链接：{} 标题：{}'.format(1-waittask.qsize()/sums,url,backurl,title))
                        else:
                            print('进度：{:.2%} 原始链接：{} 跳转链接：{}'.format(1-waittask.qsize()/sums,url,backurl))
            exit()

def get_title(response):
    encoding = response.apparent_encoding
    try:
        title =  re.findall(b'<title>(.*?)</title>',response.content,re.S|re.M|re.I)[0]
        try:
            return ''.join(html.unescape(re.sub('\s{2,}',' ',title.decode())).replace(' ','_').split()).replace('_',' ').strip()
        except Exception as e:
            try:
                return ''.join(html.unescape(re.sub('\s{2,}',' ',title.decode('gbk'))).replace(' ','_').split()).replace('_',' ').strip()
            except Exception as e:
                try:
                    return ''.join(html.unescape(re.sub('\s{2,}',' ',title.decode(encoding.lower()))).replace(' ','_').split()).replace('_',' ').strip()
                except Exception as e:
                    return ''
    except Exception as e:
        return ''

def main():
    for dicts in dictslist:
        waittask.put(''.join(dicts))
    dictslist.clear()
    global sums
    sums = waittask.qsize()
    for i in range(1,int(args.thread)):
        asset = Asset()
        asset.start()

if __name__ == '__main__':
    parser = ArgumentParser(description='',prog="",usage=SUPPRESS)
    parser.add_argument('-u', '--url', required=True, help='目标链接：http://$$.mi.com 则表示爆破mi.com的子域名，$$为标记点，想爆哪里就放在那里')
    parser.add_argument('-r', '--ranges', default='1-4', help='字典范围：默认字典长度为1-4位数所有可能组合，加上该参数表示使用自定义长度。')
    parser.add_argument('-t', '--thread', default=20, nargs='?', help='线程：默认20个线程，该参数表示自定义线程数')
    parser.add_argument('-o', '--options', default='g', nargs='?',help='请求模式：默认GET模式，加上该参数表示使用head请求方式')
    parser.add_argument('-m', '--mode', default='l', nargs='?', help='字典模式：默认26个字母所有可能排序，加上该参数表示在字母基础上加上0-9的数字')
    args = parser.parse_args()
    if args.options == None:
        Options = 'HEAD'
    else:
        Options = 'GET'
    if args.mode == None:
        Mode = 'abcdefghijklmnopqrstuvwxyz0123456789'
    else:
        Mode = 'abcdefghijklmnopqrstuvwxyz'
    if len(args.ranges.split('-')) == 2:
        dictslist = []
        start,end = int(args.ranges.split('-')[0]),int(args.ranges.split('-')[1])
        for i in range(start,end+1):
            result = product(Mode, repeat=i)
            dictslist.extend(list(result))
    else:
        dictslist = []
        result = product(Mode, repeat=int(args.ranges))
        dictslist.extend(list(result))
    waittask = queue.Queue()
    main()
