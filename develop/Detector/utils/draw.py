def rand_color(exist_color_list=[]):
    """
    Pick a color randomly which is different from any color in exist_color_list.
    :param exist_color_list: exist color list [(B, G, R)]
    :return: new_color: chosen color (B:int, G:int, R:int)
             exist_color_list: updated exist color [(B, G, R), (B, G, R), ...]
    """
    from random import randint
    new_color = (randint(0, 255), randint(0, 255), randint(0, 255))  # (Blue. Green. Red)
    while new_color in exist_color_list:
        new_color = (randint(0, 255), randint(0, 255), randint(0, 255))  # (Blue. Green. Red)
    exist_color_list.append(new_color)
    return new_color, exist_color_list
