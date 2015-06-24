import sys
import signal
from threading import Thread
from flask import Flask, render_template, request, abort, make_response, Response, jsonify
from bson import json_util
from setproctitle import *
import sqlalchemy as sa
import pandas as pd
import random


boundarray = [ 0.32123219,  0.39830334,  0.45917859,  0.42660938,  0.38771624,
        0.4537306 ,  0.38206535,  0.31845475,  0.36430404,  0.25287483,
        0.34902882,  0.35471008,  0.44384717,  0.19425869,  0.35241491,
        0.4546636 ,  0.43941404,  0.33114138,  0.41369366,  0.53249488,
        0.28380106,  0.27860754,  0.3000111 ,  0.30042944,  0.30163271,
        0.36991524,  0.36575366,  0.41326117,  0.35871493,  0.43572577,
        0.4057421 ,  0.30926022,  0.236724  ,  0.54507127,  0.35813167,
        0.38102455,  0.37764518,  0.26237418,  0.38612264,  0.2881096 ,
        0.38157414,  0.31150652,  0.51278862,  0.31643468,  0.31604852,
        0.32620508,  0.29902008,  0.25854587,  0.43877977,  0.30259866,
        0.41577164,  0.36492908,  0.31516731,  0.39268372,  0.51651848,
        0.32000064,  0.36331108,  0.29836331,  0.32730662,  0.33482509,
        0.44735805,  0.30080917,  0.23312869,  0.36192315,  0.31353737,
        0.35411701,  0.23600386,  0.33757391,  0.46296709,  0.34121517,
        0.19910024,  0.36820156,  0.35928085,  0.31905497,  0.38318565,
        0.37099592,  0.43026242,  0.2886674 ,  0.42189399,  0.42019057,
        0.32051683,  0.38838321,  0.28513178,  0.35600416,  0.30124224,
        0.3420976 ,  0.33636067,  0.3705828 ,  0.22419021,  0.3103291 ,
        0.36686152,  0.29250963,  0.48930005,  0.30707803,  0.23682102,
        0.28953369,  0.36661086,  0.41444653,  0.17959471,  0.25881627,
        0.54106869,  0.38210532,  0.38491174,  0.71287014,  0.15788126,
        0.37135856,  0.40699786,  0.29843758,  0.3280706 ,  0.31433914,
        0.36146877,  0.52436607,  0.25440191,  0.28156315,  0.33295386,
        0.28653898,  0.33418558,  0.42151469,  0.3517384 ,  0.33525583,
        0.35004198,  0.25453092,  0.32187781,  0.42794544,  0.3715075 ,
        0.1771779 ,  0.26092702,  0.27839933,  0.38504961,  0.3008126 ,
        0.25709869,  0.35491691,  0.41465351,  0.2615035 ,  0.46731483,
        0.46988073,  0.29407715,  0.38430432,  0.24425163,  0.33989925,
        0.38602199,  0.27105842,  0.36975171,  0.3356947 ,  0.29899131,
        0.427571  ,  0.51788916,  0.44951466,  0.39356585,  0.36439674,
        0.26742971,  0.25551044,  0.35201715,  0.27832718,  0.26474895,
        0.39674158,  0.20057134,  0.40314698,  0.32152241,  0.32251481,
        0.7005793 ,  0.32659033,  0.36903805,  0.44043124,  0.37619567,
        0.26611351,  0.33441713,  0.37142703,  0.32747486,  0.36805246,
        0.54371176,  0.39479857,  0.3217335 ,  0.36265054,  0.39174094,
        0.37768692,  0.32706581,  0.49858319,  0.70680496,  0.38400332,
        0.3867914 ,  0.48905711,  0.27634555,  0.38944146,  0.31926371,
        0.44867706,  0.25885832,  0.27855626,  0.29590959,  0.29334505,
        0.61433217,  0.41676176,  0.61286827,  0.25917222,  0.31403825,
        0.27545707,  0.32324647,  0.41412418,  0.19903402,  0.43076636,
        0.29325771,  0.3538182 ,  0.44366133,  0.47372824,  0.24468869]


setproctitle('Random-Walk')
DATABASE_NAME = '' #SQL Database
TABLE_NAME = '' #SQL Table
MODEL_CAT_LABELS = '' #Path to scene category file.


#cats =pd.read_csv('/Users/teej/Downloads/placesCNN/categoryIndex_places205.csv',delimiter=" ",header=0)
cats =pd.read_csv(MODEL_CAT_LABELS,delimiter=" ",header=0)
f = lambda x: ": ".join(x.split('/')[2:])
cats['category']= cats['category'].map(f)

app = Flask(__name__)



def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sys.exit(0)



def database_lookup(category):
    try:
        cat_numb = cats[cats['category']==category].values[0,1]
        lb = str(boundarray[cat_numb])
        engine  = sa.create_engine('mysql://root:password@127.0.0.1:3306/flickr?charset=utf8') #set password to your own
        connection = engine.connect()
        
        result = connection.execute("select lat,lon,url,scene1,sval1 from "+TABLE_NAME+" where scene1="+str(cat_numb)+\
            " and  sval1>"+lb)
        connection.close()
        return result
    except:
        print 'SQL Lookup Error'
        return None

def init_pics(number):
    try:
        numb= str(number)

        
        engine  = sa.create_engine('mysql://root:password@127.0.0.1:3306/flickr?charset=utf8')
        connection = engine.connect()
        result = connection.execute("select lat,lon,url,scene1,sval1 from "+TABLE_NAME+" where sval1>.5 order by ID DESC limit "+numb+";")
        
        

        final =  send_out(result)
        connection.close()
        return final
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

@app.route('/init/<number>')
def getpics(number):

    package = init_pics(number)
    #random.shuffle(package) #uncomment if you want to randomly shuffle recent Flickr images

    return jsonify( points = package)

    

    
if __name__=='__main__':
    signal.signal(signal.SIGINT, signal_handler)
    app.run(threaded=True, host='0.0.0.0', port=80,debug=True)
    


    
    










