from csv import writer
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
ImageFile.LOAD_TRUNCATED_IMAGES = True

file_save = False


caffe_root = '' #Root folder for Caffe
sys.path.insert(0, caffe_root + 'python')
import caffe

#Optional last argument to limit number of lines in csv file (if restricted memory is an issue)
if sys.argv[3]=='None':
    NUMBER_OF_POINTS = None
else: 
    NUMBER_OF_POINTS = int(sys.argv[3])


#path for Flickr 100M csv data file
PATH_TO_DATASET = sys.argv[2]#'./yfcc100m_dataset-0'


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




name_list = ['Photo/video identifier','NSID','nickname','Date_taken','Date_uploaded','device','Title',\
             'Description','user_tags','machine_tags','Longitude','Latitude','Accuracy','page_URL','download_URL',\
             'License_name','License URL','server_ID','farm_ID','secret','secret_orig','extension','pv_marker']
             
photo = pd.read_csv(PATH_TO_DATASET,nrows=NUMBER_OF_POINTS,sep='\t',header=None,names =name_list )

pnew = photo[['Latitude','Longitude', 'download_URL','pv_marker']][photo['Latitude'].notnull()]

pnew = pnew[['Latitude','Longitude', 'download_URL']][pnew['pv_marker']==0]

search = re.compile('[a-zA-Z0-9_]{3,10}_[a-zA-Z0-9_]{3,10}')

def init(count):
     global counter
     counter = count
     
def get_and_classify(params):
    
    lat,lon,url = params
    
    global counter
    counter.value += 1
    sys.stdout.flush()
    sys.stdout.write("\r{0}".format(counter.value))
    sys.stdout.flush()
    
    m = search.search(url)
    
    fname = './Images/Flickr/' + m.group(0) +'.jpg'
    try:
        im = requests.get(url, stream=True)
        if int(im.headers['content-length'])>5000:
            

            with open(fname,'a') as f:
                im.raw.decode_content=True
                shutil.copyfileobj(im.raw, f)

                input_image = caffe.io.load_image(fname)
                #input_image = caffe.io.resize_image(input_image,(256,256))
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


#Multiprocessing Handler        
            
def mp_handler():    
    counter = Value('i', 0)
    pool = Pool(initializer = init, initargs= (counter, ),processes=4)              # process per core
    #pool.map(calculate_inflation, val_array)
    with open(filename,'a') as f:
        out = writer(f)
        for results in pool.imap(get_and_classify, pnew.values):
                if results != None:
                    out.writerow(results)
                
    print "\nFinished all %i classifications out of %i processed" % (counter.value,NUMBER_OF_POINTS)
    print "Written in File: %s" % filename   
                
                
    
    
    
if __name__ == '__main__':
    #b,c,w,R,t0 
    filename =  sys.argv[1]
    DATA_PATH = os.path.dirname(filename)
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)

       


    
    with open(filename,'wb') as f:
        out = writer(f)
        out.writerow(['lat','lon','url','scene1','scene2','scene3','scene4','scene5',\
            'sval1','sval2','sval3','sval4','sval5','obj1','obj2','obj3','obj4','obj5',\
            'oval1','oval2','oval3','oval4','oval5'])

    #f= open(filename,'a')
    #out = writer(f)
    mp_handler()
    
    
    
    
    