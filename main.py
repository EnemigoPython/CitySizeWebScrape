from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import unicodedata


class City:
    pass


# parse data
def new_soup(url):
    client = urlopen(url)
    html_page = client.read()
    client.close()
    page_soup = soup(html_page, "html.parser")
    return page_soup


my_url = 'https://en.wikipedia.org/wiki/List_of_largest_cities#List'
page_soup = new_soup(my_url)

# find/dissect table
text_part = page_soup.find("div", {"class": "mw-parser-output"})
wiki_table = text_part.find("table", {"class": "wikitable"})
headers = wiki_table.find_all('th')
body = wiki_table.find("tbody")
rows = body.find_all("tr")

categories = []
col_dict = {}
header_exceptions = []
for num, header in enumerate(headers):
    try:
        header.sup.decompose()
    except AttributeError:
        pass
    try:
        # if the header has subcategories and spans many columns, save the text to use with the subheader
        col_span = int((header['colspan']))
        col_dict.update({header.text: col_span})
    except KeyError:
        if len(col_dict) > 0:
            if list(col_dict.values())[0] > 0:
                categories.append(f"{list(col_dict.keys())[0]} * {header.text}")
                col_dict[list(col_dict.keys())[0]] -= 1
            else:
                col_dict.pop(list(col_dict.keys())[0])
                if list(col_dict.values())[0] > 0:
                    categories.append(f"{list(col_dict.keys())[0]} * {header.text}")
                    col_dict[list(col_dict.keys())[0]] -= 1
        else:
            try:
                # if the header is for non-text categories such as images, mark the column as unusable/to ignore
                if header["class"] == ['unsortable']:
                    header_exceptions.append(num)
                else:
                    categories.append(header.text)
            except KeyError:
                categories.append(header.text)

categories = [" ".join(category.split()) for category in categories]

cities = []

for row in rows:
    panels = row.find_all("td")
    cities.append(City())
    category_num = 0
    for num, panel in enumerate(panels):
        if num in header_exceptions:
            continue
        try:
            panel.sup.decompose()
        except AttributeError:
            pass
        try:
            text = " ".join(panel.text.split())
            if text == "":
                setattr(cities[-1], categories[category_num], 'N/A')
            else:
                # save numbers as type int where possible to allow for sorting
                if text.replace(',', '').isnumeric():
                    setattr(cities[-1], categories[category_num], int(text.replace(',', '')))
                    if not hasattr(cities[-1], 'pop'):
                        setattr(cities[-1], 'pop', int(text.replace(',', '')))
                else:
                    setattr(cities[-1], categories[category_num], text)
            category_num += 1
        except AttributeError:
            pass
    if not hasattr(cities[-1], 'City'):
        cities.remove(cities[-1])


def with_commas(val):
    return "{:,}".format(val)


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


# assumption that City/Country remains in wiki table
pop_categories = [category for category in categories if category != 'City']
while True:
    user = input('''Type "A" for cities, "B" for categories
''')
    if user.upper() == "A":
        user = input('''Number of results? (type anything for all)
''')
        if user.isnumeric() and int(user) < len(cities):
            for rank, city in enumerate(cities[:int(user)], 1):
                print(
                    f'{rank}) {getattr(city, "City")}, {getattr(city, "Country")} (Pop: {with_commas(getattr(city, "pop"))})')
            print(f'Showing {int(user)} results.')
        else:
            for rank, city in enumerate(cities, 1):
                print(
                    f'{rank}) {getattr(city, "City")}, {getattr(city, "Country")} (Pop: {with_commas(getattr(city, "pop"))})')
            print(f'Showing {len(cities)} results.')
        print("Type a city to view its data.")
    elif user.upper() == "B":
        for num, category in enumerate(pop_categories):
            print(f'{category} [{num}]')
        print('Type the corresponding number to view the data, which will be ordered if possible.')
    elif user.isnumeric() and int(user) in range(len(pop_categories)):
        chosen_category = pop_categories[int(user)]
        user = input('''Number of results? (type anything for all)
''')
        print(chosen_category)
        if chosen_category == 'Country':
            country_dict = {}
            for city in cities:
                if getattr(city, 'Country') in country_dict.keys():
                    country_dict[getattr(city, 'Country')] += 1
                else:
                    country_dict.update({getattr(city, 'Country'): 1})
            sorted_countries = sorted(country_dict, key=country_dict.get, reverse=True)
            for country in sorted_countries:
                print(f'{country_dict.get(country)} cities from {country}')
            print(f'Showing {len(country_dict)} countries from list.')
        else:
            if type(getattr(cities[0], chosen_category)) == int:
                sorted_cities = sorted([city for city in cities if hasattr(city, chosen_category) and
                                        type(getattr(city, chosen_category)) == int],
                                       key=lambda i: getattr(i, chosen_category), reverse=True)
                if user.isnumeric() and int(user) < len(sorted_cities):
                    for rank, city in enumerate(sorted_cities[:int(user)], 1):
                        print(
                            f'{rank}) {getattr(city, "City")}, {getattr(city, "Country")} ({with_commas(getattr(city, chosen_category))})')
                    print(f'Showing {user} results for {chosen_category}.')
                else:
                    for rank, city in enumerate(sorted_cities, 1):
                        print(
                            f'{rank}) {getattr(city, "City")}, {getattr(city, "Country")} ({with_commas(getattr(city, chosen_category))})')
                    print(f'Showing {len(sorted_cities)} results for {chosen_category}.')
            else:
                if user.isnumeric() and int(user) < len(cities):
                    for rank, city in enumerate(cities[:int(user)], 1):
                        print(
                            f'{rank}) {getattr(city, "City")}, {getattr(city, "Country")} ({getattr(city, chosen_category)})')
                    print(f'Showing {user} results for {chosen_category}.')
                else:
                    for rank, city in enumerate(cities, 1):
                        print(
                            f'{rank}) {getattr(city, "City")}, {getattr(city, "Country")} ({getattr(city, chosen_category)})')
                    print(f'Showing {len(cities)} results for {chosen_category}.')
            print("Type a city to view its data.")
    else:
        if any(getattr(city, 'City') == user for city in cities) or any(strip_accents(getattr(city, 'City')) == user for city in cities):
            try:
                chosen_city = [city for city in cities if getattr(city, 'City') == user][0]
            except IndexError:
                chosen_city = [city for city in cities if strip_accents(getattr(city, 'City')) == user][0]
            for category in categories:
                if type(getattr(chosen_city, category)) == int:
                    print(f'{category}: {with_commas(getattr(chosen_city, category))}')
                else:
                    print(f'{category}: {getattr(chosen_city, category)}')
            my_url = f'https://en.wikipedia.org/wiki/{getattr(chosen_city, "City")}'
            my_url = '_'.join(my_url.split())
            my_url = strip_accents(my_url)
            print(my_url)
            page_soup = new_soup(my_url)
            main_body = page_soup.find("body")
            text_part = main_body.find(id="mw-content-text")
            all_paragraphs = text_part.find_all("p")
            paragraphs = all_paragraphs[:3]
            for paragraph in paragraphs:
                try:
                    sups = paragraph.find_all("sup")
                    for sup in sups:
                        sup.decompose()
                except AttributeError:
                    pass
                text = " ".join(paragraph.text.split())
                if len(text) > 0:
                    print(text)
        else:
            print(f'No cities with the name {user} found.')
