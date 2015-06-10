import sys
import signal
from threading import Thread
from flask import Flask, render_template, request, abort, make_response, Response, jsonify
from bson import json_util
from setproctitle import *
import sqlalchemy as sa
import pandas as pd





setproctitle('Random-Walk')
DATABASE_NAME = 'flicker'
TABLE_NAME = 'photos'


#cats =pd.read_csv('/Users/teej/Downloads/placesCNN/categoryIndex_places205.csv',delimiter=" ",header=0)
cats =pd.read_csv('/root/Caffe-Source/models/placesCNN/categoryIndex_places205.csv',delimiter=" ",header=0)
f = lambda x: ": ".join(x.split('/')[2:])
cats['category']= cats['category'].map(f)

app = Flask(__name__)

#Redis Instance
# red = redis.StrictRedis()

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sys.exit(0)



def database_lookup(category):
    try:
        cat_numb = str(cats[cats['category']==category].values[0,1])

        engine  = sa.create_engine('mysql://root:@127.0.0.1:3306/flickr?charset=utf8')
        connection = engine.connect()
        result = connection.execute("select lat,lon,url,scene1,sval1 from photos where scene1="+cat_numb+\
            " and  sval1>.3")
        return result
    except:
        print 'SQL Lookup Error'
        return None

def send_out(lookup_result):
    points_json = []
    for obj in lookup_result:
        q = dict(obj.items())
        q['scene1'] = cats[cats['number']==q['scene1']].values[0,0]
        points_json.append(q)
    return points_json

    


#Function to publish all tweets in Database
# def publisher_thread():
#     print "Initializing Publisher..."
#     db = Connection().streamer
#     coll = db.tweets
#     cursor = coll.find({},{"_id" : 0, "time": 0},tailable=True,timeout=False)
#     ci=0
#     while cursor.alive:
#         try:
#             doc = cursor.next()
#             ci += 1
#             red.publish('stream', u'%s' % json.dumps(doc,default=json_util.default))
#         except StopIteration:
#             pass


#Function to push all tweets on initial request.            
# def push_all():
#     tw_json =[]
#     print "pushing all tweets"
#     db = Connection().streamer
#     coll = db.tweets
#     cursor = coll.find({},{"_id" : 0, "time": 0})
#     ci=0
#     while cursor.alive:
#         try:
#             ci+=1
#             doc = cursor.next()
#             tw_json.append(doc)
#         except StopIteration:
#             pass
#     print "data returned\n\n"
#     return  tw_json 
        
    
    
    
    
    
#Listener to push tweets from the publish queue via event stream. 
# def event_stream():
#     pubsub = red.pubsub()
#     pubsub.subscribe('stream')
#     i=0
#     for message in pubsub.listen():
#         i+=1
#         yield 'data: %s\n\n' % message['data']
        
        
# Setup Flask and SocketIO




#Set debug equal to True for testing...
#app.debug=True


######################################################################
################### Flask Routing ####################################
######################################################################

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/category/<category>')
def getpoints(category):
    db_res = database_lookup(category)

    return jsonify( points = send_out(db_res))

    

# def runThread():
#     st = Thread( target = publisher_thread )
#     st.start()
    
if __name__=='__main__':
    signal.signal(signal.SIGINT, signal_handler)
    #app.before_first_request(runThread)
    app.run(threaded=True, host='0.0.0.0', port=80,debug=True)
    


    
    










