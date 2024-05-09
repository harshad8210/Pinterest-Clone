from flask import current_app
import secrets, os
from PIL import Image


def save_pin_img(form_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    pin_pic_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/pin_img', pin_pic_fn)

    i = Image.open(form_pic)
    i.save(picture_path)
    return pin_pic_fn


def get_selected_tags(pin_tags):
    selected_tags = []
    for tag in pin_tags:
        selected_tags.append(tag.tag_id)
    return selected_tags


def list_tag_trandings(all_tag, tranding_tag):
    """generates tranding tag list
    :param all_tag:
    :param tranding_tag:
    :return: list of tranding tag id
    """

    tranding_tag = sorted(tranding_tag, reverse=True)
    list1 = []
    list2 = []
    for i in all_tag:
        list1.append(i.id)
    for j in tranding_tag:
        list2.append(j.tag_id)
    for k in list1:
        if k not in list2:
            list2.append(k)
    return list2
