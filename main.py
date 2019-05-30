#-*- coding : utf-8 -*-

from flask import Flask, render_template, url_for, request, redirect
from subprocess import call, PIPE, Popen
from firebase import firebase
from pyfcm import FCMNotification
import psutil, datetime
import json
import pymysql

app = Flask(__name__)

def mySQL(sqltype,tablename,where):
    # MySQL Connection, Access databse
    db = pymysql.connect(host='localhost', user='pi', password='flytothemoon', db='flytothemoon', charset='utf8')

    # Make Cursor from Connection
    cursor = db.cursor()

    # Write SQL Query
    if (sqltype == 'select') :
	sql = "select * from "+tablename
        print(sql)
	cursor.execute(sql)
	rows = cursor.fetchall()
        print(rows)
        db.close()
        return "OK"

    elif (sqltype == 'insert') :
        sql = "INSERT INTO "+tablename+" (place) VALUES ('"+where+"')"
        print(sql)
        cursor.execute(sql)
        db.commit()
        print("insert values")
        print("last index : "+cursor.lastrowid)
        db.close()
        return "OK"

    elif (sqltype == 'update') :
        print("update")

    elif (sqltype == 'delete') :
        print("delete")


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

@app.route('/arduino/test', methods=['GET'])
def arduino_test( action = None ):
    action = request.args.get("action")
    if ( action == 'fire' ) :
        return 'Fire occured !! '
    elif ( action == 'open' ) :
        return 'Open the door'
    elif ( action == 'close' ) :
        return 'Close the door'
    else :
        return 'You know nothing...'
 
@app.route('/test/<string:text>/')
def testCall(text):
    return 'test call : ' + text

@app.route('/arduino', methods=['POST', 'GET'])
def arduino( action = None ):
    error = None
    if request.method == 'POST' :
        action = request.form['action']
        if not action :
            return 'TYPE:post/BAD REQUEST'

        return action

    elif request.method == 'GET' :
        action = request.args.get("action")
	sqltype = request.args.get("sqltype")
	tablename = request.args.get("tablename")
        where = request.args.get("where")

        #action = request.args.get['action'].text
        if not action :
            return 'TYPE:get/BAD REQUEST'
		
        result = mySQL(sqltype=sqltype, tablename=tablename, where=where)
        if (sqltype == 'select') :
            #return render_template('mysqlselect.html', mysql_select = result,title = "MariaDB Database",tablename = tablename)
            return result
        elif (sqltype == 'insert'):
            return result

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

    message_title = request.args.get("title")
    message_body = request.args.get("body")
    data_message = {
            "message_title" : message_title,
            "message_body" : message_body,
            }
    result = duckbase.get("/users", None)
    listToken = []
    for k, v in result.items():
        listToken.append(v["token"])
    push_service = FCMNotification(api_key="AAAAKZIq-gg:APA91bFAQi1T8kZRPMiTFol8NG7undfjGOMjw5ebh5QaF3cLbAZQ_XfxSMEo1nF-uThG7sARbtWoZChtoRjWlxhKFLsGcCYY2TT2h8dkX3VnZGFKP9KlfwOBH1ritnBGabzDftMt2Pv9")
    result = push_service.multiple_devices_data_message(registration_ids=listToken, data_message=data_message)
    print(result)


    duckbase.patch('/raspberrypi', {'fire' : action})
    # patch can change a single data
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

    
