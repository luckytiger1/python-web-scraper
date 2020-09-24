from requests import get
from bs4 import BeautifulSoup
from warnings import warn
from time import sleep
from random import randint
import numpy as np
import pandas as pd

# can only go to 10000 items because after that the URI ha no discernable distinction
# pages = np.arange(4001, 5000, 50)
pages = np.arange(1, 500, 50)

print(pages)

# initialize empty lists to store the variables scraped
titles = []
years = []
ratings = []
genres = []
runtimes = []
imdb_ratings = []
metascrores = []
votes = []
grosses = []

iterations = 0

imdb_genre = 'comedy'

for page in pages:

    # get request
    response = get("https://www.imdb.com/search/title?genres="
                   + imdb_genre
                   + "&start="
                   + str(page)
                   + "&explore=title_type,genres&ref_=adv_prv")

    # print(response)

    # sleep(randint(8, 15))

    # throw warning for status codes that are not 200
    if response.status_code != 200:
        warn('Request: {}; Status code:{}'.format(
            requests, response.status_code))

    # parse the content of current iteration of request
    # page_html = BeautifulSoup(response.text, 'html.parser')
    page_html = BeautifulSoup(response.text, 'lxml')

    # print(page_html.prettify())

    movie_containers = page_html.find_all(
        'div', class_='lister-item mode-advanced')
    # print(movie_containers)
    # extract the 50 movies for that page
    for container in movie_containers:

        # conditional for all with metascore
        # if container.find('div', class_='ratings-metascore') is not None:

        # title
        title = container.h3.a.text
        titles.append(title)

        # year released
        year = container.h3.find(
            'span', class_='lister-item-year text-muted unbold').text
        years.append(year)

        # rating
        if container.p.find('span', class_='certificate') != None:
            rating = container.p.find('span', class_='certificate').text
            ratings.append(rating)
        else:
            rating = None
            ratings.append(rating)

        # genre
        if container.p.find('span', class_='certificate') != None:
            genre = container.p.find('span', class_='genre').text
            genres.append(genre)
        else:
            genre = None
            genres.append(genre)

        # runtime

        if container.p.find('span', class_='runtime') != None:
            time = container.p.find('span', class_='runtime').text
            runtimes.append(time)
        else:
            time = None
            runtimes.append(time)

        # IMDB ratings
        if container.strong != None:
            imdb = float(container.strong.text)
            imdb_ratings.append(imdb)
        else:
            imdb = None
            imdb_ratings.append(imdb)

        # # Metascore
        # m_score = container.find('span', class_='metascore').text
        # metascrores.append(int(m_score))

        # Number of votes
        if(container.find_all('span', attrs={'name': 'nv'})):
            vote = container.find_all('span', attrs={'name': 'nv'})[
                0]['data-value']
            votes.append(int(vote))
        else:
            votes.append(None)

        # Total gross
        if(len(container.find_all('span', attrs={'name': 'nv'})) == 2):
            gross = container.find_all('span', attrs={'name': 'nv'})[
                1]['data-value']
            grosses.append(int(gross.replace(',', '')))
        else:
            grosses.append(None)

        iterations += 1
        print("Finished iteration: " + str(iterations))


sci_fi_df = pd.DataFrame({'movie': titles,
                          'year': years,
                          'rating': ratings,
                          'genre': genres,
                          'runtime': runtimes,
                          'imdb': imdb_ratings,
                          #   'metascore': metascrores,
                          'votes': votes,
                          'grosses': grosses
                          })

# remove the parenthesis at the front and the end of the year and turn them into integers
sci_fi_df.loc[:, 'year'] = sci_fi_df['year'].astype(
    str).str[-5:-1].astype(int, copy=True, errors='ignore')


# standardize the IMDB score so that it is comparable to the scale of the other one
# sci_fi_df['n_imdb'] = sci_fi_df['imdb'] * 10

# remove " min" from the end of the runtime variable and make them integers
sci_fi_df['runtime_min'] = sci_fi_df['runtime'].apply(
    lambda x: '' if x is None else x.replace(" min", "")).apply(lambda x: 0 if x is '' else int(x))

# drop the old runtime column
sci_fi_df.drop(columns='runtime', axis=1, inplace=True)

# remove the "\n" at the beginning of the genres
sci_fi_df['genre'] = sci_fi_df['genre'].apply(
    lambda x: '' if x is None else x.replace("\n", ""))

# after standardizing the imdb variable, it became a float. We don't need it to be so I made it an int
# sci_fi_df['n_imdb'] = sci_fi_df['n_imdb'].apply(
#     lambda x: int(x))

# I found that there was whitespace in the arrays of genres so I removed that with .rstrip()
sci_fi_df['genre'] = sci_fi_df['genre'].apply(
    lambda x: '' if x is None else x.rstrip())

# split the string list into an actual array of values to do NLP on later
sci_fi_df['genre'] = sci_fi_df['genre'].astype(str).str.split(",")

# write the final dataframe to the working directory
sci_fi_df.to_csv("Talk-Show-movies.csv", index=False)


def check_if_null(sel):
    return sel != None
