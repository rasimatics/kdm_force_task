import csv
import requests

URL = "https://booking-com.p.rapidapi.com/v1/hotels/"
HEADERS = {
	"X-RapidAPI-Host": "booking-com.p.rapidapi.com",
	"X-RapidAPI-Key": "aa91bbe60bmsh2a1c5221f029c7ap1b2c3ajsnf907a098ce42"
}

CSV_HEADERS = [
    "Hotel ID",
    "Hotel name",
    "Hotel URL",
    "Stars (class)",
    "x,y coordinates",
    "pros",
    "cons",
    "author ID",
    "creation_date"
]


def prepare_csv(result_file, header, rows):
    """
        Fill csv file with given header and rows
    """
    writer = csv.writer(result_file)
    writer.writerow(header)
    for row in rows:
        writer.writerow(list(row.values()))


def get_city_id(city_name: str):
    """
        Get city id from city name and return it
    """
    querystring = {"locale": "en-gb", "name": f"{city_name}"}
    response = requests.request(
        "GET", URL + "locations", headers=HEADERS, params=querystring)

    for i in response.json():
        if i['dest_type'] == 'city':
            return i['dest_id']

    return None


def get_hotels_data(city_id: int):
    """
        Get hotel data and reviews for given city_id
    """
    querystring = {"checkout_date": "2022-10-01", "units": "metric", "dest_id": f"{city_id}", "dest_type": "city", "locale": "en-gb", "adults_number": "2", "order_by": "popularity", "filter_by_currency": "AED",
                   "checkin_date": "2022-09-30", "room_number": "1", "children_number": "2", "page_number": "0", "children_ages": "5,0", "categories_filter_ids": "class::2,class::4,free_cancellation::1", "include_adjacency": "true"}
    response = requests.request(
        "GET", URL + "search", headers=HEADERS, params=querystring)
    result = response.json()['result']
    counter = min(len(result), 20)
    res = []

    for i in range(counter):
        r = result[i]
        reviews = get_hotel_reviews(r.get('hotel_id', None))
        for re in reviews:
            hotel_data = {'id': r['hotel_id'], 'name': r['hotel_name'], 'url': r['url'],
                          'cls': r['class'], 'x': r['longitude'], 'y': r['latitude']}
            review_data = {'pros': re['pros'], 'cons': re['cons'],
                           'author_id': re['author_id'], 'date': re['date']}
            res.append({**hotel_data, **review_data})
    return res


def get_hotel_reviews(hotel_id):
    """
        Get reviews for given hotel_id
    """
    print('Processing reviews for hotel_id =', hotel_id)
    querystring = {"sort_type": "SORT_MOST_RELEVANT", "locale": "en-gb", "hotel_id": f"{hotel_id}",
                   "language_filter": "en-gb,de,fr", "customer_type": "solo_traveller,review_category_group_of_friends"}
    response = requests.request(
        "GET", URL + "reviews", headers=HEADERS, params=querystring)
    reviews = response.json()['result']
    res = []
    for re in reviews:
        obj = {'pros': re['pros'], 'cons': re['cons'],
               'author_id': re['author']['user_id'], 'date': re['date']}
        res.append(obj)
    return res


if __name__ == "__main__":
    """
        Run all functions
    """
    city_id = get_city_id("Jeddah")
    if not city_id:
        raise("City not found")

    hotels_data = get_hotels_data(city_id)
    result_file = open("result.csv", "w", encoding='UTF-8')
    prepare_csv(result_file, CSV_HEADERS, hotels_data)
