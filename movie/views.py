# coding: utf-8
#-*- coding : utf8 -*-
#coding : utf8

from django.shortcuts import render
import MySQLdb
import json
import re
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import random
from random import shuffle
from django.http import JsonResponse

# PARSE JSON FOR INSERT DATA
class JsonReader:
    valuelist=[]
    columnlist=[]
    def __init__(self,jsonlist=[]):
        self.valuelist=[]
        self.readjson(jsonlist)
    def readjson(self,jsonlist):
        self.columnlist=jsonlist.keys()
        for column in self.columnlist:
            self.valuelist.append(jsonlist[column])


#ENCODE INTO JSON FORMAT AND RESPONSE
class JsonEncoder:
    selects=[]
    selects_list=[]
    def __init__(self,selectall=[],columns=[]):
        self.retrieveList(selectall,columns)
    def retrieveList(self,selectall,columns):
        self.selects=[]
        self.selects_list=[]
        for s in selectall:
            i=0
            select={}
            for col in columns:
                if re.search("list",str(s[i].__class__)) or re.search("bool",str(s[i].__class__)):
                    select[col]=s[i]
                else:
                    select[col]=str(s[i]).decode("utf-8","ignore")
                i+=1
            self.selects_list.append(select)
        self.selects=json.dumps(self.selects_list)

#SQL SCRIPTS
class tableControl:
    columnList=[]
    valueList=[]
    tablename=""
    cursor=""

    def __init__(self,columnList=[],valueList=[],tablename="",cursor=""):
        self.columnList=columnList
        self.valueList=valueList
        self.tablename=tablename
        self.cursor=cursor
    def insert(self):
        variables=["%s"]*len(self.columnList)
        variables=re.sub("'","",str(tuple(variables)))
        columns=re.sub("'|u","",str(tuple(self.columnList)))
        self.cursor.execute(
        "INSERT INTO {0} {1} VALUES {2} ".
        format(self.tablename,columns,variables),
        self.valueList)


# Create your views here.
##############################Genre
@csrf_exempt
def genre(request,GID):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    columns=["MID","NAME","RATE_CAL","RUNTIME","RELEASED","DIRECTOR","DESCRIPTION","IMAGE"]
    if request.method=="GET":
        skip=request.GET.get("skip",0)
        limit=request.GET.get("limit",1)
        if skip==1 and limit ==1 :
            skip=0
            limit=10000
        cursor.execute("call watchmen.get_MoviesByGenre({0},{1},{2})".format(GID,skip,limit))
        movieall=cursor.fetchall()
        db.close()###
        return HttpResponse(JsonEncoder(movieall,columns).selects)

