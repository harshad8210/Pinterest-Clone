def block_user_list(blocks):
    """for blocked user list
    :param blocks: query input
    :return: blocked user list
    """

    block_list = []
    for block in blocks:
        block_list.append(block.user_id)
    return block_list
