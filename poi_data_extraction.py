''' poi_data_extraction.py
functions to extract and format data from a poi geojson
'''

import json

def collect_values(obj, key, results_list):
    # check if obj is a dict
    if isinstance(obj, dict):
        # check if key is in dict
        for k, v in obj.items():
            if k == key:
                # append key value to results list
                results_list.append(v)
            else:
                # recurse
                collect_values(v, key, results_list)
    # run over obj list by elem
    elif isinstance(obj, list):
        for item in obj:
            collect_values(item, key, results_list)

def extract_values(geojson_path, key):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results_list = []
    collect_values(data, key, results_list)
    return results_list
