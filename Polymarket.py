import operator
import re
from typing import Dict, Generator, List, Tuple

import requests
from fuzzywuzzy import fuzz


def _get_name_matches(name: str, guess_words: List[str]) -> int:
    matches = sum(word in name for word in guess_words)
    return matches


def _get_name_score(names: List[str], guess: str) -> int:
    names = [re.sub(r"[^\w\s]", "", name).lower() for name in names]
    guess_words = guess.split()
    matches = max(_get_name_matches(name, guess_words) for name in names)
    diff = max(fuzz.token_sort_ratio(guess, name) for name in names)
    return matches * 100 + diff


def _check_question(question: "PolyQuestion", guess: str) -> Tuple[int, int]:
    return question.id, _get_name_score([question.question], guess)


def _get_best_question_id(poly: "Poly", guess: str) -> int:
    return max(
        (_check_question(question, guess) for question in poly.questions),
        key=operator.itemgetter(1),
    )[0]


def search_question(poly: "Poly", guess: str) -> "PolyQuestion":
    return poly.get_question(_get_best_question_id(poly, guess))


class PolyQuestion:
    def __init__(self, poly: "Poly", data: Dict):
        self.poly = poly
        self._data = data
        self.api_url = f"{self.poly.api_url}?id={self.id}/"

    def _get(self, url: str) -> requests.Response:
        """
        Send a get request to the Polymarket API.
        :param url:
        :return: response
        """
        r = self.predictit.s.get(url)
        if r.status_code == 429:
            raise requests.RequestException("Hit API rate limit")
        return r

    @property
    def name(self):
        return self.question

    def __getattr__(self, name: str):
        if name not in self._data:
            raise AttributeError(
                f"Attribute {name} is neither directly on this class nor in the raw question data"
            )
        return self._data[name]

    def refresh(self):
        """
        Refetch the market data from Polymarket,
        used when the question data might have changed.
        """
        r = self._get(self.api_url)
        self._data = r.json()


class Poly:
    def __init__(self):
        self.api_url = "https://strapi-matic.poly.market/markets"
        self.s = requests.Session()
        self._data = self._get(self.api_url).json()

    def _get(self, url: str) -> requests.Response:
        r = self.s.get(url)
        if r.status_code == 429:
            raise requests.RequestException("Hit API rate limit")
        return r

    def refresh_markets(self):
        self._data = self._get(self.api_url).json()

    @property
    def questions(self) -> Generator[PolyQuestion, None, None]:
        for data in self._data:
            yield PolyQuestion(self, data)

    def get_question(self, id: int) -> PolyQuestion:
        for data in self._data:
            if data["id"] == id:
                return PolyQuestion(self, data)
        raise ValueError("Unable to find a market with that ID.")

    def search_questions(self, guess: str) -> PolyQuestion:
        return search_question(self, guess.lower())
