import re
import requests
from lxml import etree
from threading import Thread
import time
import os
class GetAsasmrAudio():
    def __init__(self):
        self.targetUrl=u"https://www.asasmr4.com/sound/24542.html"
        self.m3u8Url=''
        self.m3u8UrlHost=""
        self.tsNum=''
        self.downloadcomplete=[]
        self.title=''
    def getM3u8(self):
        htmlData=requests.get(self.targetUrl).text
        html=etree.HTML(htmlData)
        m3u8Script=html.xpath('//*[@id="info"]/div[1]/script/text()')
        self.title=html.xpath('//*[@id="single"]/div[1]/div[1]/div[2]/h1/text()')[0]
        ex=',"url":"(.*?)","pic":'
        self.m3u8Url=re.findall(ex,str(m3u8Script),re.S)[0]
        self.m3u8Url='https:'+self.m3u8Url.replace("\\","")
        self.m3u8UrlHost=self.m3u8Url[0:self.m3u8Url.index("index.m3u8")]
        print(self.m3u8UrlHost)
        
        return self
    
    def getAudioContent(self):
        content=requests.get(self.m3u8Url).text
        ex="index(.*?)ts"
        self.tsNum=int(re.findall(ex,content,re.S)[-1].replace(".",""))
        os.makedirs(self.title,exist_ok=True)
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
        while retryCurrentNum <=retryMaxNum:
            try:
                data=requests.get(url).content   
            except Exception as e:
                print("ERROR:"+str(e))
            else:
                break

        with open("./"+self.title+"/"+str(num)+".ts","wb") as f:
            f.write(data)
            f.close    
        self.downloadcomplete.remove(num)
        print("当前正在下载切片："+str(self.downloadcomplete))

        
    def tsToMp4(self):
        print("正在合并...")
        with open ("./"+self.title+"/"+self.title+".mp3","wb") as f1:
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