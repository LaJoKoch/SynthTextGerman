# Author: Ankush Gupta
# Date: 2015

"""
Entry-point for generating synthetic text images, as described in:

@InProceedings{Gupta16,
      author       = "Gupta, A. and Vedaldi, A. and Zisserman, A.",
      title        = "Synthetic Data for Text Localisation in Natural Images",
      booktitle    = "IEEE Conference on Computer Vision and Pattern Recognition",
      year         = "2016",
    }
"""

import numpy as np
import h5py
import os, sys, traceback
import os.path as osp
from synthgen import *
from common import *
import wget, tarfile
import cv2 as cv
import time
import base64
import io
from PIL import Image


## Define some configuration variables:
NUM_IMG = -1 # no. of images to use for generation (-1 to use all available):
INSTANCE_PER_IMAGE = 1 # no. of times to use the same image
SECS_PER_IMG = 5 #max time per image in seconds

# path to the data-file, containing image, depth and segmentation:
DATA_PATH = 'data'
DB_FNAME = osp.join(DATA_PATH,'dset_8000.h5')
# url of the data (google-drive public file):
DATA_URL = 'http://www.robots.ox.ac.uk/~ankush/data.tar.gz'
OUT_FILE = 'results/SynthText_8000.h5'

# adding pre-processed data files into dset_8000.h5 
def add_more_data_into_dset(DB_FNAME,more_img_file_path,more_depth_path,more_seg_path):
  # open files (a:append, r:read, w:write/overwrite)
  db=h5py.File(DB_FNAME,'w')
  depth_db=h5py.File(more_depth_path, 'r')
  seg_db=h5py.File(more_seg_path, 'r')
  db.create_group('image')
  db.create_group('depth')
  db.create_group('seg')

  #print(list(depth_db.keys()))
  #print(list(seg_db.keys()))

  for imname in os.listdir(more_img_file_path):
    if imname.endswith('.jpg'):
      full_path=more_img_file_path + '\\' + imname
      print (full_path,imname)
      print('image size: %d bytes'%os.path.getsize(full_path))

      img_np = np.array(Image.open(full_path))
      
      db['image'].create_dataset(imname,data=img_np)

      # specify exceptions, because not every image has a corresponding depth and segmentation 
      try:
        db['depth'].create_dataset(imname,data=depth_db[imname])
      except KeyError:
        print(imname)
        continue 

      try:
        db['seg'].create_dataset(imname,data=seg_db['mask'][imname])
        db['seg'][imname].attrs['area']=seg_db['mask'][imname].attrs['area']
        db['seg'][imname].attrs['label']=seg_db['mask'][imname].attrs['label']
      except KeyError:
        print(imname)
        continue

  db.close()
  depth_db.close()
  seg_db.close()

# path to the data-file, containing image, depth and segmentation:
DB_FNAME = 'C:\\Users\\mvoe-l\\projects\\SynthText\\data\\dset_8000.h5'

# paths to the downloaded pre-processed data
more_depth_path='C:\\Users\\mvoe-l\\projects\\SynthText\\data\\depth.h5'
more_seg_path='C:\\Users\\mvoe-l\\projects\\SynthText\\data\\seg.h5'
more_img_file_path='C:\\Users\\mvoe-l\\projects\\SynthText\\data\\bg_img'

#add_more_data_into_dset(DB_FNAME,more_img_file_path,more_depth_path,more_seg_path)

def get_data():
  """
  Download the image,depth and segmentation data:
  Returns, the h5 database.
  """
  if not osp.exists(DB_FNAME):
    try:
      colorprint(Color.BLUE,'\tdownloading data (56 M) from: '+DATA_URL,bold=True)
      print()
      sys.stdout.flush()
      out_fname = 'data.tar.gz'
      wget.download(DATA_URL,out=out_fname)
      tar = tarfile.open(out_fname)
      tar.extractall()
      tar.close()
      os.remove(out_fname)
      colorprint(Color.BLUE,'\n\tdata saved at:'+DB_FNAME,bold=True)
      sys.stdout.flush()
    except:
      print (colorize(Color.RED,'Data not found and have problems downloading.',bold=True))
      sys.stdout.flush()
      sys.exit(-1)
  # open the h5 file and return:
  return h5py.File(DB_FNAME,'r')


