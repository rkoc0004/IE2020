from flask import Flask, request, jsonify, render_template, render_template_string, Response
from flask_restful import Resource, Api
from json import dumps
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import shapely.vectorized as sv
from time import time
from math import radians, cos, sin, asin, sqrt
from flask_cors import CORS
import collections
import random

global inter_bush_neigh_dissolve_geom
global vic_locality_polygon
global species_vic_also_mod_con
global vic_state_b_1

inter_bush_neigh_dissolve_geom = gpd.read_file('inter_bush_neigh_dissolve_geom.shp')
vic_locality_polygon = gpd.read_file('vic_locality_polygon_shp-gda2020/VIC_LOCALITY_POLYGON_shp GDA2020/VIC_LOCALITY_POLYGON_shp.shp')
species_vic_also_mod_con = gpd.read_file('species_vic_also_mod_con.shp')
vic_state_b_1 = gpd.read_file('vic_state_b_1.shp')
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
  return 'Welcome Victoria!'

@app.route('/victoria/<string:coords_inp>')
def victoria_check(coords_inp):
    x,y = coords_inp.split(' ')
    x = float(x)
    y = float(y)
    c_1 = Point(x,y)
    if sv.contains(vic_state_b_1.geometry[0],c_1.x, c_1.y).flat[0]:
        message = 'Yes'
    else:
        message = 'No'
    return message


@app.route('/bushfire_message/<string:coords_inp>')
def bushfire_question(coords_inp):
    # if victoria_check(coords_inp)=='No':
    #     dict_message = {}
    #     list_message = []
    #     dict_message['message_key'] = ''
    #     list_message.append(dict_message)
    #     return dumps(list_message)
    x,y = coords_inp.split(' ')
    x = float(x)
    y = float(y)
    c_1 = Point(x,y)
    if sv.contains(inter_bush_neigh_dissolve_geom.geometry[0],c_1.x, c_1.y).flat[0]:
        message = 'Yes'
    else:
        message = 'No'
    return message

@app.route('/bushfire/<string:coords_inp>')
def bushfire_finder(coords_inp):
    # if victoria_check(coords_inp)=='No':
    #     dict_message = {}
    #     list_message = []
    #     dict_message['message_key'] = ''
    #     list_message.append(dict_message)
    #     return dumps(list_message)
    # x,y = coords_inp.split(' ')
    # x = float(x)
    # y = float(y)
    # c_1 = Point(x,y)
    # if sv.contains(inter_bush_neigh_dissolve_geom.geometry[0],c_1.x, c_1.y).flat[0]:
    #     message = 'Yes'
    # else:
    #     message = 'No'
    message = bushfire_question(coords_inp)
    dict_message = {}
    list_message = []
    dict_message['message_key'] = message
    list_message.append(dict_message)
    return dumps(list_message)

@app.route('/suburb/<string:coords_inp>')

def suburb_finder(coords_inp):
    if victoria_check(coords_inp)=='No':
        dict_suburb = {}
        list_suburb = []
        dict_suburb['suburb'] = ''
        list_suburb.append(dict_suburb)
        return dumps(list_suburb)
    x,y = coords_inp.split(' ')
    x = float(x)
    y = float(y)
    c_1 = Point(x,y)
    j = 0
    for i in range(len(vic_locality_polygon)):
        if c_1.within(vic_locality_polygon.geometry[i]):
            suburb = vic_locality_polygon.iloc[j,6]
            print()
            suburb = vic_locality_polygon.iloc[j,6]
        j+=1
    dict_suburb = {}
    list_suburb = []
    dict_suburb['suburb'] = suburb.title()
    list_suburb.append(dict_suburb)
    return dumps(list_suburb)
    # return 'Your suburb is'+' '+ suburb.title()

@app.route('/distance')

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

@app.route('/distance/<string:coords_inp>')

