# Author: Xinshuo Weng
# email: xinshuo.weng@gmail.com

import yaml, numpy as np, os
from easydict import EasyDict as edict
# from AB3DMOT_libs.model_multi import AB3DMOT_multi
from AB3DMOT_libs.model import AB3DMOT
from AB3DMOT_libs.kitti_oxts import load_oxts
from AB3DMOT_libs.kitti_calib import Calibration
from AB3DMOT_libs.nuScenes_split import get_split
from xinshuo_io import mkdir_if_missing, is_path_exists

def Config(filename):
    listfile1 = open(filename, 'r')
    listfile2 = open(filename, 'r')
    cfg = edict(yaml.safe_load(listfile1))
    settings_show = listfile2.read().splitlines()

    listfile1.close()
    listfile2.close()

    return cfg, settings_show

def get_subfolder_seq(dataset, split):

	# dataset setting
	if dataset == 'KITTI':				# KITTI
		det_id2str = {1: 'Pedestrian', 2: 'Car', 3: 'Cyclist'}
		
		if split == 'val': subfolder = 'training' 
		elif split == 'test': subfolder = 'testing' 
		else: assert False, 'error'
		
		hw = (720, 1920)
		
		if split == 'train': seq_eval = ['0000', '0002', '0003', '0004', '0005', '0007', '0009', '0011', '0017', '0020']         # train
		if split == 'val':   seq_eval = ['0001', '0006', '0008', '0010', '0012', '0013', '0014', '0015', '0016', '0018', '0019']    # val
		if split == 'test':  seq_eval  = ['%04d' % i for i in range(29)]
	
	elif dataset == 'nuScenes':			# nuScenes
		det_id2str = {1: 'Pedestrian', 2: 'Car', 3: 'Bicycle', 4: 'Motorcycle', 5: 'Bus', 6: 'Trailer', 7: 'Truck'}
		
		subfolder = split
		hw = (900, 1600)
		
		if split == 'train': seq_eval = get_split()[0]		# 700 scenes
		if split == 'val':   seq_eval = get_split()[1]		# 150 scenes
		if split == 'test':  seq_eval = get_split()[2]      # 150 scenes
	else: assert False, 'error'
		
	return subfolder, det_id2str, hw, seq_eval

def initialize(cfg, data_root, save_dir, subfolder, seq_name, cat, ID_start, hw, log_file):
	# initialize the tracker and provide all path of data needed

	oxts_dir  = os.path.join(data_root, subfolder, 'oxts')
	calib_dir = os.path.join(data_root, subfolder, 'calib')
	image_dir = os.path.join(data_root, subfolder, 'image_02')

	# load ego poses
	oxts = os.path.join(data_root, subfolder, 'oxts', seq_name+'.json')
	if not is_path_exists(oxts): oxts = os.path.join(data_root, subfolder, 'oxts', seq_name+'.txt')
	imu_poses = load_oxts(oxts)                 # seq_frames x 4 x 4

	# load calibration
	calib = os.path.join(data_root, subfolder, 'calib', seq_name+'.txt')
	calib = Calibration(calib)

	# load image for visualization
	img_seq = os.path.join(data_root, subfolder, 'image_02', seq_name)
	vis_dir = os.path.join(save_dir, 'vis_debug', seq_name); mkdir_if_missing(vis_dir)

	# initiate the tracker
	if cfg.hypothesis > 1:
		tracker = AB3DMOT_multi(cfg, cat, calib=calib, oxts=imu_poses, img_dir=img_seq, vis_dir=vis_dir, hw=hw, log=log_file, ID_init=ID_start) 
	elif cfg.hypothesis == 1:
		tracker = AB3DMOT(cfg, cat, calib=calib, oxts=imu_poses, img_dir=img_seq, vis_dir=vis_dir, hw=hw, log=log_file, ID_init=ID_start) 
	else: assert False, 'error'
	
	return tracker