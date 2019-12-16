import os
import random
from lxml.etree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import matplotlib.pyplot as plt
from PIL import Image


src_txt_dir = "./data/Annotation"
src_img_dir = "./data/images"
src_xml_dir = "./data/Annotations"
src_main_dir = "./data/ImageSets"

def get_details(txt_name):
    # load images

    img_name = txt_name.replace('txt','jpg')

    txt_dir = os.path.join(src_txt_dir,txt_name)
    img_dir = os.path.join(src_img_dir,img_name)

    img = Image.open(img_dir)
    img_bands = img.getbands()
    img_size = img.size
    # 通道
    depth = len(img_bands)
    # 宽度
    width = img_size[0]
    # 高度
    height = img_size[1]


    # 边框
    boxes = []
    # 类别
    objects = []


    with open(txt_dir,"rb") as f:
        for line in f.readlines():
            annotation = line.split()
            boxes.append([int(x) for x in annotation[2:]])
            if annotation[1]==bytes("带电芯充电宝",encoding='utf8'):
                objects.append('core')
            else:
               objects.append('coreless')

    # plt.imshow(img)
    # for box,obj in zip(boxes,objects):
    #     plt.plot([box[0],box[2]],[box[1],box[1]],c='r')
    #     plt.plot([box[0],box[0]],[box[1],box[3]],c='r')
    #     plt.plot([box[0],box[2]],[box[3],box[3]],c='r')
    #     plt.plot([box[2],box[2]],[box[1],box[3]],c='r')
    #     plt.text(box[0], box[1], obj,size=12,c = 'r')

    # plt.show()

    target = {}
    target["filename"] = img_name
    target["width"] = width
    target["height"] = height
    target["depth"] = depth
    target["boxes"] = boxes
    target["object"] = objects

    return target

def save_xml(target={},target_dir=src_xml_dir):

    filename = target["filename"]
    width = target["width"]
    height = target["height"]
    depth = target["depth"]
    boxes = target["boxes"]
    objects = target["object"]


    node_root = Element('annotation')

    node_folder = SubElement(node_root, 'folder')
    node_folder.text = 'Image'

    node_filename = SubElement(node_root, 'filename')
    node_filename.text = filename

    node_size = SubElement(node_root, 'size')
    node_width = SubElement(node_size, 'width')
    node_width.text = '%s' % width

    node_height = SubElement(node_size, 'height')
    node_height.text = '%s' % height

    node_depth = SubElement(node_size, 'depth')
    node_depth.text = '%s' % depth

    for box, object in zip(boxes,objects):
        node_object = SubElement(node_root, 'object')
        node_name = SubElement(node_object, 'name')
        node_name.text = object
        node_difficult = SubElement(node_object, 'difficult')
        node_difficult.text = '0'
        node_bndbox = SubElement(node_object, 'bndbox')
        node_xmin = SubElement(node_bndbox, 'xmin')
        node_xmin.text = '%s' % box[0]
        node_ymin = SubElement(node_bndbox, 'ymin')
        node_ymin.text = '%s' % box[1]
        node_xmax = SubElement(node_bndbox, 'xmax')
        node_xmax.text = '%s' % box[2]
        node_ymax = SubElement(node_bndbox, 'ymax')
        node_ymax.text = '%s' % box[3]

    xml = tostring(node_root, pretty_print=True)
    dom = parseString(xml)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    save_xml = os.path.join(target_dir, filename.replace('jpg', 'xml'))

    with open(save_xml, 'wb') as f:
        f.write(xml)


# 生成训练，测试，验证集
def generate_main(xml_path=src_xml_dir,part_path=src_main_dir):
    trainval_percent = 0.1
    train_percent = 0.9
    total_xml = os.listdir(xml_path)

    num = len(total_xml)
    list = range(num)

    tv = int(num * trainval_percent)
    tr = int(tv * train_percent)

    trainval = random.sample(list, tv)
    train = random.sample(trainval, tr)

    if not os.path.exists(part_path):
        os.makedirs(part_path)

    ftrainval = open(os.path.join(part_path,'trainval.txt'), 'w')
    ftest = open(os.path.join(part_path,'test.txt'), 'w')
    ftrain = open(os.path.join(part_path,'train.txt'), 'w')
    fval = open(os.path.join(part_path,'val.txt'), 'w')

    for i in list:
        name = total_xml[i][:-4] + '\n'
        if i in trainval:
            ftrainval.write(name)
            if i in train:
                ftest.write(name)
            else:
                fval.write(name)
        else:
            ftrain.write(name)

    ftrainval.close()
    ftrain.close()
    fval.close()
    ftest.close()




def change_to_xml(txt_list):
    for item in txt_list:
        target = get_details(item)
        save_xml(target)


# def draw_picture(jpg_name):
#     jpg_path = os.path.join(src_img_dir,jpg_name,'.jpg')
#     txt_name = os.path.join(jpg_name,'.txt')
#     boxes = get_details(txt_name)['boxes']
#     plt.imshow(jpg_path)
#     for box in boxes:
#         plt.plot([box[0],box[2]],[box[1],box[1]],c='r')
#         plt.plot([box[0],box[0]],[box[1],box[3]],c='r')
#         plt.plot([box[0],box[2]],[box[3],box[3]],c='r')
#         plt.plot([box[2],box[2]],[box[1],box[3]],c='r')

if __name__ == "__main__":
    txt_list= list(sorted(os.listdir(src_txt_dir)))
    change_to_xml(txt_list)
    generate_main()
    # txt_name = 'core_battery00000708.txt'
    # get_details(txt_name)
