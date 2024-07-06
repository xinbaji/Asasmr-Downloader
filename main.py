import re
import requests
from lxml import etree
from threading import Thread
import time
import os
from Crypto.Cipher import AES
class GetAsasmrAudio():
    def __init__(self):
        self.targetUrl=u""
        self.m3u8Url=''
        self.m3u8UrlHost=""
        self.tsNum=''
        self.downloadcomplete=[]
        self.title=''
        self.asmrType=''
        self.origin=''
    def getM3u8(self):
        while True:
            self.targetUrl=input("输入asasmr的地址：")
            self.origin=self.targetUrl[0:self.targetUrl.find('com')+3]
            htmlData=requests.get(self.targetUrl).text
            html=etree.HTML(htmlData)
            '''var line = ["https:\/\/cfv1.huabeias.top\/video\/1718820880qhtpg\/index.m3u8?st=USSVTD9Dpd6mK5dfjN-83w&e=1720257324"];'''
            if 'sound' in self.targetUrl:
                self.asmrType='sound'
                print("识别为音频类型")
                m3u8Script=html.xpath('//*[@id="info"]/div[1]/script/text()')
                self.title=html.xpath('//*[@id="single"]/div[1]/div[1]/div[2]/h1/text()')[0]
                ex=',"url":"(.*?)","pic":'
                self.m3u8Url=re.findall(ex,str(m3u8Script),re.S)[0]
                self.m3u8Url='https:'+self.m3u8Url.replace("\\","")
                break
            elif 'video' in self.targetUrl:
                self.asmrType='video'
                print("识别为视频类型")
                m3u8Script=html.xpath('//*[@id="dooplay_player_response"]/script/text()')[0]
                self.title=html.xpath('//*[@id="single"]/div[2]/div[1]/div[2]/h1/text()')[0]
                ex="url: '(.*?)',"
                self.m3u8Url=re.findall(ex,str(m3u8Script),re.S)[0]
                self.m3u8Url=self.m3u8Url.replace("\\","")
                break
            else:
                print("地址非法请重新输入。")
        
        self.m3u8UrlHost=self.m3u8Url[0:self.m3u8Url.index("index.m3u8")]
        print(self.m3u8UrlHost)
        
        return self
    
    def getAudioContent(self):
        content=requests.get(self.m3u8Url).text
        ex="index(.*?)ts"
        self.tsNum=int(re.findall(ex,content,re.S)[-1].replace(".",""))
        os.makedirs(self.title,exist_ok=True)
        if self.asmrType == 'video':
            content=requests.get(self.m3u8Url).text
            ex='URI="(.*?)",IV'
            keyurl=re.findall(ex,content,re.S)[0]
            key=requests.get(keyurl).text.encode()
            print(key)
            self.aes=AES.new(key,AES.MODE_CBC,b'0000000000000000')
        for i in range(0,self.tsNum+1,1):
            self.downloadcomplete.append(i)
            tsUrl=self.m3u8UrlHost+"index"+str(i)+".ts"
            Thread(target=self.downloadAudioTs,args=(tsUrl,i)).start()
        while(len(self.downloadcomplete) != 0):
            time.sleep(0.1)
            continue
        return self
        
    def downloadAudioTs(self,url,num):
        retryCurrentNum=0
        retryMaxNum=10
        headers={
            'Referer':
self.origin+'/',
'User-Agent':
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
'Origin':
self.origin
        }
        while retryCurrentNum <=retryMaxNum:
            try:
                data=requests.get(url,headers=headers).content 
                if self.asmrType =='video':
                    
                    data=self.aes.decrypt(data)
            except Exception as e:
                print("ERROR:"+str(e))
                time.sleep(1)
            else:
                break

        with open("./"+self.title+"/"+str(num)+".ts","wb") as f:
            f.write(data)
            f.close    
        self.downloadcomplete.remove(num)
        print("当前正在下载切片："+str(self.downloadcomplete))

        
    def tsToMp4(self):
        print("正在合并...")
        if self.asmrType=='sound':
            path="./"+self.title+"/"+self.title+".mp3"
        elif self.asmrType == 'video':
            path="./"+self.title+"/"+self.title+".mp4"
        with open (path,"wb") as f1:
            for i in range(0,int(self.tsNum)+1,1):
                with open ("./"+self.title+"/"+str(i)+".ts" ,"rb") as f2:
                    f1.write(f2.read())
                    f2.close()
                os.remove("./"+self.title+"/"+str(i)+".ts")
            f1.close()

        return self
    
gaa=GetAsasmrAudio()
gaa.getM3u8().getAudioContent().tsToMp4()
print("成功下载："+gaa.title)