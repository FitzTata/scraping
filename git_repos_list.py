from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

import requests


class Context():
    """Defining client if"""

    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> Strategy:
        """Link to strategy object. context have no idea about concrete strategy used"""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def do_some_http_req_magic(self) -> None:
        """Delegating work to strategy"""
        print("Context: Do some type of some http request, not sure which 1")
        result = self._strategy.do_algorithm()
        print(result)


class Strategy(ABC):
    """Init some common operations for all strategies. Context uses this if to call algo defined special strategies"""

    @abstractmethod
    def do_algorithm(self, request_type, url):
        pass


class SpecialStrategy(Strategy):
    def __init__(self) -> None:
        self.username = SpecialStrategy.get_username()
        self._url = f'https://api.github.com/users/{self.username}/repos'

    @staticmethod
    def get_username() -> str:
        username = input('Введите имя пользователя, чтобы получить его список репозиториев: ')
        return username

    def do_algorithm(self, url):
        pass


class StrategyGet(SpecialStrategy):
    """http-GET method"""
    def do_algorithm(self) -> List:
        url = self._url
        r = requests.get(url).json()
        repositories = []
        for el in r:
            repositories.append(el['name'])
        return repositories


class StrategyPost(SpecialStrategy):
    """http-POST method"""
    def do_algorithm(self) -> List:
        url = self._url
        r = requests.post(url).json()
        repositories = []
        for el in r:
            repositories.append(el['name'])
        return repositories


if __name__ == "__main__":
    context = Context(StrategyGet())
    print("Client: Strategy is http-GET")
    context.do_some_http_req_magic()

    # Eсли тип запроса POST
    # print("Client: Strategy is http-POST")
    # context.strategy = StrategyPost()
    # context.do_some_http_req_magic()
