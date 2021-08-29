import time
from datetime import datetime
from pytrends.request import TrendReq
from .scraper import main

# Timezone for trends
ts = time.time()
utc_offset = (datetime.fromtimestamp(ts) -
        datetime.utcfromtimestamp(ts)).total_seconds()
utc_offset = int(abs(utc_offset/60))

# Pytrends
pytrends = TrendReq(hl='en-US', tz=utc_offset)
CATEGORIES = pytrends.categories()

def related_queries(terms, geo):
    related_queries = list()
    for term in terms:
        pytrends.build_payload(kw_list=[term], timeframe='today 1-m', geo=geo)
        df = pytrends.related_queries()
        related_queries.append(df)
    return related_queries

def related_topics(terms, geo):
    related_topics = list()
    for term in terms:
        pytrends.build_payload(kw_list=[term], timeframe='today 1-m', geo=geo)
        df = pytrends.related_topics()
        related_topics.append(df)
    return related_topics

def get_recommendations(webpages):
    terms = main(webpages)
    queries = related_queries(terms, 'US')
    topics = related_topics(terms, 'US')
    return queries, topics