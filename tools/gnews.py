#! /usr/bin/python3

import logging as log
import os
import requests
import json
from typing import Dict, Any, Type
from pydantic import BaseModel, Field
from langchain.tools.base import BaseTool

log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


class HeadlinesInput(BaseModel):
    news_category: str = Field(
        default="general",
        description="News Category to fetch the headlines for. Must be one of general, world, \
        nation, business, technology, entertainment, sports, science or health. REMEMBER, any \
        category outside of this list will fall back to `general`. ",
    )
    country: str = Field(
        default="in",
        description="""Country code to fetch the headlines for. 'in' for India, \
        'us' for United States, 'gb' for United Kingdom. DO NOT USE ANY OTHER COUNTRY CODE.""",
    )


class HeadlinesTool(BaseTool):
    """Headlines tool for fetching news."""

    name: str = "headlines"
    args_schema: Type[BaseModel] = HeadlinesInput
    description: str = "Useful for when you need to fetch the top news headlines for a given category. \
                    Returns the result in the form of a json string. \
                    If you want to dive deeper into a particular news item, you can browse to the specified URL."

    def _run(
        self,
        news_category: str = "general",
        country: str = "in",
        # start_timestamp: str = None,
        # end_timestamp: str = None,
    ) -> str:
        """This method allows you to fetch the top headlines for a particular category and country.
        The result is returned in the form of a json string.

        Returns:
        str: Json string that contains the results of the query."""
        log.info(f"Fetching news for category=[{news_category}], country=[{country}].")
        return requests.get(
            "https://gnews.io/api/v4/top-headlines",
            params={
                "category": news_category,
                "lang": "en",
                "country": country,
                "max": 10,
                "apikey": GNEWS_API_KEY,
                "from": None,
                "to": None,
            },  # unused: `q`
        ).content

    async def _arun(
        self,
        news_category: str = "general",
        country: str = "in",
        # start_timestamp: str = None,
        # end_timestamp: str = None,
    ) -> str:
        raise NotImplementedError
