from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import datetime
import pandas as pd

import numpy as np
import re
import time
from datetime import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from keras.models import model_from_json
import cv2

global classifiers


def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})   

def Aboutus(request):
    if request.method == 'GET':
       return render(request, 'Aboutus.html', {})

    
def SearchTextProduct(request):
    if request.method == 'GET':
       return render(request, 'SearchTextProduct.html', {})

def SearchImageProduct(request):
    if request.method == 'GET':
       return render(request, 'SearchImageProduct.html', {})

def get_data(pageNo,linkName):  
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    r = requests.get(linkName+'ref=zg_bs_pg_'+str(pageNo)+'?ie=UTF8&pg='+str(pageNo), headers=headers)#, proxies=proxies)
    content = r.content
    soup = BeautifulSoup(content)
    #print(soup)

    alls = []
    for d in soup.findAll('div', attrs={'class':'a-section a-spacing-none aok-relative'}):
        #print(d)
        name = d.find('span', attrs={'class':'zg-text-center-align'})
        n = name.find_all('img', alt=True)
        #print(n[0]['alt'])
        author = d.find('a', attrs={'class':'a-size-small a-link-child'})
        rating = d.find('span', attrs={'class':'a-icon-alt'})
        users_rated = d.find('a', attrs={'class':'a-size-small a-link-normal'})
        price = d.find('span', attrs={'class':'p13n-sc-price'})

        all1=[]
        if n is not None:
            all1.append(n[0]['src'])
        else:
            all1.append("no-image")

        if name is not None:
            #print(n[0]['alt'])
            all1.append(n[0]['alt'])
        else:
            all1.append("unknown-product")

        if author is not None:
            #print(author.text)
            all1.append(author.text)
        elif author is None:
            author = d.find('span', attrs={'class':'a-size-small a-color-base'})
            if author is not None:
                all1.append(author.text)
            else:    
                all1.append('0')

        if rating is not None:
            #print(rating.text)
            all1.append(rating.text)
        else:
            all1.append('-1')

        if users_rated is not None:
            #print(price.text)
            all1.append(users_rated.text)
        else:
            all1.append('0')     

        if price is not None:
            #print(price.text)
            all1.append(price.text)
        else:
            all1.append('0')
        alls.append(all1)    
    return alls
    

def SearchImageProductAction(request):
    if request.method == 'POST':
        myfile = request.FILES['t1'].name
        print(myfile)
        image = cv2.imread('testImages/'+myfile)
        img = cv2.resize(image, (64,64))
        im2arr = np.array(img)
        im2arr = im2arr.reshape(1,64,64,3)
        img = np.asarray(im2arr)
        img = img.astype('float32')
        img = img/255
        with open('model/model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            classifier = model_from_json(loaded_model_json)
        classifier.load_weights("model/model_weights.h5")
        classifier._make_predict_function()   
        json_file.close()
        preds = classifier.predict(img)
        predict = np.argmax(preds)
        cats = ['Home Appliances','Decor','Electronic Devices','Furniture','Home Essentials']
        category = cats[predict]
        print(category)
        filterValue = request.POST.get('t2', False)
        rangeValue = request.POST.get('t3', False)
        arr = str(rangeValue).split("-")
        start = int(arr[0].strip())
        end = int(arr[1].strip())
        #end = int(arr[1].strip())
        url = 'none'
        if category == 'Electronic Devices':
            url = 'https://www.amazon.in/gp/bestsellers/electronics/'
        if category == 'Home Appliances':
            url = 'https://www.amazon.in/gp/bestsellers/kitchen/1380045031/'
        if category == 'Home Essentials':
            url = 'https://www.amazon.in/Home-Essentials/s?k=Home+Essentials/'
        if category == 'Furniture':
            url = 'https://www.amazon.in/gp/bestsellers/kitchen/5689444031/'    
        if category == 'Decor':
            url = 'https://www.amazon.in/gp/bestsellers/kitchen/1380374031/'
        results = []
        for i in range(1, 3):
            results.append(get_data(i,url))
        flatten = lambda l: [item for sublist in l for item in sublist]
        df = pd.DataFrame(flatten(results),columns=["image",'Book Name','Author','Rating','Customers_Rated', 'Price'])
        df = df.values
        output = '<table border="1" align="center">'
        output+='<tr><th>Product Name</th><th>Description</th><th>Ratings</th><th>Total Customers Rated</th><th>Price</th><th>Product Image URL</th><th>Product URL</th></tr>'
        for i in range(len(df)):
            if filterValue == 'Price Range':
                price = df[i,5]
                price = price.strip()
                price = re.findall('\d+',price)
                value = ''
                for m in range(0,(len(price)-1)):
                    value+=price[m]
                value = value.strip()
                if len(value) == 0:
                    value = 0
                price = float(value)
                if price >= start and price <= end:
                    output+='<tr><td><font size="" color="black">'+df[i,1]+'</td><td><font size="" color="black">'+df[i,2]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,3]+'</td><td><font size="" color="black">'+df[i,4]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,5]+'</td><td><a href='+df[i,0]+'><font size="" color="black">Go To Product Image</a></td>'
                    output+='<td><a href='+url+'><font size="" color="black">Go to Product Page</a></td></tr>'
            if filterValue == 'Average Customer Ratings':
                price = df[i,3]
                price = price.strip()
                price = price.split(" ")
                price = price[0].strip()
                print(price)
                price = float(price)
                if price >= start and price <= end:
                    output+='<tr><td><font size="" color="black">'+df[i,1]+'</td><td><font size="" color="black">'+df[i,2]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,3]+'</td><td><font size="" color="black">'+df[i,4]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,5]+'</td><td><a href='+df[i,0]+'><font size="" color="black">Go To Product Image</a></td>'        
                    output+='<td><a href='+url+'><font size="" color="black">Go to Product Page</a></td></tr>'
        context= {'data':output}
        return render(request, 'ViewResult.html', context)   

