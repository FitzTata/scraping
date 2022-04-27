import json
import json
import re
import time
from pprint import pprint
from pymongo import MongoClient

import requests
from bs4 import BeautifulSoup as bs


class MongoMagic:
    def __init__(self):
        self.mongo_host = "localhost"
        self.mongo_port = 27017
        self.mongo_db = "vacancies"
        self.mongo_collection = "vacancies"

    def save_one_vacancy_to_mongo(self, vacancy_data: dict) -> None:
        with MongoClient(self.mongo_host, self.mongo_port) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            collection.insert_one(vacancy_data)

    def save_unique_vacancy_to_mongo(self, vacancy_data: dict) -> None:
        with MongoClient(self.mongo_host, self.mongo_port) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            link = vacancy_data['link']
            if not list(collection.find({'link': link})):
                collection.insert_one(vacancy_data)

    def find_by_salary_and_print(self) -> None:
        with MongoClient(self.mongo_host, self.mongo_port) as client:
            db = client[self.mongo_db]
            collection = db[self.mongo_collection]
            salary_to_find = int(input('Введите минимальную сумму зп, за которую вы согласны работать: '))
            sorted_vacancies = collection.find({
                "$or": [{"salary_min": {"$gte": salary_to_find}}, {"salary_min": {"$gte": salary_to_find}}]
            })
            for vacancy in sorted_vacancies:
                pprint(vacancy)


class HHScraper:
    def __init__(self):
        self.headers = {'User-agent':
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
                        }
        self.vacancy_title = self.get_vacancy_title()
        self.vacancies_list = []
        self.to_json = {'vacancies': self.vacancies_list}
        self.max_page = self.get_max_page()
        self.current_page = 0
        self.url = self.get_current_url()

    @staticmethod
    def get_vacancy_title():
        vacancy = input('Введите название вакансии: ')
        if len(vacancy.split()) > 1:
            vacancy = '+'.join(vacancy.split())
        return vacancy

    def increase_current_page_by_one(self):
        self.current_page += 1

    def get_current_url(self):
        return f"https://hh.ru/search/vacancy?area=1&text={self.vacancy_title}&" \
               f"page={self.current_page}&hhtmFrom=vacancy_search_list"

    @staticmethod
    def get_max_page():
        return int(input('Сколько страниц смотреть? '))

    def create_html(self):
        return requests.get(self.url, headers=self.headers).text

    def process(self):
        while self.current_page < self.max_page:
            parsed_html = bs(self.create_html(), 'html.parser')
            jobs_list = parsed_html.find_all('div', {'class': 'vacancy-serp-item'})
            for job in jobs_list:
                job_data = {}
                req = job.find('span', {'class': 'g-user-content'})
                if req:
                    main_info = req.findChild()
                    job_name = main_info.getText()
                    job_link = main_info['href']
                    salary = job.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                    if not salary:
                        salary_min = None
                        salary_max = None
                    else:
                        salary = salary.getText().replace('\u202f', '')
                        salaries = salary.split('–')
                        salaries[0] = re.sub(r'[^0-9]', '', salaries[0])
                        salary_min = int(salaries[0])
                        if len(salaries) > 1:
                            salaries[1] = re.sub(r'[^0-9]', '', salaries[1])
                            salary_max = int(salaries[1])
                    job_data['name'] = job_name
                    job_data['salary_min'] = salary_min
                    job_data['salary_max'] = salary_max
                    job_data['link'] = job_link
                    job_data['site'] = 'hh.ru'
                    job_data['page'] = self.current_page
                    self.vacancies_list.append(job_data)
                    # mongo.save_one_vacancy_to_mongo(job_data) Закомментировал после первого
                    # срабатывания, чтобы не засорять базу
                    mongo.save_unique_vacancy_to_mongo(job_data)
            self.increase_current_page_by_one()
            self.url = self.get_current_url()
            time.sleep(1)
        return self.vacancies_list

    def save_info_to_json(self):
        with open('vacansies.json', 'w') as f:
            json.dump(self.to_json, f, indent=4)


if __name__ == "__main__":
    mongo = MongoMagic()
    # scraper = HHScraper()
    # scraper.process()
    mongo.find_by_salary_and_print()
    # scraper.save_info_to_json()
