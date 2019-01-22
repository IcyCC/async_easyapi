def str2hump(text):
    """
    驼峰转下划线
    :param text:
    :return:
    """
    arr = filter(None, text.lower().split('_'))
    res = ''
    for i in arr:
        res = res + i[0].upper() + i[1:]
    return res


def default_url_condition(args: dict) -> (dict, dict, dict):
    """
    默认的url参数条件解析
    :param args:
    :return:
    """
    query = {}
    pager = {}
    sorter = {}
    if args:
        for k, v in args.items():
            if k == '_per_page':
                pager['_per_page'] = v
            elif k == '_page':
                pager['_page'] = v
            elif k == '_order_by':
                sorter['_order_by'] = v
            elif k == '_desc':
                sorter['order'] = v
            else:
                if isinstance(v, list):
                    query[k] = v
                else:
                    query[k] = [v]
    return query, pager, sorter
