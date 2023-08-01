import math
import requests
import io
import data
from pypdf import PdfReader
from geopy.geocoders import Nominatim
from fuel import Fuel

country_found = False
added_value = 0.06
is_Manual = False

geo = Nominatim(user_agent='MyApp')

country_wanted = input ('Which country do you live in? ').title()

# Request to EU government PDF with fuel prices.
def get_pdf() -> list[str]:
    response = requests.get('https://ec.europa.eu/energy/observatory/reports/latest_prices_with_taxes.pdf')
    f = io.BytesIO(response.content)
    reader = PdfReader(f)
    return reader.pages[1].extract_text().split('\n')

# Calculate the price based on the country of your choice.
def calculate_price(fuel_type : Fuel, each_country : list[str]) -> float:
    price = each_country[fuel_type.value].replace("," , '')
    return (float(price) / 1000) + added_value

# Request for a specific car to a DB.
def get_car() -> list[str]:
    car_url = "https://car-utils.p.rapidapi.com/fueleconomy"
    querystring = {"make":f"{car_maker}","model":f"{car_model}"}
    headers = {
        #sub_code will be the code that you receive once you subscribed to Disctante API at rapidapi.com
        "X-RapidAPI-Key": data.sub_code,
        "X-RapidAPI-Host": "car-utils.p.rapidapi.com"
    }
    car_response = requests.get(car_url, headers=headers, params=querystring)
    return car_response.json()

# Request for an API that returns time and distance between two points considering the roads.
def get_trip_info():
    trip_url = "https://distanceto.p.rapidapi.com/get"
    querystring = {"route":'[{\"t\":\"'+str(origin.latitude)+','+ str(origin.longitude)+'\"},{\"t\":\"'+str(destination.latitude)+','+ str(destination.longitude)+'\"}]',"car":"true"}
    headers = {
        #sub_code will be the code that you receive once you subscribed to Disctante API at rapidapi.com
        "X-RapidAPI-Key": data.sub_code,
        "X-RapidAPI-Host": "distanceto.p.rapidapi.com"
    }
    return requests.get(trip_url, headers=headers, params=querystring).text

# Calculate the final cost of the trip.
def get_final_price(distance : float, fuel : float, consumo : float) -> str:
    return f'Traveling {car_distance:.2f}Km will cost you {(distance*fuel*consumo):.2f}€ and will take you {int(hour)}h:{int(60*min)}min'

pdf = get_pdf()
# 17 and -16 are the numbers that represent the lines that cointain the countries in the given PDF.
for country in pdf[17:-16]:
    each_country = country.split(' ')
    country_name = each_country[0]
    if country_name == country_wanted:
        country_found = True
        gasoline = calculate_price(Fuel.GASOLINE, each_country)

        diesel = calculate_price(Fuel.DIESEL, each_country)
        
        if each_country[3] != 'N.A':
            gas = calculate_price(Fuel.GAS, each_country)
        else:
            gas = 0

        origin = geo.geocode(input('From where are you starting your trip? '))
        destination = geo.geocode(input('Where is your destination? '))
        gas_type = input ('Which fuel do you use? (95/oil/gas) ')
        car_info = input ('Which maker and model is your car? ').split(' ')
        car_maker = car_info[0]
        car_model = car_info[1]        
        
        json_car = get_car()

        if not isinstance(json_car, list):
            if 'not found' in json_car.values():
                answer = input('Car not found, do you want to put manually the fuel economy? (yes/no) ')
                if answer == 'yes':
                    ask_consumo = float(input('How many liters does your car consume at 100Km? '))
                    consumo = ask_consumo/100
                    is_Manual = True
                elif answer == 'no':
                    print('Closing program...')
                    exit()
                else:
                    print('Invalid answer')
                    exit()

        # Checking if car is inserted manually so json_car is not empty.
        if not is_Manual:            
            total_mpg = 0
            lenght = 0
            for car in json_car:
                if car['fuel_type'] != 'Electricity':
                    total_mpg += car['combined_mpg']
                    lenght += 1
            consumo = (235.215 / (total_mpg / lenght)) / 100

        # This would be "json_trip = get_trip_info()" but for testing reasons it has been changed to a stored data.
        json_trip = data.json_page
        car_trip_info = json_trip['steps'][0]['distance']['car']
        car_distance = float(car_trip_info['distance'] / 1000)
        car_duration = float(car_trip_info['duration'] / 3600)

        min, hour = math.modf(car_duration)

        if gas_type == '95':
            print(get_final_price(car_distance,gasoline,consumo))
        elif gas_type == 'oil':
            print(get_final_price(car_distance,diesel,consumo))
        elif gas_type == 'gas':
            if gas != 0:
                print(get_final_price(car_distance,gas,consumo))
            else:
                print('This fuel is not available in this country.')
        else:
            print('Fuel is not correct.')

if not country_found:
    print('Country not found.')