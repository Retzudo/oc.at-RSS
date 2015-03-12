#!./env/bin/python3
import datetime
import urllib.request
from bs4 import BeautifulSoup
from flask import Flask
from flask import render_template

OCAT_URL = "https://overclockers.at"

app = Flask(__name__)


def get_ocat_html():
    response = urllib.request.urlopen(OCAT_URL)
    return response.read()


def parse_news():
    html = BeautifulSoup(get_ocat_html())
    news = []

    for item in html.find_all(class_="news"):
        a = item.find("h2").find("a")
        title = a.string
        link = OCAT_URL + a.get('href')
        description = item.find(class_='previewtext').text.strip()

        details = item.find(class_='details')
        author = details.contents[2].strip()
        date_string = details.contents[4].strip()

        news.append({
            'title': title,
            'link': link,
            'description': description,
            'author': author,
            'date': date_string,
        })

    return news


@app.route('/')
def index():
    news = parse_news()
    return render_template('rss2.0.xml', news=news)


if __name__ == '__main__':
    app.run(debug=True)
