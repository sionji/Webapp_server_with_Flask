#-*- coding : utf-8 -*-

from flask import Flask, render_template, url_for, request, redirect
from subprocess import call, PIPE, Popen
from firebase import firebase
from pyfcm import FCMNotification
import psutil, datetime
import json
import pymysql

app = Flask(__name__)

# fire status global variable
fire_pistatus = 0

def mySQL(sqltype,tablename,where):
    # MySQL Connection, Access databse
    db = pymysql.connect(host='localhost', user='pi', password='flytothemoon', db='flytothemoon', charset='utf8', use_unicode=True)

    # Make Cursor from Connection
    cursor = db.cursor()

    # Write SQL Query
    if (sqltype == 'select') :
        try :
            sql = "select * from "+tablename
            print(sql)
	    cursor.execute(sql)
	    rows = cursor.fetchall()
            return rows
        finally :
            db.close()

    elif (sqltype == 'insert') :
        try :
            sql = "INSERT INTO "+tablename+" (place) VALUES ('"+where+"')"
            print(sql)
            cursor.execute(sql)
            db.commit()
            return cursor.lastrowid
        finally :
            db.close()

    elif (sqltype == 'update') :
        print("update")

    elif (sqltype == 'delete') :
        print("delete")

def fcm_datapush(title, body) : 
    data_message = {
            "message_title" : title,
            "message_body" : body,
            "message_channel" : "EMERGENCY"
            }
    listToken = []
    usertokens = duckbase.get("/users", None)
    for k, v in usertokens.items():
        listToken.append(v["token"])
    push_service = FCMNotification(api_key="AAAAKZIq-gg:APA91bFAQi1T8kZRPMiTFol8NG7undfjGOMjw5ebh5QaF3cLbAZQ_XfxSMEo1nF-uThG7sARbtWoZChtoRjWlxhKFLsGcCYY2TT2h8dkX3VnZGFKP9KlfwOBH1ritnBGabzDftMt2Pv9")
    result = push_service.multiple_devices_data_message(registration_ids=listToken, data_message=data_message)
    return result

#firebase realtime database
thread = None
duckbase = firebase.FirebaseApplication('https://gradeprojectoreo.firebaseio.com/', None)
sionbase = firebase.FirebaseApplication('https://graduate-project-c0c01.firebaseio.com/', None)

#raspi cpu temperature
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1 : output.rindex("'")])


@app.route('/')
def basic():
    return 'Fly to the Moon Graduate Project'

@app.route('/fire/<int:input_pistatus>')
def fire_occurs(input_pistatus):
    global fire_pistatus
    # fire_pistatus and input_pistatus is int type data
    if (fire_pistatus == 0 and input_pistatus == 1) :
        fire_pistatus = input_pistatus
        message = fcm_datapush('Fire Occured!', 'Touch to see evacuation route.')
        print(message)
        return 'Global variable is %d' % fire_pistatus
    
    else :
        return 'Global variable is %d' % fire_pistatus

@app.route('/fire/reset', methods=['GET'])
def fire_reset():
    global fire_pistatus
    fire_pistatus = 0
    return 'Global variable reset to %d' %fire_pistatus

@app.route('/test/<string:text>/')
def testCall(text):
    return 'test call : ' + text

@app.route('/arduino', methods=['GET'])
def arduino():
    global fire_pistatus
    if (fire_pistatus == 1) :
        # if fire_pistatus is int 1, then return string 1
        return 'y'

    elif request.method == 'GET' :
	sqltype = request.args.get("sqltype")
	tablename = request.args.get("tablename")
        where = request.args.get("where")
	
        if ( sqltype == 'insert' ) :
            mySQL(sqltype=sqltype, tablename=tablename, where=where)
        return 'n'

    else :
        return "Check your request..."

@app.route('/arduino/web', methods=['GET'])
def arduino_web():
    global fire_pistatus
    if (fire_pistatus == 1) :
        # if fire_pistatus is int 1, then return string 1
        return '1'

    elif request.method == 'GET' :
	sqltype = request.args.get("sqltype")
	tablename = request.args.get("tablename")
        where = request.args.get("where")
		
        result = mySQL(sqltype=sqltype, tablename=tablename, where=where)

        if (sqltype == 'select') :
            return render_template('selectdb.html', result=result) 
        elif (sqltype == 'insert'):
            selectedrows = mySQL(sqltype="select", tablename=tablename, where=where)
            return render_template('insertdb.html', result=selectedrows, lastrowid=result)

    else :
        return "Check your request..."

    return action

@app.route('/pi')
def pi():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    cpu_temperature = get_cpu_temperature()
    cpu_percent = psutil.cpu_percent()
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory()
    mem_total = mem.total
    mem_percent = mem.percent
    disk = psutil.disk_usage("/")
    disk_percent = disk.percent

    raspi_dict = {'CPU Temp (C)' : cpu_temperature,
            'CPU Usage (%) ' : cpu_percent,
            'CPU Core' : cpu_count,
            'Total Memory' : mem_total,
            'RAM Usage (%)' : mem_percent,
            'Disk Usage (%)' : disk_percent,
            }
    return render_template('hello.html', raspi_info = raspi_dict,
          title = 'Raspi Status',
          time = timeString)
    
@app.route('/firebase', methods=['GET'])
def firebase_database():
    action = request.args.get("action")
    duckbase.patch('/raspberrypi', {'fire' : action})
    
    message_title = request.args.get("title")
    message_body = request.args.get("body")
    result = fcm_datapush(message_title, message_body) 
    print(result)


    # firebase patch query can change a single data
    # data = { 'deeplearning' : action }
    # sionbase.put('','put', data)
    # fb.put takes three arguments : first is url or path,
    # second is the keyname or the snapshot name and
    # third is the data(json)

    print(action)
    return (''), 204

@app.errorhandler(404)
def page_not_found(error):
    return 'page_not_found_error(404)'

# app run
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

    