def add_res_to_db(imgname,res,db):
  """
  Add the synthetically generated text image instance
  and other metadata to the dataset.
  """
  ninstance = len(res)
  for i in range(ninstance):
    print(colorize(Color.GREEN, 'added into the db %s '%res[i]['txt']))

    dname = "%s_%d"%(imgname, i)
    db['data'].create_dataset(dname,data=res[i]['img'])
    db['data'][dname].attrs['charBB'] = res[i]['charBB']
    db['data'][dname].attrs['wordBB'] = res[i]['wordBB']
    #print('type of res[i][\'txt\'] ', type(res[i]['txt']))

    db['data'][dname].attrs['txt'] = res[i]['txt']

    # adding unicode strings of variable length 
    #db['data'][dname].attrs.create('txt', res[i]['txt'], dtype=h5py.vlen_dtype(np.dtype('U')))
    #print('type of db ',type(db['data'][dname].attrs['txt'])) 
    #print(colorize(Color.GREEN,'successfully added'))
    #print(res[i]['txt'])
    #print(res[i]['img'].shape)
    #print('charBB',res[i]['charBB'].shape)
    #print('charBB',res[i]['charBB'])
    #print('wordBB',res[i]['wordBB'].shape)
    #print('wordBB',res[i]['wordBB'])


def main(viz=False):
  # open databases:
  print (colorize(Color.BLUE,'getting data..',bold=True))
  db = get_data()
  print (colorize(Color.BLUE,'\t-> done',bold=True))

  # open the output h5 file:
  out_db = h5py.File(OUT_FILE,'w')
  out_db.create_group('/data')
  print (colorize(Color.GREEN,'Storing the output in: '+OUT_FILE, bold=True))

  # get the names of the image files in the dataset:
  imnames = sorted(db['image'].keys())
  N = len(imnames)
  global NUM_IMG
  if NUM_IMG < 0:
    NUM_IMG = N
  start_idx,end_idx = 0,min(NUM_IMG, N)

  RV3 = RendererV3(DATA_PATH,max_time=SECS_PER_IMG)

  for i in range(start_idx,end_idx):
    t1=time.time() # variable that holds the starting time

    imname = imnames[i]
    print(i, imname)

    if imname in out_db['data'].keys():
        continue

    try:
      # get the image:
      img = Image.fromarray(db['image'][imname][:])
      # get the pre-computed depth:
      #  there are 2 estimates of depth (represented as 2 "channels")
      #  here we are using the second one (in some cases it might be
      #  useful to use the other one):
      depth = db['depth'][imname][:].T
      depth = depth[:,:,1]
      # get segmentation:
      seg = db['seg'][imname][:].astype('float32')
      area = db['seg'][imname].attrs['area']
      label = db['seg'][imname].attrs['label']

      # re-size uniformly:
      sz = depth.shape[:2][::-1]
      img = np.array(img.resize(sz,Image.ANTIALIAS))
      seg = np.array(Image.fromarray(seg).resize(sz,Image.NEAREST))

      print (colorize(Color.RED,'%d of %d'%(i,end_idx-1), bold=True))
      res = RV3.render_text(img,depth,seg,area,label,
                            ninstance=INSTANCE_PER_IMAGE,viz=viz)
      t2=time.time() # endtime 
      print('time consume in each pic', t2-t1)

      if len(res) > 0:
        # non-empty : successful in placing text:
        add_res_to_db(imname,res,out_db)
    
      # visualize the output:
      if viz:
        if 'q' in input(colorize(Color.RED,'continue? (enter to continue, q to exit): ',True)):
          break
    except:
      traceback.print_exc()
      print (colorize(Color.GREEN,'>>>> CONTINUING....', bold=True))
      continue
  db.close()
  out_db.close()


if __name__=='__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Genereate Synthetic Scene-Text Images')
  parser.add_argument('--viz',action='store_true',dest='viz',default=False,help='flag for turning on visualizations')
  args = parser.parse_args()
  main(args.viz)
