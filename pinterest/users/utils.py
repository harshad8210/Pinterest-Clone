from flask import current_app
from pinterest.models import Follow
import secrets
import os
from PIL import Image


def save_pic(form_pic):
    """separates extension from file name and convert filename to hex and add hex to extension
    :param form_pic: string
    :return: new file name or image name
    """

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    profile_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_img', profile_fn)

    pic_size = (150, 150)
    i = Image.open(form_pic)
    i.thumbnail(pic_size)

    i.save(picture_path)
    return profile_fn


def selected_user_tags(user_tags):
    """
    :param user_tags: query obj
    :return: user selected tag list
    """
    selected_tags = []
    for i in user_tags:
        selected_tags.append(i.tag_id)
    return selected_tags


def password_check(passwd):
    specialsym = ['$', '@', '#', '%']

    if not any(char.isdigit() for char in passwd):
        msg = 'Password should have at least one numeral'
        return True, msg

    elif not any(char.isupper() for char in passwd):
        msg = 'Password should have at least one uppercase letter'
        return True, msg

    elif not any(char.islower() for char in passwd):
        msg = 'Password should have at least one lowercase letter'
        return True, msg

    elif not any(char in specialsym for char in passwd):
        msg = 'Password should have at least one of the symbols $@#'
        return True, msg

    else:
        msg = 'Password validate'
        return False, msg


def count_follower(user_id):
    """count followers and user followings
    :param user_id:
    :return: int-followers, int-following
    """

    followers = Follow.query.filter_by(user_id=user_id).count()
    following = Follow.query.filter_by(follower_id=user_id).count()
    return followers, following
