from csv import writer
import time
import sys
import os
import codecs
import numpy as np
import itertools
import shutil
import requests
import json
import re
import pandas as pd
from multiprocessing import Pool, Value
from skimage import io; io.use_plugin('matplotlib')
from PIL import ImageFile
from sqlalchemy import create_engine, engine
ImageFile.LOAD_TRUNCATED_IMAGES = True
import flickrapi
from sqlalchemy.types import VARCHAR

#SAVE IMAGE FILES?
file_save = False


caffe_root = '' #Root folder for Caffe
sys.path.insert(0, caffe_root + 'python')
import caffe

#polling frequency and number of photos per request to get
NUMBER_OF_POINTS = 5
FREQ = 20


DB_NAME = '' #Name of your SQL Database
TABLE_NAME = '' #Name of your SQL Table

#Flickr Authentication credentials
API_KEY = u''
API_SECRET = u''
flickr = flickrapi.FlickrAPI(API_KEY,API_SECRET,format='parsed-json')



MODEL_FILE_1 = caffe_root + '' #Sceneery model prototext path
PRETRAINED_1 = caffe_root + '' #Sceneery model file path
MEAN_1 = caffe_root + '' #Mean file path

MODEL_FILE_2 = caffe_root + '' #Obeject model prototext path
PRETRAINED_2 = caffe_root + '' #Object model file path
MEAN_2 = caffe_root + '' #Mean file path

#Set to GPU mode if CUDA enabled
caffe.set_mode_cpu()

net_scene = caffe.Classifier(MODEL_FILE_1, PRETRAINED_1,
                       mean=np.load(MEAN_1).mean(1).mean(1),
                       channel_swap=(2,1,0),
                       raw_scale=255,
                       image_dims=(256, 256))
                       
net_object = caffe.Classifier(MODEL_FILE_2, PRETRAINED_2,
                       mean=np.load(MEAN_2).mean(1).mean(1),
                       channel_swap=(2,1,0),
                       raw_scale=255,
                       image_dims=(256, 256))



def get_and_classify(params):
    
    lat,lon,url, pic_id = params
    
    
    
    fname = './Images/Flickr/' + pic_id +'.jpg'
    try:
        im = requests.get(url, stream=True)
        #Filters for stupid accounts like traffic cam and the like.
        if int(im.headers['content-length'])>5000 and abs(float(lat)- 40.683166) > 0.00001 and abs(float(lon) +73.97375) > 0.00001\
        and abs(float(lat)- 49.551483) > 0.00001 and abs(float(lon) -15.364358) > 0.00001:
            

            with open(fname,'a') as f:
                im.raw.decode_content=True
                shutil.copyfileobj(im.raw, f)

                input_image = caffe.io.load_image(fname)
                input_image = caffe.io.resize_image(input_image,(256,256))
                if file_save == False:
                    os.remove(fname)
            
            
            classif_array_scene = net_scene.predict([input_image])[0]
            classif_array_s_top5 = classif_array_scene.argsort()[-5:][::-1]
            classif_array_scene = classif_array_scene[classif_array_s_top5]



            classif_array_object = net_object.predict([input_image])[0]
            classif_array_o_top5 = classif_array_object.argsort()[-5:][::-1]
            classif_array_object = classif_array_object[classif_array_o_top5]

            final = [[lat,lon,url],classif_array_s_top5.tolist(),classif_array_scene.tolist()\
             ,classif_array_o_top5.tolist(), classif_array_object.tolist()]

            final = list(itertools.chain.from_iterable(final))
            
            
            return final
        
        else:
            return None
    except: 
        return None


def getRecent( n_photo,flickr):

	try:
	    photos = flickr.photos.getRecent(per_page=n_photo)
	    
	    urls = np.array([ "https://farm{0}.staticflickr.com/{1}/{2}_{3}.jpg".format(elem['farm'],elem['server'],elem['id'], elem['secret'])\
	 for elem in photos['photos']['photo']])
	    photo_ids = [elem['id'] for elem in photos['photos']['photo']]
	    loc = [flickr.photos.geo.getLocation(photo_id = elem)for elem in photo_ids]
	    loc_array = []
	    for elem in loc:
	        if elem['stat']=='ok':
	            a = elem['photo']['location']
	            loc_array.append([float(a['latitude']),float(a['longitude'])])
	        else:
	            loc_array.append([-1.0,-1.0])
	            
	    loc_array = np.array(loc_array)
	    
	    before_filter = np.array([photo_ids,urls,loc_array[:,0],loc_array[:,1] ]).T
	    
	    return before_filter[before_filter[:,-1]!='-1.0']
	except:
		return np.array([])


def getNewPics(freq,p_numb,db_name,table_name):
    start = time.time()
    
    
    
    while True:
        end = time.time()
        pic_set = set([])
        payload = np.array([])
        if abs(end-start) > freq:
            pic_array = getRecent(p_numb,flickr)
            
            for elem in pic_array:
                pic_id, url, lat, lon = elem
                
                if pic_id not in pic_set:
                    
                    classification = get_and_classify([lat,lon,url,pic_id])

                    if classification != None:
                    	print pic_id
                        payload = np.append(payload,[classification])
            payload = payload.reshape((-1,23))           
            db_loader = pd.DataFrame(payload, columns=('lat','lon','url','scene1','scene2','scene3','scene4','scene5',\
            'sval1','sval2','sval3','sval4','sval5','obj1','obj2','obj3','obj4','obj5',\
            'oval1','oval2','oval3','oval4','oval5'))

            #print db_loader.describe()
            
            
            #db_loader.loc = payload
            
            engine = create_engine('mysql://root:password@localhost:3306/'+db_name+'?charset=utf8')
            connection = engine.connect()
            max_ID_q = connection.execute("select max(ID) from "+TABLE_NAME+";")
            max_ID = -1

            for item in max_ID_q: 
            	max_ID = item[0]

    		indexer = range(max_ID+1, max_ID+1+db_loader.shape[0])
    		db_loader['ID'] = indexer
 
            # Do not insert the row number (index=False)
            db_loader.to_sql(name=table_name, con=engine, if_exists='append', flavor='mysql',dtype={'url': VARCHAR(255)}, index=False, chunksize=5000)
            connection.close()
            if pic_array.shape[0]>0:
            	pic_set = set(pic_array[:,0])
            payload
            
            start = end
    	time.sleep(5)


if __name__ == '__main__':

	getNewPics(FREQ,NUMBER_OF_POINTS,DB_NAME,TABLE_NAME)