def SearchTextProductAction(request):
    if request.method == 'POST':
        category = request.POST.get('t1', False)
        filterValue = request.POST.get('t2', False)
        rangeValue = request.POST.get('t3', False)
        arr = str(rangeValue).split("-")
        start = int(arr[0].strip())
        end = int(arr[1].strip())
        url = 'none'
        if category == 'Electronic Devices':
            url = 'https://www.amazon.in/gp/bestsellers/electronics/'
        if category == 'Home Appliances':
            url = 'https://www.amazon.in/gp/bestsellers/kitchen/1380045031/'
        if category == 'Home Essentials':
            url = 'https://www.amazon.in/Home-Essentials/s?k=Home+Essentials/'
        if category == 'Furniture':
            url = 'https://www.amazon.in/gp/bestsellers/kitchen/5689444031/'    
        if category == 'Decor':
            url = 'https://www.amazon.in/gp/bestsellers/kitchen/1380374031/'
        results = []
        for i in range(1, 3):
            results.append(get_data(i,url))
        flatten = lambda l: [item for sublist in l for item in sublist]
        df = pd.DataFrame(flatten(results),columns=["image",'Book Name','Author','Rating','Customers_Rated', 'Price'])
        df = df.values
        output = '<table border="1" align="center">'
        output+='<tr><th>Product Name</th><th>Description</th><th>Ratings</th><th>Total Customers Rated</th><th>Price</th><th>Product Image URL</th><th>Product URL</th></tr>'
        for i in range(len(df)):
            if filterValue == 'Price Range':
                price = df[i,5]
                price = price.strip()
                price = re.findall('\d+',price)
                value = ''
                for m in range(0,(len(price)-1)):
                    value+=price[m]
                value = value.strip()
                if len(value) == 0:
                    value = 0
                price = float(value)
                if price >= start and price <= end:
                    output+='<tr><td><font size="" color="black">'+df[i,1]+'</td><td><font size="" color="black">'+df[i,2]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,3]+'</td><td><font size="" color="black">'+df[i,4]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,5]+'</td><td><a href='+df[i,0]+'><font size="" color="black">Go To Product Image</a></td>'
                    output+='<td><a href='+url+'><font size="" color="black">Go to Product Page</a></td></tr>'
            if filterValue == 'Average Customer Ratings':
                price = df[i,3]
                price = price.strip()
                price = price.split(" ")
                price = price[0].strip()
                print(price)
                price = float(price)
                if price >= start and price <= end:
                    output+='<tr><td><font size="" color="black">'+df[i,1]+'</td><td><font size="" color="black">'+df[i,2]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,3]+'</td><td><font size="" color="black">'+df[i,4]+'</td>'
                    output+='<td><font size="" color="black">'+df[i,5]+'</td><td><a href='+df[i,0]+'><font size="" color="black">Go To Product Image</a></td>'        
                    output+='<td><a href='+url+'><font size="" color="black">Go to Product Page</a></td></tr>'
        context= {'data':output}
        return render(request, 'ViewResult.html', context)                    
            
            
  
    
def Signup(request):
    if request.method == 'POST':
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      address = request.POST.get('address', False)
      utype = request.POST.get('type', False)
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MLWeb',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO register(username,password,contact,email,address,usertype) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"','"+utype+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Signup Process Completed'}
       return render(request, 'Register.html', context)
      else:
       context= {'data':'Error in signup process'}
       return render(request, 'Register.html', context)    
        
def UserLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        utype = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'MLWeb',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    utype = row[5]
                    break
        if utype == 'User':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        if utype == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)        
        
        