def location_finder(coords_inp):
    start_time = time()
    if victoria_check(coords_inp)=='No':
        dict_distance = {}
        list_distance = []
        dict_distance['distance'] = ''
        dict_distance['explore'] = ''
        list_distance.append(dict_distance)
        return dumps(list_distance)
    if bushfire_question(coords_inp)=='Yes':
        dist_bush = 0
        x,y = coords_inp.split(' ')
        x = float(x)
        y = float(y)
        c_1 = Point(x,y)
        list_dist_all = []
        dict_coords = dict()
        # yield('Your distance is being calculated...')
        for i in inter_bush_neigh_dissolve_geom.geometry[0]:
            j=0
            x, y = i.exterior.coords.xy
            for i in range(len(x)):
                # yield('Your distance is being calculated...')
                s = haversine(c_1.x, c_1.y, x[j], y[j])
                list_dist_all.append(s)
                dict_coords[round(s,2)] = str(x[j]) + ' ' + str(y[j])
                j+=1
        # dist_bush = round(min(list_dist_all),2)
        od  = collections.OrderedDict(sorted(dict_coords.items()))
        list_1 = list(od.values())[:80:20]
        choice_1 = random.choice(list_1)
        # yield(dist_bush)
        # return Response(generate(), mimetype='text/html')
        lon_1 = choice_1.split(' ')[0]
        lat_1 = choice_1.split(' ')[1]
        url_1 = '<a href="https://www.google.com/maps/place/'+str(lat_1)+','+str(lon_1)+'" target="_blank" rel="noopener noreferrer">click here</a>'
        # str_1 = 'Bushfire affected location suggested for you to explore out of the top locations closest to you: ' + url_1
        # return ('Minimum distance from the bushfire affected region in Victoria: ' + str(dist_bush) +' km. ' +str_1 + '. This might not be the closest location near you, but is one of the nearby locations compared to other such regions in Victoria with respect to your location.')
        dict_distance = {}
        list_distance = []
        dict_distance['distance'] = dist_bush
        dict_distance['explore'] = url_1
        list_distance.append(dict_distance)
        return dumps(list_distance)
    x,y = coords_inp.split(' ')
    x = float(x)
    y = float(y)
    c_1 = Point(x,y)
    list_dist_all = []
    dict_coords = dict()
    # yield('Your distance is being calculated...')
    for i in inter_bush_neigh_dissolve_geom.geometry[0]:
        j=0
        x, y = i.exterior.coords.xy
        for i in range(len(x)):
            # yield('Your distance is being calculated...')
            s = haversine(c_1.x, c_1.y, x[j], y[j])
            list_dist_all.append(s)
            dict_coords[round(s,2)] = str(x[j]) + ' ' + str(y[j])
            j+=1
    dist_bush = round(min(list_dist_all),2)
    od  = collections.OrderedDict(sorted(dict_coords.items()))
    list_1 = list(od.values())[:200:40]
    choice_1 = random.choice(list_1)
    # yield(dist_bush)
    # return Response(generate(), mimetype='text/html')
    lon_1 = choice_1.split(' ')[0]
    lat_1 = choice_1.split(' ')[1]
    url_1 = '<a href="https://www.google.com/maps/place/'+str(lat_1)+','+str(lon_1)+'" target="_blank" rel="noopener noreferrer">click here</a>'
    # str_1 = 'Bushfire affected location suggested for you to explore out of the top locations closest to you: ' + url_1
    # return ('Minimum distance from the bushfire affected region in Victoria: ' + str(dist_bush) +' km. ' +str_1 + '. This might not be the closest location near you, but is one of the nearby locations compared to other such regions in Victoria with respect to your location.')
    dict_distance = {}
    list_distance = []
    dict_distance['distance'] = dist_bush
    dict_distance['explore'] = url_1
    list_distance.append(dict_distance)
    return dumps(list_distance)

@app.route('/species/<string:coords_inp>')
def species_finder(coords_inp):
    x,y = coords_inp.split(' ')
    x = float(x)
    y = float(y)
    c_1 = Point(x,y)
    j = 0
    list_found =[]
    for i in range(len(species_vic_also_mod_con)):
        try:
            if c_1.within(species_vic_also_mod_con.geometry[i]):
                list_found.append(j)
            j+=1
        except:
            if c_1.within(species_vic_also_mod_con.geometry[i].buffer(0)):
                list_found.append(j)
            j+=1

        # ## Subsetting our dataframe based on the species habitat in the user's location and selecting the columns of interest to be shown to the client side.
        #

        # In[14]:


    species_found = species_vic_also_mod_con[species_vic_also_mod_con.index.isin(list_found)].copy()
    df_found = species_found[['comm_name', 'tax_group','pres_rank', 'threatened']].copy()


        # In[15]:


        # print(len(df_found))


        # ## As per the data,
        #
        # ### pres_rank = 1 => corresponds to 'Species or species habitat may occur within area'
        #
        # ### pres_rank = 2 => corresponds to 'Species or species habitat is likely to occur within area'
        #

        # In[16]:


    df_found.loc[df_found['pres_rank'] =='1' , 'pres_rank'] = 'May Occur in this region'
    df_found.loc[df_found['pres_rank'] =='2' , 'pres_rank'] = 'Likely to Occur in this region'


        # ## Output to json format

        # In[17]:


    # out = df_found.to_json(orient='records')[1:-1]
    out = df_found.to_json(orient='records')
    return out



    # return render_template_string('''
    #
    #
    # <table>
    #         <tr>
    #             <td> comm_name </td>
    #             <td> tax_class </td>
    #             <td> pres_rank </td>
    #         </tr>
    #
    #
    # {% for key, value in out.items() %}
    #
    #         <tr>
    #             <td>{{ value }}</td>
    #             <td>{{ value }}</td>
    #             <td>{{ value }}</td>
    #         </tr>
    #
    # {% endfor %}
    #
    #
    # </table>
    # ''', labels=out)


if __name__=='__main__':
    app.run()

'''
Test Routes below:


@app.route('/greet')
def say_hello():
  return 'Hello from Server'

@app.route('/hello')
def hello():
  return 'Hello, greetings from different endpoint'

#adding variables
@app.route('/user/<username>')
def show_user(username):
  #returns the username
  return 'Username: %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
  #returns the post, the post_id should be an int
  return str(post_id)

'''
