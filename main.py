import requests
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask

cred = credentials.Certificate("serviceacckey.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)


def save_api_key(api_key):
  with open('api_key.json', 'w') as key_file:
    json.dump({"key": api_key}, key_file)


def load_api_key():
  try:
    with open('api_key.json', 'r') as key_file:
      data = json.load(key_file)
      return data.get("key", None)
  except FileNotFoundError:
    return None


def convert_to_lower_no_spaces(s):
  return s.lower().replace(" ", "")


# Read city names from a file
city_names = []
with open('city_zip.txt', 'r') as file:
  for line in file:
    city_names.append(line.strip())

api_key = load_api_key()

if not api_key:
  api_key = input("Enter your WeatherAPI key: ")
  save_api_key(api_key)

api_url = "http://api.weatherapi.com/v1/current.json"
aqi = "yes"


def get_air():
  for location in city_names:
    params = {"key": api_key, "q": location, "aqi": aqi}

    try:
      response = requests.get(api_url, params=params)

      if response.status_code == 200:
        data = response.json()

        location = data['location']
        current = data['current']
        name = location['name']
        country = location['country']
        lon = location['lon']
        lat = location['lat']
        localtime = location['localtime']
        localtime_datetime = datetime.strptime(localtime, "%Y-%m-%d %H:%M")
        date = localtime_datetime.strftime("%Y-%m-%d")
        time = localtime_datetime.strftime("%H:%M")
        temp_c = current['temp_c']
        temp_f = current['temp_f']
        condition_text = current['condition']['text']
        wind_kph = current['wind_kph']
        wind_degree = current['wind_degree']
        wind_dir = current['wind_dir']
        pressure_mb = current['pressure_mb']
        precip_mm = current['precip_mm']
        humidity = current['humidity']
        cloud = current['cloud']
        vis_km = current['vis_km']
        uv = current['uv']
        gust_kph = current['gust_kph']
        air_quality = current['air_quality']
        co = air_quality['co']
        no2 = air_quality['no2']
        o3 = air_quality['o3']
        so2 = air_quality['so2']
        pm2_5 = air_quality['pm2_5']
        pm10 = air_quality['pm10']
        us_epa_index = air_quality['us-epa-index']
        gb_defra_index = air_quality['gb-defra-index']

        extracted_data = {
            "name": convert_to_lower_no_spaces(name),
            "country": convert_to_lower_no_spaces(country),
            "latitude": lat,
            "longitude": lon,
            "date": date,
            "time": time,
            "temperature_c": temp_c,
            "temperature_f": temp_f,
            "condition": convert_to_lower_no_spaces(condition_text),
            "wind_speed_kph": wind_kph,
            "wind_degree": wind_degree,
            "wind_direction": convert_to_lower_no_spaces(wind_dir),
            "pressure_mb": pressure_mb,
            "precipitation_mm": precip_mm,
            "humidity": humidity,
            "cloud_cover": cloud,
            "visibility_km": vis_km,
            "uv_index": uv,
            "gust_speed_kph": gust_kph,
            "co": co,
            "no2": no2,
            "o3": o3,
            "so2": so2,
            "pm2_5": pm2_5,
            "pm10": pm10,
            "us_epa_index": us_epa_index,
            "gb_defra_index": gb_defra_index
        }

        extracted_data_json = json.dumps(extracted_data, indent=4)
        # print(f"Data for {location}:\n{extracted_data_json}")

        db = firestore.client()
        doc_ref = db.collection('hourlyData').document()
        doc_ref.set(extracted_data)
        print("Document ID:", doc_ref.id)
        print(time)

      else:
        print(
            f"Request for {location} failed with status code: {response.status_code}"
        )
    except requests.RequestException as e:
      print(f"Request for {location} failed: {e}")


@app.route('/')
def hello():
  get_air()
  return 'Hello, World!'


app.run(host='0.0.0.0')
