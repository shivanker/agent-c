#! /usr/bin/python3

import logging as log
import os
import requests
import json
from typing import Dict, Any
from pydantic import BaseModel, Field

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


class HeadlinesInput(BaseModel):
    news_category: str = Field()
    "News Category to fetch the headlines for. Must be one of general, world, nation, business, technology, entertainment, sports, science or health."


def top_headlines(
    news_category: str,
    # country: str = "in",
    # start_timestamp: str = None,
    # end_timestamp: str = None,
) -> str:  # Dict[str, Any]:
    """This method allows you to fetch the top headlines for a particular category and country.
    The result is returned in the form of a json string.
    Parameters:
    news_category (str): News category that you need the headlines for. This must be one of general, world, nation, business, technology, entertainment, sports, science or health.

    Returns:
    str: Json string that contains the results of the query."""
    log.info(f"Fetching news for category=[{news_category}], country=[us].")
    return requests.get(
        "https://gnews.io/api/v4/top-headlines",
        params={
            "category": news_category,
            "lang": "en",
            "country": "us",
            "max": 10,
            "apikey": GNEWS_API_KEY,
            "from": None,
            "to": None,
        },  # unused: `q`
    ).content
