# Random-Walk
Random Walk is a web application to allow users to identify and explore regions with specific scenery via Flickr photos. Photographs are analyzed using a deep learning model based on the AlexNet structure and trained on the MIT Places205 image set (2.5 million images). 

## Setup
The primary dependencies for the web server itself are Flask and [Caffe](http://caffe.berkeleyvision.org). Also, if you want to take advantage of the pretrained Places model see the [Caffe Model Zoo](https://github.com/BVLC/caffe/wiki/Model-Zoo). 

Download and compile pycaffe using the [installation instructions](http://caffe.berkeleyvision.org/installation.html), then edit the `Random-Walk.py` file to point to your SQL database. 

Finally, run the Flask web server via
```
sudo python Random-Walk.py
```

## Database Generation
The `imclass_remote.py` file is meant to work with csv files from the [Flickr 100M](http://labs.yahoo.com/news/yfcc100m/) photo set. After downloading and extracting the files the images can be classified via 
```python imclass_remote.py PATH_TO_CLASSIFICATION_CSV PATH_TO_PHOTOSET_CSV NUMBER_OF_POINTS```

Then the fileset is added to your MySQL database with
```python database_entry PATH_TO_CLASSIFICATION_CSV```
