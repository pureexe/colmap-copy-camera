from database import COLMAPDatabase, blob_to_array, array_to_blob
from read_write_model import read_cameras_binary, read_images_binary
import argparse
import numpy as np

def copy_camera(args):
    cameras = read_cameras_binary('penguinguy/cameras.bin')
    destionation_db = COLMAPDatabase.connect(args.destionation) 
    destionation_db.execute('DELETE FROM cameras')
    for i in cameras:
        cam_id, model, width, height, params = cameras[i]
        known_focal = params[0]
        destionation_db.add_camera(model, width, height, params[:-1], prior_focal_length=known_focal, camera_id=cam_id)
    destionation_db.commit()
    destionation_db.close()

def copy_images(args):
    destionation_db = COLMAPDatabase.connect(args.destionation) 
    images = read_images_binary('penguinguy/images.bin')
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

"""
    source_db = COLMAPDatabase.connect(args.source) 
    cursor = source_db.cursor()
    cursor.execute('SELECT F FROM two_view_geometries ORDER BY pair_id')
    source_data = cursor.fetchall()
    source_db.close()

    destionation_db = COLMAPDatabase.connect(args.destionation) 
    cursor = destionation_db.cursor()
    cursor.execute('SELECT F FROM two_view_geometries ORDER BY pair_id')
    destionation_data = cursor.fetchall()
    destionation_db.close()
    
    for i in range(38,len(source_data)):
        print(source_data[i][0])
        s = blob_to_array(source_data[i][0],np.float64)
        d = blob_to_array(destionation_data[i][0],np.float64)
        if not np.array_equal(s,d):
            print(s)
            print(d)
            print('YES! %d' % i)

    #print(len(data))
    #print(blob_to_array(data[1][0],np.float64).reshape((3,3)))
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='copy.py - Colmap camera intrisic & Extrinsic copyer')
    parser.add_argument('-s', '--source', default='sfm.db', type=str,
        help='database file that already do structure from motion to be source file')
    parser.add_argument('-d', '--destionation', default='pen_matched_400img.db', type=str,
        help='database file from feature mapping to set intrisic and extrinsic')
    main(parser.parse_args())