@csrf_exempt
def genres(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    columns=["GID","GNAME",]
    if request.method=="GET":
        cursor.execute("SELECT GID,GNAME FROM genre")
        genreall=cursor.fetchall()
        db.close()###
        return HttpResponse(JsonEncoder(genreall,columns).selects)

##############################Collection

@csrf_exempt
def collection(request,UID):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    movieall=[]
    #print request.META.get('HTTP_TEST')
    columns=["MID","NAME","RATE_CAL","RUNTIME","RELEASED","DIRECTOR","IMAGE"]
    if request.method=="GET":
        cursor.execute("call watchmen.get_Collections({0})".format(UID))
        movieall=cursor.fetchall()
        db.close()###
        return HttpResponse(JsonEncoder(movieall,columns).selects)


@csrf_exempt
def collections_delete(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    if request.method=="POST":
        MID=request.POST.get("MID",-1)
        UID=request.POST.get("UID",-1)
        print MID,UID
        cursor.execute("DELETE FROM Collection WHERE MID={0} AND UID={1}".format(MID,UID))
        db.commit()
        db.close()
        return HttpResponse(200)
@csrf_exempt
def collections(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    if request.method=="POST":
        js=request.POST.get("collectiontable",1)
        jsJson=json.loads(js)
        del jsJson["TIME_COLLECTION"]

        #Read the json code
        Jsonread=JsonReader(jsJson)
        values=Jsonread.valuelist
        columns=Jsonread.columnlist
        print values
        print columns


        #insert into Rate tbale
        COLLECT=tableControl(columns,values,"Collection",cursor)
        try:
            COLLECT.insert()
        except Exception as e:
            if re.search("Duplicate",str(e)) :
                return HttpResponse("collect_duplicate")
            return HttpResponse(e)
        db.commit()


        db.close()###
        return HttpResponse(200)


###############################Rates
@csrf_exempt
def rates(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    if request.method=="POST":
        js=request.POST.get("ratetable",1)
        jsJson=json.loads(js)


        #Read the json code
        jsJson['RATE']=int(re.sub("\s*?min","",jsJson['RATE']))
        Jsonread=JsonReader(jsJson)
        values=Jsonread.valuelist
        columns=Jsonread.columnlist

        #insert into Rate tbale
        RATE=tableControl(columns,values,"Rate",cursor)
        try:
            RATE.insert()
        except Exception as e:
            print e
            return HttpResponse("HasRated")
        db.commit()
        cursor.execute("call Insert_rate({0})".format(jsJson['MID']))
        db.commit()


        db.close()###
        return HttpResponse(200)
##############################Comment
@csrf_exempt
def comment(MID):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    columns=["UID","COMMENT_ID","COMMENT","TIME","UNAME","PROFILE_PICTURE"]
    cursor.execute("call watchmen.get_OneMovieComments({0})".format(MID))
    comments=cursor.fetchall()
    return JsonEncoder(comments,columns).selects_list
@csrf_exempt
def comments(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    if request.method=="POST":
        js=request.POST.get("commenttable",1)
        jsJson=json.loads(js)

        #Read the json code
        Jsonread=JsonReader(jsJson)
        values=Jsonread.valuelist
        columns=Jsonread.columnlist

        #insert into User tbale
        COMMENT=tableControl(columns,values,"Comment",cursor)
        COMMENT.insert()
        db.commit()
        db.close()###
    return HttpResponse(200 )

##############################login
##############################User
@csrf_exempt
def login(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    if request.method=="POST":
        js=request.POST.get("login",1)
        jsJson=json.loads(js)
        ACCOUNT=jsJson['ACCOUNT']
        PASSWORD=jsJson['PASSWORD']
        cursor.execute(
        """SELECT PASSWORD,IDENTITY,UID,PROFILE_PICTURE,RANDOM_ID,NAME
           FROM User WHERE ACCOUNT='{0}'""".format(ACCOUNT))
        user=cursor.fetchall()
        db.close()###
        if PASSWORD == user[0][0]:
            columns=["IDENTITY","UID","PROFILE_PICTURE","token","NAME"]
            values=[[user[0][1],user[0][2],user[0][3],user[0][4],user[0][5]]]

            return HttpResponse(JsonEncoder(values,columns).selects)
        else:
            return HttpResponse("login_error")

@csrf_exempt
def users(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    columns=["UID","NAME","IDENTITY","ACCOUNT","PASSWORD","PROFILE_PICTURE","RANDOM_ID"]
    if request.method=="GET":
        cursor.execute("SELECT * FROM User ORDER BY UID")
        userall=cursor.fetchall()
        db.close()###
        return HttpResponse(JsonEncoder(userall,columns).selects)

    if request.method=="POST":
        js=request.POST.get("usertable",1)
        jsJson=json.loads(js)

        #Read the json code
        Jsonread=JsonReader(jsJson)
        values=Jsonread.valuelist

        columns=Jsonread.columnlist

        columns.append("RANDOM_ID")
        print columns
        print values
        #insert into User tbale

        while True:
            try:
                values.append(str(random.randint(100000,999999)))
                USER=tableControl(columns,values,"User",cursor)
                USER.insert()
                break
            except Exception as e:
                print str(e)
                values.pop()
                if re.search("Duplicate",str(e)):
                    return HttpResponse("account_duplicate")
                print "RANDOMID_error"

        db.commit()

        db.close()###
        return HttpResponse(200)

################################Movie
@csrf_exempt
def movie(request,MID):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    key=request.GET.get('token',-1)
    print key
    if key != -1:
        cursor.execute("SELECT UID FROM User WHERE RANDOM_ID={0}".format(key))
        UID=cursor.fetchall()[0][0]
        cursor.execute("SELECT RATE FROM Rate WHERE UID={0} AND MID={1}".format(UID,MID))
        try:
            rate=cursor.fetchall()[0][0]
        except:#IF GO WRONG it means that the rate isn't exist
            rate=False
        cursor.execute("SELECT UID FROM Collection WHERE UID={0} AND MID={1}".format(UID,MID))
        try:
            collection=cursor.fetchall()[0][0]
            collection=True
        except:
            collection=False
    else:
        rate=False
        collection=False

    #print request.META.get('HTTP_TEST')
    columns=["MID","NAME","RATE_CAL","RUNTIME","RELEASED","DIRECTOR","DESCRIPTION","IMAGE","USER_R","USER_C","GENRE"]
    columns_comment=["UID","COMMENT_ID","COMMENT","TIME","UNAME","PROFILE_PICTURE"]
    if request.method=="GET":
        columns_genre=["GID","GNAME"]
        cursor.execute(
        """SELECT genre.GID,GNAME FROM genre,Genre_Mediator
        WHERE genre.GID=Genre_Mediator.GID AND MID={0}""".format(MID))
        genreall=cursor.fetchall()
        genrelist=JsonEncoder(genreall,columns_genre).selects_list

        cursor.execute("SELECT * FROM Movie WHERE MID={0}".format(MID))
        movieall=list(cursor.fetchall()[0])
        movieall.append(rate)
        movieall.append(collection)
        movieall.append(genrelist)
        movieall=[movieall]
        comments=comment(MID)
        comments_json={}
        comments_json["COMMENTS"]=comments
        All=json.dumps([JsonEncoder(movieall,columns).selects_list[0],comments_json])
        db.close()###

        return HttpResponse(All)


@csrf_exempt
def movies(request):
    db = MySQLdb.connect(host="140.119.19.19", user="adb", passwd="abc123", db="watchmen")
    cursor= db.cursor()
    columns=["MID","NAME","RATE_CAL","DIRECTOR","IMAGE"]
    if request.method=="GET":
        skip=request.GET.get("skip",1)
        limit=request.GET.get("limit",1)
        if skip==1 and limit ==1 :
            skip=0
            limit=50
        #Strored Procedure
        cursor.execute("call watchmen.get_movies({0},{1})".format(skip,limit))
        movieall=cursor.fetchall()#callproc("get_movies",[1,20])
        db.close()###
        return HttpResponse(JsonEncoder(movieall,columns).selects)

    if request.method=="POST":
        js=request.POST.get("movietable",1)
        jsJson=json.loads(js)
        GENRE=jsJson['GENRE']
        jsJson['RUNTIME']=int(re.sub("\s*?min","",jsJson['RUNTIME']))
        del jsJson['GENRE']

        #Read the json code
        Jsonread=JsonReader(jsJson)
        values=Jsonread.valuelist
        columns=Jsonread.columnlist

        #Insert into Movie tbale
        MOVIE=tableControl(columns,values,"Movie",cursor)
        MOVIE.insert()
        db.commit()

        #PUT THE GENRE INTO gere table and Gere_Alternative table
        for gen in  re.split(",",GENRE):
            try:
                cursor.execute("INSERT INTO genre (GNAME) VALUES (%s) ", [gen])
                db.commit()
            except:
                print "DB INSERT Genre : {0}".format(gen)
            gen=re.sub("\s*","",gen)

            cursor.execute("SELECT MAX(MID) FROM Movie")
            row2=cursor.fetchall()
            print gen
            cursor.execute("SELECT GID FROM genre WHERE GNAME = %s",[gen])
            row1=cursor.fetchall()
            cursor.execute("INSERT INTO Genre_Mediator (GID,MID) VALUES (%s,%s) ", (row1[0][0],row2[0][0]))
            db.commit()
        db.close()###
        return HttpResponse("ok")

#def insertMovies(requst):
