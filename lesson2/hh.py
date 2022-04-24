import json
import re
import time
from pprint import pprint

import requests
from bs4 import BeautifulSoup as bs


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

    def increase_current_page_by_one (self):
        self.current_page += 1

    def get_current_url(self):
        return f"https://hh.ru/search/vacancy?area=1&text={self.vacancy_title}&page={self.current_page}&hhtmFrom=vacancy_search_list"


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
            self.increase_current_page_by_one()
            self.url = self.get_current_url()
            time.sleep(1)
        return self.vacancies_list


    def save_info_to_json(self):
        with open('vacansies.json', 'w') as f:
            json.dump(self.to_json, f, indent=4)


if __name__ == "__main__":
    scraper = HHScraper()
    scraper.process()
    scraper.save_info_to_json()
