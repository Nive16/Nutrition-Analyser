# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import django
import requests
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt


def get_labels(request):
    import base64
    with open("burger.jpeg", "rb") as imageFile:
        base64_str = base64.b64encode(imageFile.read())
    PARAMS = {"requests": [{"image": {
        "content": base64_str},
        "features": [{
            "type": "LABEL_DETECTION",
            "maxResults": 10
        }
        ]}]}
    vision_response = requests.post(
        "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAjpIkgAjiWc2rwMR7473FM3cGAMTZUsmk",
        json=PARAMS).json()
    print("Contains: " + str(vision_response['responses'][0]['labelAnnotations'][0]['description']))
    print("Score: " + str(vision_response['responses'][0]['labelAnnotations'][0]['score']))


def get_nutrients(request, food_name):
    food_name = "hamburger"
    headers = {'x-app-id': '5995d752', 'x-app-key': 'f71c977eac2182ba9d35b4fcc1a98360',
               'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'query': food_name}
    nutrient_response = requests.post("https://trackapi.nutritionix.com/v2/natural/nutrients", data=data,
                                      headers=headers)
    print(nutrient_response.json())


@csrf_exempt
def analyse_image(request):
    if request.method == "POST":
        data = request.POST
        base64_str = data.get('base_64')
        base64_str = str(base64_str).split('base64,')[1]

        PARAMS = {"requests": [{"image": {
            "content": base64_str},
            "features": [{
                "type": "LABEL_DETECTION",
                "maxResults": 10
            }
            ]}]}

        vision_response = requests.post(
            "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAjpIkgAjiWc2rwMR7473FM3cGAMTZUsmk",
            json=PARAMS).json()

        if 'food' in str(vision_response):
            name_str = str(vision_response['responses'][0]['labelAnnotations'][0]['description'])
            if name_str == "dish":
                PARAMS = {"requests": [{"image": {
                    "content": base64_str},
                    "features": [{
                        "type": "WEB_DETECTION",
                        "maxResults": 10
                    }
                    ]}]}

                vision_response_web = requests.post(
                    "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAjpIkgAjiWc2rwMR7473FM3cGAMTZUsmk",
                    json=PARAMS).json()
                name_str = str(vision_response_web['responses'][0]['webDetection']['webEntities'][0]["description"])
            return JsonResponse({'name': name_str})
        else:
            return JsonResponse({'name': "No foods found."})


@csrf_exempt
def analyse_nutrients(request):
    vitamin_name1 = None
    vitamin_name2 = None
    unit1 = None
    unit2 = None
    if request.method == "POST":
        data = request.POST
        food_name = data.get('name')
        print(food_name)
        headers = {'x-app-id': '5995d752', 'x-app-key': 'f71c977eac2182ba9d35b4fcc1a98360',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'query': food_name}
        nutrients = requests.post("https://trackapi.nutritionix.com/v2/natural/nutrients", data=data,
                                  headers=headers).json()

        calories = nutrients['foods'][0]['nf_calories']
        potassium = nutrients['foods'][0]['nf_potassium']
        protein = nutrients['foods'][0]['nf_protein']
        fat = nutrients['foods'][0]['nf_total_fat']
        list_1 = nutrients['foods'][0]['full_nutrients']
        from operator import itemgetter
        newlist = sorted(list_1, key=itemgetter('value'), reverse=True)
        file = open(str(os.path.abspath(os.path.dirname('__file__')))+'/nutrition_analyser/nutrient.csv').read().splitlines()
        for i in file:

            attr_id = i.split(',')[0]
            if attr_id == str(newlist[0]['attr_id']):
                vitamin_name1 = i.split(',')[2]
                unit1 = i.split(',')[3]
                if " \"" in str(unit1):
                    unit1 = i.split(',')[4]
            elif attr_id == str(newlist[1]['attr_id']):
                vitamin_name2 = i.split(',')[2]
                unit2 = i.split(',')[3]
                if " \"" in str(unit2):
                    unit2 = i.split(',')[4]
        return JsonResponse({'calories': str(calories), 'potassium': str(potassium), 'protein': str(protein), 'fat': str(fat),
                             "vitamin_name1": str(vitamin_name1), "vitamin_unit1": str(unit1), "vitamin_name2": str(vitamin_name2),
                             "vitamin_unit2": str(unit2), "vitamin_value1": str(newlist[0]['value']),
                             'vitamin_value2': str(newlist[1]['value'])})
