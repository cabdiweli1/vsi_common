""" A collection of GPGPU image processing utility functions """
#from PIL import Image
import numpy as np
import pyopencl as cl
import os


def NCC_score_image(ocl_ctx, images, masks, window_radius):
    """ compute a sliding NCC score based on a set of images with masks """

    cl_queue = cl.CommandQueue(ocl_ctx)

    num_images = len(images)
    img_dims = images[0].size

    # create large buffers of concatentated images and masks
    image_stack = np.zeros((num_images*img_dims[1], img_dims[0]),np.float32)
    mask_stack = np.zeros((num_images*img_dims[1], img_dims[0]),np.uint8)
    for i in range(num_images):
        image_stack[i*img_dims[1]:(i+1)*img_dims[1],:] = np.array(images[i]).astype(np.float32)
        mask_stack[i*img_dims[1]:(i+1)*img_dims[1],:] = np.array(masks[i]).astype(np.uint8)

    mf = cl.mem_flags
    image_buff = cl.Buffer(ocl_ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=image_stack)
    mask_buff = cl.Buffer(ocl_ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=mask_stack)

    score_img = np.zeros((img_dims[1], img_dims[0]),np.float32)
    output_buff = cl.Buffer(ocl_ctx, mf.WRITE_ONLY, score_img.nbytes)

    cl_dir = os.path.dirname(__file__)
    cl_filename = cl_dir + '/cl/NCC_score_multi.cl'
    with open(cl_filename, 'r') as fd:
        clstr = fd.read()

    prg = cl.Program(ocl_ctx, clstr).build()
    prg.NCC_score_multi(cl_queue, (img_dims[1], img_dims[0]), None,
                        image_buff, mask_buff, output_buff, np.int32(num_images),
                        np.int32(img_dims[0]), np.int32(img_dims[1]), np.int32(window_radius))

    cl.enqueue_copy(cl_queue, score_img, output_buff)
    cl_queue.finish()
    return score_img, image_stack, mask_stack


def sliding_NCC(ocl_ctx, img1, img2, window_radius):
    """ perform normalized cross-corellation on a window centered around every pixel """

    cl_queue = cl.CommandQueue(ocl_ctx)

    img1_np = np.array(img1).astype(np.float32)
    img2_np = np.array(img2).astype(np.float32)

    mf = cl.mem_flags
    i1_buf = cl.Buffer(ocl_ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img1_np)
    i2_buf = cl.Buffer(ocl_ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img2_np)
    dest_buf = cl.Buffer(ocl_ctx, mf.WRITE_ONLY, img1_np.nbytes)

    cl_dir = os.path.dirname(__file__)
    cl_filename = cl_dir + '/cl/sliding_ncc.cl'
    with open(cl_filename, 'r') as fd:
        clstr = fd.read()

    prg = cl.Program(ocl_ctx, clstr).build()
    prg.sliding_ncc(cl_queue, img1_np.shape, None,
                    i1_buf, i2_buf, dest_buf,
                    np.int32(img1_np.shape[1]), np.int32(img1_np.shape[0]), np.int32(window_radius))

    ncc_img = np.zeros_like(img1_np)
    cl.enqueue_copy(cl_queue, ncc_img, dest_buf)
    cl_queue.finish()

    return ncc_img


def sliding_SSD(ocl_ctx, img1, img2, window_radius):
    """ perform sum of squared differences on a window centered around every pixel """

    cl_queue = cl.CommandQueue(ocl_ctx)

    img1_np = np.array(img1).astype(np.float32)
    img2_np = np.array(img2).astype(np.float32)

    mf = cl.mem_flags
    i1_buf = cl.Buffer(ocl_ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img1_np)
    i2_buf = cl.Buffer(ocl_ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=img2_np)
    dest_buf = cl.Buffer(ocl_ctx, mf.WRITE_ONLY, img1_np.nbytes)

    cl_dir = os.path.dirname(__file__)
    cl_filename = cl_dir + '/cl/sliding_ssd.cl'
    with open(cl_filename, 'r') as fd:
        clstr = fd.read()

    prg = cl.Program(ocl_ctx, clstr).build()
    prg.sliding_ssd(cl_queue, img1_np.shape, None,
                    i1_buf, i2_buf, dest_buf,
                    np.int32(img1_np.shape[1]), np.int32(img1_np.shape[0]), np.int32(window_radius))

    ssd_img = np.zeros_like(img1_np)
    cl.enqueue_copy(cl_queue, ssd_img, dest_buf)
    cl_queue.finish()

    return ssd_img

