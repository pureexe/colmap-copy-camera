from database import COLMAPDatabase, blob_to_array, array_to_blob
from read_write_model import read_cameras_binary, read_images_binary
import argparse, os
import numpy as np

def copy_camera(args):
    cameras = read_cameras_binary(os.path.join(args.source,'cameras.bin'))
    destionation_db = COLMAPDatabase.connect(args.destionation) 
    c = destionation_db.cursor()
    c.execute('SELECT * FROM cameras')
    destionation_db.execute('DELETE FROM cameras')
    for i in cameras:
        cam_id, model, width, height, params = cameras[i]
        known_focal = params[0]
        destionation_db.add_camera(model, width, height, params[:-1], prior_focal_length=known_focal, camera_id=cam_id)
    destionation_db.commit()
    destionation_db.close()

def copy_images(args):
    destionation_db = COLMAPDatabase.connect(args.destionation) 
    images = read_images_binary(os.path.join(args.source,'images.bin'))
    destionation_db.execute('DELETE FROM images')
    for i in images:
        img_id, qvec, tvec, cam_id, name, xys, point3D_ids = images[i]
        destionation_db.add_image( name, cam_id, prior_q=qvec, prior_t=tvec, image_id=img_id)
    destionation_db.commit()
    destionation_db.close()

def main(args):
    copy_camera(args)
    copy_images(args)
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='colmap_copy.py - Colmap camera intrisic & Extrinsic copyer')
    parser.add_argument('-s', '--source', default='penguinguy', type=str,
        help='sparse model directory that already do structure from motion to be source file')
    parser.add_argument('-d', '--destionation', default='pen_matched_400img.db', type=str,
        help='database file from feature mapping to set intrisic and extrinsic')
    main(parser.parse_args())
