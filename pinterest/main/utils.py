def user_interest_tags(interested_tags):
    """create list of user interest
    :param interested_tags:
    :return: user interested tag list
    """

    list = []
    for interest in interested_tags:
        list.append(interest[0])
    return list


def user_interest_pins(inst_pin_id):
    """create user pin list which is user interested
    :param inst_pin_id:
    :return: user interested pin list
    """

    list = []
    for pin in inst_pin_id:
        list.append(pin.pin_id)
    return list

