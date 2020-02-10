# -*- coding: UTF-8 -*-
import os
import xml.etree.ElementTree as ET
from lxml import etree
from PIL import Image
import json
import shutil

# 递归读取文件夹下文件路径
# 输入：- root：文件目录 - ext：文件后缀（None则所有后缀都读取）
# 输出：
#   - file_list： root目录下后缀在ext中的文件绝对路径
#   - rel_file_list： root目录下后缀在ext中的文件相对路径
def load_file(root, rel_path="", file_list=[], rel_file_list=[], ext=None):
    if os.path.isfile(root):
        # if check_img(root):
        if ext != None:
            if root.split(".")[-1] in ext:
                file_list.append(root)
                rel_file_list.append(rel_path)
        else:
            file_list.append(root)
            rel_file_list.append(rel_path)
    elif os.path.isdir(root):
        for path_i in os.listdir(root):
            sub_root = os.path.join(root, path_i)
            sub_rel_path = os.path.join(rel_path, path_i)
            file_list, rel_file_list = load_file(sub_root, sub_rel_path, file_list, rel_file_list, ext)
    return file_list, rel_file_list

# 单个object构造
def insert_object_node(root_node, xmin, ymin, xmax, ymax, label):
    object_node = ET.SubElement(root_node, 'object')
    name_node = ET.SubElement(object_node, 'name')
    name_node.text = str(label)
    pose_node = ET.SubElement(object_node, 'pose')
    pose_node.text = 'Unspecified'
    truncated_node = ET.SubElement(object_node, 'truncated')
    truncated_node.text = '0'
    difficult_node = ET.SubElement(object_node, 'difficult')
    difficult_node.text = '0'

    bndbox_node = ET.SubElement(object_node, 'bndbox')
    xmin_node = ET.SubElement(bndbox_node, 'xmin')
    xmin_node.text = str(xmin)
    ymin_node = ET.SubElement(bndbox_node, 'ymin')
    ymin_node.text = str(ymin)
    xmax_node = ET.SubElement(bndbox_node, 'xmax')
    xmax_node.text = str(xmax)
    ymax_node = ET.SubElement(bndbox_node, 'ymax')
    ymax_node.text = str(ymax)

# 生成XML文件
# 若 ann_root 为 None 则在图像路径底下生成一个对应的xml文件， 否则在 ann_root 底下生成
# 备注拒绝中文路径，容易出错
def save_xml(im_path, bboxes, ann_root=None):
    # create node
    root_node = ET.Element('annotation')

    folder_node = ET.SubElement(root_node, 'folder')
    folder_node.text = im_path
    filename_node = ET.SubElement(root_node, 'filename')
    filename_node.text = os.path.splitext(os.path.basename(im_path))[0]
    path_node = ET.SubElement(root_node, 'path')
    path_node.text = im_path

    source_node = ET.SubElement(root_node, 'source')
    database_node = ET.SubElement(source_node, 'database')
    database_node.text = 'gesture'

    img = Image.open(path_node.text)
    imgSize = img.size

    size_node = ET.SubElement(root_node, 'size')
    width_node = ET.SubElement(size_node, 'width')
    width_node.text = str(imgSize[0])
    height_node = ET.SubElement(size_node, 'height')
    height_node.text = str(imgSize[1])
    depth_node = ET.SubElement(size_node, 'depth')
    depth_node.text = '3'

    segmented_node = ET.SubElement(root_node, 'segmented')
    segmented_node.text = '0'

    for key in bboxes.keys():
        for box_i in bboxes[key]:
            [xmin, ymin, xmax, ymax] = [box_i[0], box_i[1], box_i[2], box_i[3]]
            insert_object_node(root_node, xmin, ymin, xmax, ymax, label=key)

    if ann_root is None:
        write_xml = "{}.xml".format(os.path.splitext(im_path)[0])
    else:
        write_xml = os.path.join(ann_root, "{}.xml".format(os.path.splitext(os.path.basename(im_path))[0]))

    tree = ET.ElementTree(root_node)
    if not os.path.exists(os.path.dirname(write_xml)):
        os.makedirs(os.path.dirname(write_xml))
    tree.write(write_xml, encoding='utf-8', xml_declaration=True)

    # lxml
    parser = etree.XMLParser()
    document = etree.parse(write_xml, parser)
    document.write(write_xml, pretty_print=True, encoding='utf-8')

# tc专用
# 读取json文件，将标注按照文件名为key存成dict并返回
# 拒绝中文路径,容易出错
def load_json_obj(json_file_path, img_root, ignore_list = None):
    all_boxes = {}
    with open(json_file_path) as f:
        json_file = json.load(f)

    for images_i in json_file['images']:
        file_name = images_i['file_name']
        file_id = images_i['id']
        file_height = images_i['height']
        file_width = images_i['width']
        file_path = os.path.join(img_root, file_name)
        img = Image.open(file_path)
        imgSize = img.size
        if int(file_width) != imgSize[0] or int(file_height) != imgSize[1]:
            print("尺寸不符： {}".format(file_name))
            continue
        all_boxes[file_id]={}
        all_boxes[file_id]["file_path"]= file_path

    for annotations_i in json_file['annotations']:
        image_id = annotations_i['image_id']
        if not image_id in all_boxes.keys():
            print("第{}号文件有误！".format(image_id))
            continue
        if not 'bboxes' in all_boxes[image_id].keys():
            all_boxes[image_id]['bboxes'] = {}

        category_id = annotations_i['category_id']
        if category_id in ignore_list:
            continue
        if not category_id in all_boxes[image_id]['bboxes'].keys():
            all_boxes[image_id]['bboxes'][category_id] = []

        # 转化为xml文件的xmin, ymin, xmax, ymax
        bbox = annotations_i['bbox']
        bbox_obj = [bbox[0], bbox[1], bbox[0] + bbox[2] - 1, bbox[1] + bbox[3] - 1]
        all_boxes[image_id]['bboxes'][category_id].append(bbox_obj)
    return all_boxes



def main():
    json_file_path = r"F:\tianchi\pzj\chongqing1_round1_train1_20191223\annotations.json"
    img_root = r"F:\tianchi\pzj\chongqing1_round1_train1_20191223\images"
    ann_root = r"F:\tianchi\pzj\chongqing1_round1_train1_20191223\annotations_clean"
    ignore_list = [0]

    all_boxes = load_json_obj(json_file_path, img_root, ignore_list)

    for image_id in all_boxes.keys():
        im_path = all_boxes[image_id]['file_path']
        bboxes = all_boxes[image_id]['bboxes']
        if len(bboxes.keys())<1:
            continue
        save_xml(im_path, bboxes, ann_root=ann_root)
        # print(os.path.join(ann_root, os.path.basename(im_path)))
        shutil.copy(im_path, os.path.join(ann_root, os.path.basename(im_path)))


if __name__ == '__main__':
    main()


