from cachetools import Cache, cached
from app.sheets import get_category

cat_cache = Cache(maxsize=3)

def convert_list(original_list):
    new_list = []
    temp_list = []
    for sublist in original_list:
        if len(temp_list) < 3:
            temp_list.append(sublist)
        else:
            new_list.append(temp_list)
            temp_list = [sublist]
        
    if temp_list:
        new_list.append(temp_list)

    return new_list

@cached(cat_cache)
def get_sheet_category():
    data = get_category()
    keys_cat = {}
    for first, second in data:
        keys_cat.setdefault(first, []).append(second)
    
    keys = list(keys_cat.keys())
    return keys, keys_cat

def invalidate_cahce():
    cat_cache.clear()

def get_cache_category():
    list, _ = get_sheet_category()
    return convert_list(list)

def contains_category(key) -> bool:
    list, _ = get_sheet_category()
    return list.__contains__(key)

def contains_sub_category(key, value) -> bool:
    list, cat = get_sheet_category()
    return list.__contains__(key) and cat[key].__contains__(value)

def get_cache_sub_category(name):
    _, cat = get_sheet_category()
    return convert_list(cat[name])