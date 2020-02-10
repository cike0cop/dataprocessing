# -*- coding: UTF-8 -*-
# @Time : 2020/2/10 22:52
# @Author : coplin
# @File : demo.py
# @Software: PyCharm
# @Dec : COCO annotations.json split into train.json、valtrain.json
import json
from sklearn.model_selection import train_test_split
def load_json_obj(json_file_path):
    with open(json_file_path) as f:
        json_file = json.load(f)
    json_info = json_file['info']
    json_image = json_file['images']
    json_license = json_file['license']
    json_categories = json_file['categories']
    json_annotations = json_file['annotations']
    print("概况》", " 类数：", len(json_categories), " 图像数：", len(json_image), " 标记数：", len(json_annotations))
    annotations_ID = []
    category_ID = []
    for i in range(len(json_annotations)):
        ann = json_annotations[i]
        annotations_ID.append(i)
        category_ID.append(ann['category_id'])
    X_train, X_test, y_train, y_test = train_test_split(annotations_ID, category_ID, test_size = 0.3, random_state = 0)
    annotations_train = []
    annotations_valtrain = []
    print("X_train: ", len(X_train), "x_test: ", len(X_test))
    for i in range(len(X_train)):
        annotations_train.append(json_annotations[X_train[i]])
    for i in range(len(X_test)):
        annotations_valtrain.append(json_annotations[X_test[i]])
    print("train: ", len(annotations_train), "val: ", len(annotations_valtrain))
    json_train = json_file
    json_valtrain = json_file
    json_train['annotations'] = annotations_train
    json_valtrain['annotations'] = annotations_valtrain
    return json_train, json_valtrain

def savejson(train, valtrain):
    annotations_train = json.dumps(train)
    with open('data\\annotations_train.json', 'w') as json_file:
        json_file.write(annotations_train)
    annotations_valtrain = json.dumps(valtrain)
    with open('data\\annotations_valtrain.json', 'w') as json_file:
        json_file.write(annotations_valtrain)
def main():
    json_file_path = r"data\annotations_washed.json"
    print("json路径：", json_file_path)
    annotations_train, annotations_valtrain = load_json_obj(json_file_path)
    savejson(annotations_train, annotations_valtrain)

if __name__ == '__main__':
    main()