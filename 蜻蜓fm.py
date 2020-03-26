import requests 
import json
import datetime
import os
import _thread
import time

当前所在路径=os.path.dirname(__file__)
vid=""
会话=requests.session()
flag=0
头={
"Host": "webapi.qingting.fm",
"Connection": "keep-alive",
"Accept": "application/json, text/plain, */*",
"DNT": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
"Origin": "https://www.qingting.fm",
"Sec-Fetch-Site": "same-site",
"Sec-Fetch-Mode": "cors",
"Referer": "https://www.qingting.fm/radios/"+vid+"/",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "zh-CN,zh;q=0.9"
}
会话.headers=头

def 获取当天时间():
    return datetime.datetime.now().strftime('%Y%m%d')

#获取该页视频列表 
def 获取视频列表(vid):
    return json.loads(会话.get("https://webapi.qingting.fm/api/pc/radio/"+vid).text)

def 初始化下载路径(电台名,日期=''):
    下载路径=os.path.join(当前所在路径,'下载')
    if not os.path.exists(下载路径):
        os.makedirs(下载路径)
    电台路径=os.path.join(下载路径,电台名)
    if not os.path.exists(电台路径):
        os.makedirs(电台路径)
    if len(日期) > 0:
        日期路径=os.path.join(电台路径,日期)
        if not os.path.exists(日期路径):
            os.makedirs(日期路径)
        return 日期路径
    else :
        return 电台路径

def 获取电台名(视频列表):
    return 视频列表['album']['title']

def 该视频尚未结束(日期,结束时间):
    当前时间=datetime.datetime.now().strftime('%Y%m%d:%H:%M:%S')
    当前时间=当前时间.split(":")
    结束时间=日期.split(":")+结束时间.split(":")
    #print(当前时间,结束时间)
    #print(当前时间,结束时间)
    if int(当前时间[0])==int(结束时间[0]):
        if int(当前时间[1])<int(结束时间[1]) and int(当前时间[2])<int(结束时间[2]) and int(当前时间[3])<int(结束时间[3]):
            return True
    return False

def 近三日下载(视频列表):
    print("开始同步近三日的所有电台")
    for i in range(-2,1):
        print(str(3+i)+'/3')
        日期=(datetime.datetime.now()+datetime.timedelta(days=i)).strftime('%Y%m%d')#获取今日日期
   # print(日期)
        指定日期下载(视频列表,日期,False)
    print("近三日电台已经同步完成！")

def 开始下载视频(保存路径,日期,开始时间,结束时间,节目名):
    global flag
    文件路径=os.path.join(保存路径,开始时间.replace(":",".")+'-'+结束时间.replace(":",".")+' '+节目名+'.aac')
    if not os.path.exists(文件路径):
        url='https://lcache.qingting.fm/cache/'+日期+'/'+vid+'/'+vid+'_'+日期+'_'+开始时间.replace(":","")+'_'+结束时间.replace(":","")+'_24_0.aac'
        #print("正在下载:"+节目名)
        r = requests.get(url, stream=True)
        f = open(文件路径, "wb")
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)
    flag = flag+1

def 指定日期下载(视频列表,日期,显示进度,视频名=""):
    global flag
    flag=0
    当天视频=视频列表['pList'][list(视频列表['pList'].keys())[0]]#用今天的时间表推断之前的时间表
    #print(日期)
    保存路径=初始化下载路径(获取电台名(视频列表),日期)
    #/下载/河南/日期/片名_开始时间_结束时间.aac
    #下载当日的视频
    当前队列数量=0
    for 视频 in 当天视频:
        开始时间=视频['start_time']
        结束时间=视频['end_time']
        节目名=视频['title']
        if len(视频名)>0:
            if 节目名!=视频名:
                continue
        if 该视频尚未结束(日期,视频['end_time']):
            #print(日期,视频['end_time'])
            if len(视频名) >0 and 当前队列数量==0:
                print("该节目尚未播出！三秒后自动返回主菜单")
                time.sleep(3)
            break
        try:
                _thread.start_new_thread( 开始下载视频, (保存路径,日期,开始时间,结束时间,节目名) )
                当前队列数量=当前队列数量+1
        except:
                print("多线程异常，正在尝试重试……")
    while flag<当前队列数量:
        if 显示进度:
            print("已下载："+str(flag)+"/"+str(当前队列数量))
        time.sleep(1)
    if 显示进度:
        print("已下载："+str(flag)+"/"+str(当前队列数量))
    flag=0


def 功能选择(视频列表):
    os.system("cls")
    chose=input("\t丨=========蜻蜓FM电台下载=======丨\n\
    \t丨\t\t\t\t丨\n\
    \t丨\t版本:v0.0.2\t\t丨\n\
    \t丨\t\t\t\t丨\n\
    \t丨\t当前电台名:"+获取电台名(视频列表)+"\t丨\n\
    \t丨\t\t\t\t丨\n\
    \t丨\t1.自动同步近三日视频\t丨\n\
    \t丨\t\t\t\t丨\n\
    \t丨\t2.下载某日 所有 视频\t丨\n\
    \t丨\t\t\t\t丨\n\
    \t丨\t3.下载某日 指定 视频\t丨\n\
    \t丨\t\t\t\t丨\n\
    \t丨==============================丨\n保存位置："+os.path.join(当前所在路径,'下载')+" \
    \n\n   请选择需要的功能的序号后回车：")
    if chose is '1':
        近三日下载(视频列表)
        os.system("pause")
    if chose is '2':
        print("日期格式为：yyyymmdd\n例子：\n\t2020年2月6日要写成20200206\n\n")
        while True:
            日期=input("请输入指定日期（两个月内）:")
            if len(日期)==8:
                break
            print("日期格式错误，请重新输入！")
        指定日期下载(视频列表,日期,True)
        print("所有内容已经下载完成！")
        os.system("pause")
    if chose is '3':
        print("日期格式为：yyyymmdd-视频名字\n例子：\n\t2020年2月6日的《河南新闻》节目要写成：20200206-河南新闻")
        节目名=input("请输入下载的日期和节目：")
        分割=节目名.split("-")
        指定日期下载(视频列表,分割[0],True,分割[1])
        print("所有内容已经下载完成！")
        os.system("pause")
    功能选择(视频列表)


#主函数入口
if __name__ == '__main__':    
    vid=input("请输入电台的id\n\
    如网址 https://www.qingting.fm/radios/1215/ 的电台id为  1215\n\
id：")
    视频列表=获取视频列表(vid)
    功能选择(视频列表)
    
