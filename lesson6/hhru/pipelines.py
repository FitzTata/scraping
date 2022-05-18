# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "jobs"


class JobparserPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client[MONGO_DB]

    @staticmethod
    def process_salary(salary_list: list, spider):
        print(salary_list)
        if spider.name == 'hhru':
            s_min = int(salary_list[salary_list.index('от ') + 1].replace('\xa0', '')) if 'от ' in salary_list else None
            s_max = int(
                salary_list[salary_list.index(' до ') + 1].replace('\xa0', '')) if ' до ' in salary_list else None
            s_currency = salary_list[salary_list.index(' на руки') - 1] if ' на руки' in salary_list else None
        else:  # Часть с sj. Мне не стыдно. Какой сайт - такой и код.
            for item in salary_list:
                item = item.replace('\xa0', '')  # Удаляю неразрывные пробелы
                temp_item = []  # Создаю временный лист. Там будет не более 2 значений - минимальная и максимальная зп
                if len(item) > 4:  # Чтобы не смотреть лишнее
                    temp_str = ''
                    for ch in item:
                        if ch.isdigit():
                            temp_str += ch
                    if temp_str:
                        temp_item.append(int(temp_str))  # Записываю одно значение полностью из цифр в список
            s_currency = 'Rub' if temp_item else None  # Надо бы допилить после тестов
            s_min = min(temp_item) if temp_item else None
            s_max = max(temp_item) if temp_item else None
            if s_min == s_max:  # Обработка случаев с зп "от" или "до"
                if 'от' in salary_list:
                    s_max = None
                elif 'до' in salary_list:
                    s_min = None
                if not s_max and not s_min:
                    s_min = s_max = 'По договорённости'
        return s_min, s_max, s_currency

    def process_item(self, item, spider):
        s_min, s_max, s_currency = self.process_salary(item["salary"], spider)
        item["title"] = " ".join(item["title"])
        if s_min:
            item["salary_min"] = s_min
        if s_max:
            item["salary_max"] = s_max
        if s_currency:
            item["salary_currency"] = s_currency
        item.pop("salary")

        collection = self.db[spider.name]
        collection.insert_one(item)

        return item
