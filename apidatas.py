import requests
import os

def getratings(isbn):
    if not os.getenv("API_KEY"):
        raise RuntimeError("API_KEY missing")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("API_KEY"), "isbns": isbn })
    datajson = res.json()
    numberofratings = datajson['books'][0]['work_ratings_count']
    averagerating = datajson['books'][0]['average_rating']
    return numberofratings,averagerating


