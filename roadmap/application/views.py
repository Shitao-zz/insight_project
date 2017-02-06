import os
from application import app
from flask import Flask,render_template, request, redirect
import requests
import pandas as pd
import numpy as np
from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import gensim
from collections import Counter
import re
import io
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

program_languages=['bash','r','python','java','c++','ruby','perl','matlab','javascript','scala','php']
analysis_software=['tableau','sas','spss','d3','saas','scipy','spotfire','splunk']
bigdata_tool=['hadoop','mapreduce','spark','pig','hive','oozie','zookeeper','flume','mahout']
databases=['sql','nosql','hbase','cassandra','mongodb','mysql','mssql','postgresql','rdbms']
overall_dict = program_languages + analysis_software + bigdata_tool + databases


UPLOAD_FOLDER = '/Users/swang/Desktop/insight_project/roadmap/application/resume'
ALLOWED_EXTENSIONS = set(['pdf'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# create a database and query from it
dbname = 'courses_db'
username = 'swang'
pswd = '1118'
engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))
if not database_exists(engine.url):
    create_database(engine.url)

course_data = pd.DataFrame.from_csv('./app_data/udemy_courses_cleaned.csv')
course_data.to_sql('course_data_table', engine, if_exists='replace')
## connect:
con = None
con = psycopg2.connect(database = dbname, user = username, host='localhost',password=pswd)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
       
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    
    # clear and count the key word frequency
    text = re.sub("[^a-zA-Z.+3#]"," ", text)
    text = text.lower().split()  
    text = [w for w in text if w in overall_dict]
    
    return text

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/plotpage', methods=['POST'])
def plotpage():

    f = request.files['file']
    
    if f and allowed_file(f.filename):
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],f.filename))
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],f.filename)
    existSkill = convert(filepath)
    os.remove(filepath)

    topSkill = pd.read_csv('./app_data/top_skills.csv').drop('Unnamed: 0',axis=1)
    for term in existSkill:
        topSkill = topSkill[topSkill.skill != term]
	topSkill = topSkill.reset_index().drop('index',axis=1)

    model = gensim.models.Word2Vec.load('./app_data/W2Vmodel')
    topSkill['similarity'] = 0.0
    for i in range(topSkill.shape[0]):
        topSkill.similarity[i] =  model.n_similarity([topSkill.skill[i]],existSkill)

    courseKey = list(topSkill.iloc[:6]['skill'])
    courseKey1 = list(topSkill.iloc[:6].sort_values('similarity')['skill'])
 
    title_list = []
    fig_list = []
    summary_list = []
    url_list = []

    title_list1 = []
    fig_list1 = []
    summary_list1 = []
    url_list1 = []
    for i in range(len(courseKey)):
        sql_query = "SELECT * FROM course_data_table WHERE (title LIKE '% "+courseKey[i]+" %') ORDER BY num_reviews DESC LIMIT 5;"
	courseSelect = pd.read_sql_query(sql_query,con).iloc[0]
        title_list.append(courseSelect['title'])
	fig_list.append(courseSelect['image'])
	summary_list.append(courseSelect['headline'])
        url_list.append('http://'+courseSelect['homepage'])

    for i in range(len(courseKey1)):
        sql_query = "SELECT * FROM course_data_table WHERE (title LIKE '% "+courseKey1[i]+" %') ORDER BY num_reviews DESC LIMIT 5;"
	courseSelect = pd.read_sql_query(sql_query,con).iloc[0]
        title_list1.append(courseSelect['title'])
	fig_list1.append(courseSelect['image'])
	summary_list1.append(courseSelect['headline'])
        url_list1.append('http://'+courseSelect['homepage'])


    percentTF = list(topSkill.iloc[:6].sort_values('count',ascending=False)['count']*100/4446)
    percentSM = list(topSkill.iloc[:6].sort_values('similarity')['similarity']*100)
    #script, div = make_figure(topSkill)

    skillKey = map(lambda x:x.upper(), courseKey)
    skillKey1 = map(lambda x:x.upper(), courseKey1)
    
    return render_template('plot.html', title = title_list, figs = fig_list, summary = summary_list, skillKey = skillKey, coursepage = url_list, title1 = title_list1, figs1 = fig_list1, summary1 = summary_list1, skillKey1 = skillKey1, coursepage1 = url_list1, percent = percentTF, percentS = percentSM)

