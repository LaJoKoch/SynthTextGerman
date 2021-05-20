"""
Download the pre-processed data from: https://github.com/ankush-me/SynthText#pre-generated-dataset
Then merge the three files containing depth, segmentation and images into one h5 file.
reference: https://github.com/JarveeLee/SynthText_Chinese_version/blob/master/add_more_data.py
"""

import numpy as np
import h5py
import os, sys
import wget, tarfile
from common import *
import os.path as osp
from PIL import Image

DATA_PATH = 'data'
# path to the data-file, containing image, depth and segmentation:
DB_FNAME = osp.join(DATA_PATH, 'dset_8000.h5')

# paths to the downloaded pre-processed data
more_depth_path = osp.join(DATA_PATH,'depth.h5')
more_seg_path = osp.join(DATA_PATH,'seg.h5')
more_img_file_path = osp.join(DATA_PATH, 'bg_img')

# url of the pe-processed data
URL_IMG = 'http://thor.robots.ox.ac.uk/~vgg/data/scenetext/preproc/bg_img.tar.gz'
URL_DEPTH = 'http://thor.robots.ox.ac.uk/~vgg/data/scenetext/preproc/depth.h5'
URL_SEG = 'http://thor.robots.ox.ac.uk/~vgg/data/scenetext/preproc/seg.h5'

# download the pre-processed data: background image, depth and segmentation
def download_preproc():
  if not osp.exists(more_img_file_path):
    try:
      colorprint(Color.BLUE,'\tdownloading image-data (8.9G) from: '+URL_IMG,bold=True)
      print()
      sys.stdout.flush()
      out_fname = 'bg_img.tar.gz'
      wget.download(URL_IMG,out=out_fname)
      tar = tarfile.open(out_fname)
      tar.extractall()
      tar.close()
      os.remove(out_fname)
      colorprint(Color.BLUE,'\n\tdata saved at:'+more_img_file_path,bold=True)
      sys.stdout.flush()
    except:
      print (colorize(Color.RED,'Image-Data not found and have problems downloading.',bold=True))
      sys.stdout.flush()
      sys.exit(-1)
  elif not osp.exists(more_seg_path):
    try: 
      colorprint(Color.BLUE,'\tdownloading segmentation-data (6.9G) from: '+URL_SEG,bold=True)
      print()
      sys.stdout.flush()
      out_fname = 'seg.h5'
      wget.download(URL_SEG,out=out_fname)
      colorprint(Color.BLUE,'\n\tdata saved at:'+more_seg_path,bold=True)
      sys.stdout.flush()
    except:
      print (colorize(Color.RED,'Segmentation-Data not found and have problems downloading.',bold=True))
      sys.stdout.flush()
      sys.exit(-1)
  elif not osp.exists(more_depth_path):
    try: 
      colorprint(Color.BLUE,'\tdownloading depth-data (15G) from: '+URL_DEPTH,bold=True)
      print()
      sys.stdout.flush()
      out_fname = 'depth.h5'
      wget.download(URL_DEPTH,out=out_fname)
      colorprint(Color.BLUE,'\n\tdata saved at:'+more_depth_path,bold=True)
      sys.stdout.flush()
    except:
      print (colorize(Color.RED,'Depth-Data not found and have problems downloading.',bold=True))
      sys.stdout.flush()
      sys.exit(-1)


# add/merge pre-processed data files into dset_8000.h5 
def add_more_data_into_dset(DB_FNAME,more_img_file_path,more_depth_path,more_seg_path):
  print (colorize(Color.GREEN,'adding data into h5 file..',bold=True))
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
  print (colorize(Color.GREEN,'\t-> done',bold=True))
  print (colorize(Color.GREEN,'Stored the data in: '+DB_FNAME, bold=True))

  db.close()
  depth_db.close()
  seg_db.close()


if __name__ == '__main__':
  download_preproc()
  add_more_data_into_dset(DB_FNAME,more_img_file_path,more_depth_path,more_seg_path)