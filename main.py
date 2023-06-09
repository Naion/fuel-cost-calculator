import math
import requests
import json
import io
import data
from pypdf import PdfReader
from geopy.geocoders import Nominatim
from vincenty import vincenty

country_found = False

response = requests.get('https://ec.europa.eu/energy/observatory/reports/latest_prices_with_taxes.pdf')
f = io.BytesIO(response.content)
reader = PdfReader(f)
contents = reader.pages[1].extract_text().split('\n')

geo = Nominatim(user_agent='MyApp')

country_wanted = input ('Which country do you live in? ').title()

for country in contents[17:-16]:
    each_country = country.split(' ')
    country_name = each_country[0]    
    if country_name == country_wanted:
        country_found = True
        gasolina_price = each_country[1].replace("," , '')
        gasolina = (float(gasolina_price) / 1000) + 0.06
        
        diesel_price = each_country[2].replace("," , '')
        diesel = (float(diesel_price) / 1000) + 0.06
        
        if each_country[3] != 'N.A':
            gas_price = each_country[3].replace("," , '')
            gas = (float(gas_price) / 1000) + 0.06
        else:
            gas = 0

        origin = geo.geocode(input('From where are you starting your trip? '))
        destination = geo.geocode(input('Where is your destination? '))
        gas_type = input ('Which fuel do you use? (95/oil/gas) ')
        car_info = input ('Which maker and model is your car? ').split(' ')
        car_maker = car_info[0]
        car_model = car_info[1]
        
        car_url = "https://car-utils.p.rapidapi.com/fueleconomy"
        querystring = {"make":f"{car_maker}","model":f"{car_model}"}
        headers = {
            #sub_code will be the code that you receive once you subscribed to Disctante API at rapidapi.com
            "X-RapidAPI-Key": data.sub_code,
            "X-RapidAPI-Host": "car-utils.p.rapidapi.com"
        }
        car_response = requests.get(car_url, headers=headers, params=querystring)
        json_car = car_response.json()

        if not isinstance(json_car, list):
            if 'not found' in json_car.values():
                answer = input('Car not found, do you want to put manually the fuel economy? (yes/no) ')
                if answer == 'yes':
                    ask_consumo = float(input('How many liters does your car consume at 100Km? '))
                    consumo = ask_consumo/100
                elif answer == 'no':
                    print('Closing program...')
                    exit()
                else:
                    print('Invalid answer')
                    exit()
                    
        total_mpg = 0
        lenght = 0
        for car in json_car:
            if car['fuel_type'] != 'Electricity':
                total_mpg += car['combined_mpg']
                lenght += 1
        consumo = (235.215 / (total_mpg / lenght)) / 100

        trip_url = "https://distanceto.p.rapidapi.com/get"
        querystring = {"route":'[{\"t\":\"'+str(origin.latitude)+','+ str(origin.longitude)+'\"},{\"t\":\"'+str(destination.latitude)+','+ str(destination.longitude)+'\"}]',"car":"true"}
        headers = {
            #sub_code will be the code that you receive once you subscribed to Disctante API at rapidapi.com
            "X-RapidAPI-Key": data.sub_code,
            "X-RapidAPI-Host": "distanceto.p.rapidapi.com"
        }
        trip_response = requests.get(trip_url, headers=headers, params=querystring).text
        json_trip = data.json_page
        car_trip_info = json_trip['steps'][0]['distance']['car']
        car_distance = float(car_trip_info['distance'] / 1000)
        car_duration = float(car_trip_info['duration'] / 3600)

        min, hour = math.modf(car_duration)

        if gas_type == '95':
            print(f'Traveling {car_distance:.2f}Km will cost you {(car_distance*gasolina*consumo):.2f}€ and will take you {int(hour)}h:{int(60*min)}min')
        elif gas_type == 'oil':
            print(f'Traveling {car_distance:.2f}Km will cost you {(car_distance*diesel*consumo):.2f}€ and will take you {int(hour)}h:{int(60*min)}min')
        elif gas_type == 'gas':
            if gas != 0:
                print(f'Traveling {car_distance:.2f}Km will cost you {(car_distance*gas*consumo):.2f}€ and will take you {int(hour)}h:{int(60*min)}min')
            else:
                print('This fuel is not available in this country.')
        else:
            print('Fuel is not correct.')

if not country_found:
    print('Country not found.')