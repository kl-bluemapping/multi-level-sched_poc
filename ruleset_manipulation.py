import json5

def find_and_update_key(obj, key, value):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                if not isinstance(v, list):
                    v = []
                    obj[k] = v
                v.append(value)
                return True
            else:
                if find_and_update_key(v, key, value):
                    return True
    elif isinstance(obj, list):
        for item in obj:
            if find_and_update_key(item, key, value):
                return True
    return False

def insert_value(ruleset, key, value):
    with open(ruleset, 'r', encoding='utf-8') as file:
        data = json5.load(file)
    found = find_and_update_key(data, key, value)
    if not found:
        data[key] = [42]
    with open(ruleset, 'w', encoding='utf-8') as file:
        json5.dump(data, file, ensure_ascii=False, indent=4)
    return

def find_and_update_dict(obj, target_key, insert_key, insert_value):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == target_key:
                if not isinstance(v, dict):
                    obj[k] = {}
                obj[k][insert_key] = insert_value
                return True
            else:
                if find_and_update_dict(v, target_key, insert_key, insert_value):
                    return True
    elif isinstance(obj, list):
        for item in obj:
            if find_and_update_dict(item, target_key, insert_key, insert_value):
                return True
    return False

def insert_pair(ruleset, target, key, value):
    with open(ruleset, 'r', encoding='utf-8') as file:
        data = json5.load(file)
    found = find_and_update_dict(data, target, key, value)
    if not found:
        data[target] = {key:value}
    with open(ruleset, 'w', encoding='utf-8') as file:
        json5.dump(data, file, ensure_ascii=False, indent=4)
    return
