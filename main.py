import requests
import json
import io
from pypdf import PdfReader
from geopy.geocoders import Nominatim
from vincenty import vincenty

country_found = False

url = "https://distanceto.p.rapidapi.com/get"

querystring = {"route":"[{\"t\":\"52.5597, 13.2877\"},{\"t\":\"Barcelona\"}]","car":"true"}

headers = {
	"X-RapidAPI-Key": "0633413946msh2052f9e7d584db6p1595d2jsnd8ee7f654313",
	"X-RapidAPI-Host": "distanceto.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring).text
json_text = json.loads(response)
car_info = json_text['steps'][0]['distance']['car']
car_distance = float(car_info['distance'] / 1000)
car_duration = float(car_info['duration'] / 3600)

print(f'{car_distance:.2f} {car_duration:.2f}')

'''response = requests.get('https://ec.europa.eu/energy/observatory/reports/latest_prices_with_taxes.pdf')
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
        gasolina = float(gasolina_price) / 1000
        
        diesel_price = each_country[2].replace("," , '')
        diesel = float(diesel_price) / 1000
        
        if each_country[3] != 'N.A':
            gas_price = each_country[3].replace("," , '')
            gas = float(gas_price) / 1000
        else:
            gas = 0

        origin = geo.geocode(input('From where are you starting your trip? '))
        destination = geo.geocode(input('Where is your destination? '))
        distance = vincenty((origin.latitude,origin.longitude),(destination.latitude,destination.longitude))
        gas_type = input ('Which fuel do you use? (95/oil/gas) ')
        ask_consumo = float(input('How many liters does your car consume at 100Km? '))

        consumo = ask_consumo/100

        if gas_type == '95':
            print(f'Traveling {distance:.2f} Km will cost you {(distance*gasolina*consumo):.2f}€')
        elif gas_type == 'oil':
            print(f'Traveling {distance:.2f} Km will cost you {(distance*diesel*consumo):.2f}€')
        elif gas_type == 'gas':
            if gas != 0:
                print(f'Traveling {distance:.2f} Km will cost you {(distance*gas*consumo):.2f}€')
            else:
                print('This fuel is not available in this country.')
        else:
            print('Fuel is not correct.')

if not country_found:
    print('Country not found.')'''