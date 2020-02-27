from database import COLMAPDatabase, blob_to_array, array_to_blob
from read_write_model import read_cameras_binary, read_images_binary
import argparse, os
import numpy as np

def main(args):
    destionation_db = COLMAPDatabase.connect(args.destionation) 
    c = destionation_db.cursor()
    images = read_images_binary(os.path.join(args.source,'images.bin'))
    cameras = read_cameras_binary(os.path.join(args.source,'cameras.bin'))
    lookup_image = dict([(images[i][4],images[i][0]) for i in images])
    c.execute('SELECT image_id,name,camera_id FROM images')
    image_list = c.fetchall()
    image_reorder = []
    camera_lookup = {}
    camera_reorder = []
    #image reorder
    for db_img in image_list:
        img_id, qvec, tvec, cam_id, name, xys, point3D_ids = images[lookup_image[db_img[1]]]
        new_image = [img_id, qvec, tvec, cam_id, name, xys, point3D_ids]
        new_image[0] = db_img[0]
        if new_image[3] != db_img[2]:
            camera_lookup[new_image[3]] = db_img[2]
            new_image[3] = db_img[2]
        image_reorder.append(new_image)
    #camera reorder
    for i in cameras:
        cam_id, model, width, height, params = cameras[i]
        new_camera = [cam_id, model, width, height, params]
        if i in camera_lookup:
            new_camera[0] = camera_lookup[i]
        camera_reorder.append(new_camera)
    destionation_db.execute('DELETE FROM images')
    destionation_db.execute('DELETE FROM cameras')
    for i in range(len(image_reorder)):
        img_id, qvec, tvec, cam_id, name, xys, point3D_ids = image_reorder[i]
        destionation_db.add_image( name, cam_id, prior_q=qvec, prior_t=tvec, image_id=img_id)
    for i in range(len(camera_reorder)):
        cam_id, model, width, height, params = camera_reorder[i]
        known_focal = params[0]
        destionation_db.add_camera(model, width, height, params[:-1], prior_focal_length=known_focal, camera_id=cam_id)
    destionation_db.commit()
    destionation_db.close()
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='colmap_copy.py - Colmap camera intrisic & Extrinsic copyer')
    parser.add_argument('-s', '--source', default='penguinguy', type=str,
        help='sparse model directory that already do structure from motion to be source file')
    parser.add_argument('-d', '--destionation', default='pen_matched_400img.db', type=str,
        help='database file from feature mapping to set intrisic and extrinsic')
    main(parser.parse_args())
