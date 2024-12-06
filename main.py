import json
import requests
import os
import folium
from dotenv import load_dotenv
from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lat, lon = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(shop):
        return shop['distance']


def main():
    with open("coffee.json", "r", encoding="CP1251") as file:
        shops_json = file.read()

    load_dotenv(dotenv_path='tokens.env')

    shops = json.loads(shops_json)

    api_key = os.environ['API_KEY']

    place = input('Где вы находитесь? ')
    current_place = fetch_coordinates(api_key, place)

    distance_shops = []

    for shop in shops:
        shop_name = shop['Name']
        shop_coordinates = shop['geoData']['coordinates']
        shop_lat, shop_lon = shop_coordinates[1], shop_coordinates[0] 
        shop_distance = distance.distance(current_place, (shop_lat, shop_lon)).km

        distance_shops.append({
            'title': shop_name,
            'distance': shop_distance,
            'latitude': shop_lat,
            'longitude': shop_lon
        })

    sorted_shop = sorted(distance_shops, key=get_distance)[:5]

    m = folium.Map(location=(current_place), zoom_start=15)

    for i in range(5):
        folium.Marker(
            location=[sorted_shop[i]['latitude'], sorted_shop[i]['longitude']],
            popup=sorted_shop[i]['title'],
            icon=folium.Icon(color="green"),
        ).add_to(m)

    m.save("index.html")


if __name__ == "__main__":
    main()