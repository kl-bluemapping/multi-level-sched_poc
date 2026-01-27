import os
import sys
import json

def extract_list_from_dict(obj, key, res_list):
    # check if obj is a dict
    if isinstance(obj, dict):
        # check if key is in dict
        for k, v in obj.items():
            if k == key:
                # append key value to results list
                res_list.append(v)
            else:
                # recurse
                extract_list_from_dict(v, key, res_list)
    # run over obj list by elem
    elif isinstance(obj, list):
        for item in obj:
            extract_list_from_dict(item, key, res_list)

def extract_key_from_geojson(geojson_path, key):
    # Charger le fichier GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    res_list = []
    extract_list_from_dict(data, key, res_list)

    return res_list



def extract_timeseries(geojson_path):
    # Charger le fichier GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    timeseries_list = []

    def search_for_timeserie(obj):
        # Si l'objet est un dictionnaire
        if isinstance(obj, dict):
            # Vérifier si 'timeserie' est une clé dans cet objet
            for key, value in obj.items():
                if key == 'timeserie':
                    # Ajouter la valeur de 'timeserie' à la liste
                    timeseries_list.append(value)
                else:
                    # Continuer la recherche récursive
                    search_for_timeserie(value)
        # Si l'objet est une liste, parcourir chaque élément
        elif isinstance(obj, list):
            for item in obj:
                search_for_timeserie(item)

    # Démarrer la recherche dans toute la structure
    search_for_timeserie(data)

    return timeseries_list

if len(sys.argv) != 2:
    print('missing parameter: <geojson_file>')
    sys.exit(1)

(_, geojson_file) = sys.argv


timeseries = extract_key_from_geojson(geojson_file, 'timeserie')
for ts in range(len(timeseries)):
    timeserie = timeseries[ts]
    print(f"{type(timeserie) = } {type(timeserie) =}")
    print(f"{len(timeserie) = }")

time_vectors = extract_key_from_geojson(geojson_file, 'time_vector')
for ts in range(len(time_vectors)):
    time_vector = time_vectors[ts]
    print(f"{type(time_vector) = }")
    print(f"{len(time_vector) = }")
    print(f"{time_vector = }")

print(f"{time_vector[0] = }")
print(f"{time_vector[1] = }")

