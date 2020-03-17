# -*- coding: utf-8 -*-
import json
import pandas as pd
from os import listdir
from os.path import isfile, join

BASE_PATH = 'data'

records = []
for file in [f for f in listdir(BASE_PATH) if isfile(join(BASE_PATH, f)) and f.endswith('json')]:
    print(file)
    record = json.load(open(join(BASE_PATH, file), 'r'))
    cols = [
        'itineraireEntree', 'itineraireSortie', 'radarTronconKm',
        'traceItineraire', 'radarGeolocalisation', 'radarDirection',
        'radarPlace'
    ]
    for key in cols:
        if record[key] == []:
            record[key] = None

    for key in ['radarEquipment', 'radarRoad']:
        if record[key] == '-':
            record[key] = None

    if len(record['radarType']) != 1:
        raise NotImplementedError
    record['radarNameDetails'] = record['radarType'][0]['radarNameDetails']

    # Parse vitesse
    rules = [e['name'] for e in record['rulesMesured']]

    vitesse_vl = [r for r in rules if r.startswith('Vitesse VL')]
    record['vitesse_vehicules_legers_kmh'] = None
    if len(vitesse_vl) == 1:
        record['vitesse_vehicules_legers_kmh'] = int(vitesse_vl[0].split(' ')[2].strip())

    vitesse_pl = [r for r in rules if r.startswith('Vitesse PL')]
    record['vitesse_poids_lourds_kmh'] = None
    if len(vitesse_pl) == 1:
        record['vitesse_poids_lourds_kmh'] = int(vitesse_pl[0].split(' ')[2].strip())

    # Parse coordinates
    record['latitude'] = None
    record['longitude'] = None
    if record['traceItineraire'] is not None:
        record['latitude'] = record['traceItineraire']['lat']
        record['longitude'] = record['traceItineraire']['lon']
    if record['radarGeolocalisation'] is not None:
        splitted_geoloc = record['radarGeolocalisation'].split(" ")
        print(splitted_geoloc[1][1:])
        print(splitted_geoloc[2][:-1])
        record['latitude'] = splitted_geoloc[2][:-1]
        record['longitude'] = splitted_geoloc[1][1:]

    # Parse radarTronconKm
    if record['radarTronconKm'] is not None:
        record['radarTronconKm'] = float(record['radarTronconKm'].replace(',', '.'))

    # Parse department
    record['department'] = record['department'].split('-')[0].strip()

    records.append(record)

df = pd.DataFrame(records)
df['radarInstallDate'] = pd.to_datetime(df['radarInstallDate'], format='%Y-%m-%dT%H:%M:%S')
for col in ['created', 'changed']:
    df[col] = pd.to_datetime(df[col], unit='s')
df.drop(columns=[
    'langcode', 'type', 'defaultLangcode', 'path', 'radarType',
    'rulesMesured', 'revisionTimestamp', 'radarGeolocalisation',
    'promote', 'revisionLog', 'revisionTranslationAffected',
    'status', 'sticky', 'title', 'uid', 'uuid', 'revisionUid',
    'vid',
    'traceItineraire', 'itineraireEntree', 'itineraireSortie'
], inplace=True)

df.rename(
    index=str,
    columns={
        "changed": "date_heure_dernier_changement",
        "created": "date_heure_creation",
        "department": "departement",
        "nid": "id",
        "radarDirection": "direction",
        "radarEquipment": "equipement",
        "radarInstallDate": "date_installation",
        "radarNameDetails": "type",
        "radarPlace": "emplacement",
        "radarRoad": "route",
        "radarTronconKm": "longueur_troncon_km",
    },
    inplace=True
)

df.sort_values(by=['id'], inplace=True)

df.to_csv(
    'data/radars.csv',
    index=False,
    encoding='utf-8',
    float_format='%.12g',
    date_format='%Y-%m-%dT%H:%M:%SZ'
)
