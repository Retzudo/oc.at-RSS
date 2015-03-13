#!./env/bin/python3
import datetime
import urllib.request
from bs4 import BeautifulSoup
from flask import Flask
from flask import jsonify
from flask import render_template
from flask.ext.cors import CORS, cross_origin

OCAT_URL = 'https://overclockers.at'
RECENT_RES = 'search.php?action=getdaily'

app = Flask(__name__)
cors = CORS(app)
app.config.update(
    JSONIFY_PRETTYPRINT_REGULAR=False,
    CORS_HEADERS='Content-Type',
)


def get_news_html():
    response = urllib.request.urlopen(OCAT_URL)
    return response.read()


def get_recent_html():
    response = urllib.request.urlopen("{}/{}".format(OCAT_URL, RECENT_RES))
    return response.read()


def parse_news():
    html = BeautifulSoup(get_news_html())
    news = []

    for item in html.find_all(class_="news"):
        a = item.find("h2").find("a")
        title = a.string
        link = OCAT_URL + a.get('href')
        description = item.find(class_='previewtext').text.strip()

        details = item.find(class_='details')
        author = details.contents[2].strip()
        date_string = details.contents[4].strip()
        date = datetime.datetime.strptime(date_string, '%d.%m.%Y')

        news.append({
            'title': title,
            'link': link,
            'description': description,
            'author': author,
            'date': date.date().isoformat(),
        })

    return news


def parse_recent():
    recent_posts = BeautifulSoup(get_recent_html())
    recent = [];

    for row in recent_posts.find(id='idThreadTable').find('tbody').find_all('tr'):
        a = row.find(class_='title').find('h5').find('a')
        title = a.text
        link = OCAT_URL + a.get('href')
        forum = row.find(class_='forum').find('a').text.strip()
        forum_link = OCAT_URL + row.find(class_='forum').find('a').get('href')
        starter = row.find(class_='starter').find('a').text.strip()
        starter_link = OCAT_URL + row.find(class_='starter').find('a').get('href')
        last_post = row.find(class_='lastpost')
        last_post_date_string = last_post.contents[0].strip()
        last_post_date = datetime.datetime.strptime(last_post_date_string, '%d.%m.%Y %H:%M')
        last_post_by = last_post.contents[1].contents[1].text
        last_post_by_link = OCAT_URL + last_post.contents[1].contents[1].get('href')
        last_post_link = OCAT_URL + last_post.contents[1].contents[3].get('href')

        recent.append({
            'title': title,
            'link': link,
            'forum': {
                'name': forum,
                'link': forum_link,
            },
            'starter': {
                'name': starter,
                'link': starter_link,
            },
            'lastPost': {
                'by': {
                    'name': last_post_by,
                    'link': last_post_by_link,
                },
                'date': last_post_date.isoformat(),
                'link': last_post_link,
            },
        })

    return recent

@app.route('/')
def index():
    news = parse_news()
    return render_template('rss2.0.xml', news=news)


@app.route('/news.json')
@cross_origin()
def news():
    return jsonify(news=parse_news())


@app.route('/recent.json')
@cross_origin()
def recent():
    return jsonify(threads=parse_recent())


if __name__ == '__main__':
    app.run(debug=True)
