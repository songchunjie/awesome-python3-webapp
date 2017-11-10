#抓取博鳌论坛网站会议动态，写入文件
from bs4 import BeautifulSoup   
import random
import requests 
import socket 
import time
import http.client 
import csv
import urllib

loop = 0

def get_html(url,data=None):
    htmltxt = urllib.request.urlopen(url).read().decode('utf-8')
    return htmltxt

def get_hyhdhdzlist(html_txt):         #获取年度会议列表
    final = []
    bs=BeautifulSoup(html_txt,"html.parser")
    body = bs.body
    data = body.find("div",{"class":"listmenu"})
    ul = data.find("ul")
    li = ul.find_all("li")
    for liobj in li:
        temp = []
        alink = liobj.find("a")
        temp.append(alink["href"])
        temp.append(alink.string)
        final.append(temp)

    return final

def get_more_url(html_txt):         #获取会议动态url
    bs=BeautifulSoup(html_txt,"html.parser")
    body = bs.body
    aurl = ""
    try:
        data = body.find("div",{"class":"zj_ist"})
        h2 = data.find("h2",{"class":"zj_title"})
        aa = h2.find_all("a")
        alink = aa[0]
        aurl = alink["href"]
    except:
        try:
            data = body.find("div",{"class":"zj_nav"})
            aa = data.find_all("a")
            for m in aa:
                str = m.find("span").string
                if str == "会议动态":
                    aurl = m["href"]
        except:
            data = body.find("div",{"class":"bl_right"})
            h2 = data.find("h2",{"class":"bl_title"})
            aa = h2.find_all("a")
            alink = aa[0]
            aurl = alink["href"]
    return aurl

def get_listdata(html_txt,confername):      #获取会议动态列表内容
    global loop
    final=[]
    pagenum = 1
    bs=BeautifulSoup(html_txt,"html.parser")   
    body=bs.body   
    try:
        data=body.find("div",{"class":"part3right"}) 
        ul=data.find("ul",{"class":"list"})  
        li=ul.find_all("li")   

        for liobj in li:
            loop = loop + 1
            temp=[]
            temp.append(loop)
            temp.append(confername)
            date=liobj.find("span").string   
            temp.append(date)   
            alink = liobj.find("a")
            temp.append(alink['href']) 
            temp.append(alink.string)
            final.append(temp)   
    except:
        data=body.find("div",{"class":"rxp_fltdt"}) 
        aa=data.find_all("a")   

        for a in aa:
            loop = loop + 1
            temp=[]
            temp.append(loop)
            temp.append(confername)
            temp.append("2017")   
            temp.append(a['href']) 
            temp.append(a.string)
            final.append(temp)   

    selectobj = body.find("select")
    optionobj = selectobj.find_all("option")
    pagenum = len(optionobj)

    return final,pagenum



def get_conferencedata(html_txt,primarykey):      #获取会议动态正文内容
    final=[]
    bs=BeautifulSoup(html_txt,"html.parser")   
    body=bs.body   
    try:
        temp=[]
        temp.append(primarykey)
        data=body.find("div",{"class":"part3right"}) 
        h3=data.find("h3")  
        temp.append(h3.get_text())
        pnode = data.find_all("p")
        content = ""
        for node in pnode[2:]:
            content = content + node.get_text()+"\n"
        temp.append(content)
        final.append(temp)
    except:
        temp=[]
        temp.append(primarykey)
        data=body.find("div",{"class":"part3"}) 
        h3=data.find("h3")  
        temp.append(h3.get_text())
        pnode = data.find_all("p")
        content = ""
        for node in pnode[2:]:
            content = content + node.get_text()+"\n"
        temp.append(content)
        final.append(temp)

    return final


def write_data(data, name):
    file_name = name
    with open(file_name, 'a', errors='ignore', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerows(data)

def get_url():
    requrl = []
    sign = range(1,5)
    for i in sign:
        if i ==1 :
            url = "http://www.boaoforum.org/2017mgdt/index.jhtml"
            requrl.append(url)
        else:
            url = "http://www.boaoforum.org/2017mgdt/index_"+ str(i) +".jhtml"
            requrl.append(url)
            
    return requrl

def get_urlstr():
    requrl = []
    sign = range(1,5)
    for i in sign:
        if i ==1 :
            url = "http://www.boaoforum.org/2017mgdt/index.jhtml"
            requrl.append(url)
        else:
            url = "http://www.boaoforum.org/2017mgdt/index_"+ str(i) +".jhtml"
            requrl.append(url)
            
    return requrl

if __name__=="__main__":
    year = ['2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017']
    mainurl = 'http://www.boaoforum.org/hyhdhdzl2017/index.jhtml'
    html=get_html(mainurl)
    yearresult=get_hyhdhdzlist(html)
    listurl = []
    for i in yearresult:
        print(i)
        tempurl = "http://www.boaoforum.org"+ i[0]
        temphtml = get_html(tempurl)
        moreurl = get_more_url(temphtml)
        print(moreurl)
        listurl.append(moreurl)
        listhtml = get_html("http://www.boaoforum.org"+ moreurl)
        result = get_listdata(listhtml,i[1])
        write_data(result[0],"Conference.csv")
        for ll in result[0]:
            primarykey = ll[0]
            contenturl = "http://www.boaoforum.org/" + ll[3]
            contenthtml = get_html(contenturl)
            contentresult = get_conferencedata(contenthtml,primarykey)
            write_data(contentresult,"Content.csv")
           
        alist = moreurl.split("/")
        print("================")
        print(alist)
        if result[1] > 1:
            pagenumlist = range(2,result[1]+1)
            for n in pagenumlist:
                pagelisturl = "http://www.boaoforum.org/" + alist[1] + "/" + "index_"+ str(n) +".jhtml"
                pagelisthtml = get_html(pagelisturl)
                pagelistresult = get_listdata(pagelisthtml,i[1])
                write_data(pagelistresult[0],"Conference.csv")
                for ll in pagelistresult[0]:
                    primarykey = ll[0]
                    contenturl = "http://www.boaoforum.org/" + ll[3]
                    contenthtml = get_html(contenturl)
                    contentresult = get_conferencedata(contenthtml,primarykey)
                    write_data(contentresult,"Content.csv")

            

    
##    urllist=get_url()
##    for url in urllist:
##        html=get_html(url)
##        result=get_listdata(html)
##        write_data(result,"Conference.csv")
##        for i in result:
##            print(i)        #控制台打印输出
    
    
