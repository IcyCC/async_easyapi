from sqlalchemy import Table
from dataclasses import dataclass

OPERATOR_FUNC_DICT = {
    '=': (lambda cls, k, v: getattr(cls, k) == v),
    '_gt_': (lambda cls, k, v: getattr(cls, k) > v),
    '_gte_': (lambda cls, k, v: getattr(cls, k) >= v),
    '_lt_': (lambda cls, k, v: getattr(cls, k) < v),
    '_lte_': (lambda cls, k, v: getattr(cls, k) <= v),
    '_like_': (lambda cls, k, v: getattr(cls, k).like(v + '%')),
    '_search_': (lambda cls, k, v: getattr(cls, k).like('%'+ v + '%')),
    '_in_': (lambda cls, k, v: getattr(cls, k).in_(v)),
}

# 从字段转 sql
def search_sql(sql, query: dict, table: Table):
    """字段转 sql
        Args:
            sql ([type]):sql 语句
            query (dict): 查询条件字典
            table (Table): 表
        Returns:
            [type]: [description]
    """
    for key in query.keys():
        if type(query[k]) is not list:
            # 兼容处理
            values = [query[key]]
        else:
            values = query[key]
        
        if key.startwith('_'): 
            for query_key in OPERATOR_FUNC_DICT.keys():
                if key.startswith(query_key):
                    for v in values:
                        sql = sql.where(OPERATOR_FUNC_DICT[query_key](table.c, key[len(query_key):], v))
        else:
            sql = sql.where(OPERATOR_FUNC_DICT['='](table.c,key,v))
    return sql


@dataclass
class Pager:
    """
    分页
    """
    page: int = None
    per_page: int = None


@dataclass
class Sorter:
    """
    排序
    """
    sort_by: str = 'id'
    desc: bool = True
