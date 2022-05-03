from __future__ import annotations
from abc import ABC
from dotenv import load_dotenv
import os, requests
from git_repos_list import Context, Strategy

load_dotenv("./.env")
KELVIN = 273


class SpecialStrategy(Strategy, ABC):
    """Use git_repos_list docs"""

    def __init__(self) -> None:
        self.username = None
        self.city = SpecialStrategy.get_city()
        self.api_key = os.getenv('KEY')
        self._url = f'https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}'

    @staticmethod
    def get_city() -> str:
        city = input('Введите название города на английском: ')
        return city


class StrategyGet(SpecialStrategy):
    """http-GET method"""

    def do_algorithm(self) -> str:
        url = self._url
        r = requests.get(url).json()
        return f'Температура в {self.city}: {round(float(r["main"]["temp"]) - KELVIN, 2)} по цельсию, состояние неба - {r["weather"][0]["main"]}'


if __name__ == "__main__":
    context = Context(StrategyGet())
    print("Client: Strategy is http-GET")
    context.do_some_http_req_magic()
