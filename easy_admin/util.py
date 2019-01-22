def str2hump(text):
    """
    驼峰转下划线
    :param text:
    :return:
    """
    arr = filter(None, text.lower().split('_'))
    res = ''
    for i in arr:
        res =  res + i[0].upper() + i[1:]
    return res
