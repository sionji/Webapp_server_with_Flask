#-*- coding : utf-8 -*-

from flask import Flask, render_template, url_for, request, redirect
from subprocess import call, PIPE, Popen
from firebase import firebase
import psutil, datetime 

app = Flask(__name__)

#firebase realtime database
thread = None
firebase = firebase.FirebaseApplication('https://gradeprojectoreo.firebaseio.com/', None)

#raspi cpu temperature
def get_cpu_temperature():
   process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
   output, _error = process.communicate()
   return float(output[output.index('=') + 1 : output.rindex("'")])


@app.route('/')
def basic():
    return 'Hello World!'

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
        action = request.query_string
	#action = request.args.get['action'].text
        if not action :
            return 'TYPE:get/BAD REQUEST'

        return action

    else :
	return request.query_string

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
   firebase.patch('/raspberrypi', {'fire' : action})
   print(action)
   return (''), 204

@app.errorhandler(404)
def page_not_found(error):
    return 'page_not_found_error(404)'

# app run
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

    
