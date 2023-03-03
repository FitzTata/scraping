# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy

# with open('../../../../data/pass.json') as f:
#     credentials = json.load(f)
# for key, val in credentials.items():
#     if key == 'instagram':
#         for k, v in val.items():
#             if k == 'login':
#                 insta_login = v
#             if k == 'pass':
#                 insta_pwd = v


class InstagramSpider(scrapy.Spider):
    # атрибуты класса
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = '***'
    insta_pwd = '***'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    # parse_user = 'kmemescluster'  # Пользователь, у которого собираем посты. Можно указать список
    parse_users = ['nine.three.photography', 'photochu']  # Пользователи, у которых собираем follower/following

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'eddbde960fed6bde675388aac39a3657'  # hash для получения данных о постах с главной страницы
    followers_hash = 'c76146de99bb02f6415203be841dd25a' # hash для получения подписчиков
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076' # hash для получения подписок

    def parse(self, response: HtmlResponse):  # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,  # метод который будет обрабатывать полученные значения
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token})  # передаём csrf токен

    # после авторизации мы попадаем на свою страницу
    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)  # Преобразуем респонс в джейсон
        if j_body['authenticated']:  # Проверяем ответ после авторизации, чтобы понять удачно ли прошла авторизация
            for parse_user in self.parse_users:     # Перебираем аккаунты пользователей
                yield response.follow(
                    # т.к. скрапи прекрасно работает с относительными ссылками - этого достаточно для перехода
                    f'/{parse_user}',
                    callback=self.user_data_parse,  # след. шаг
                    cb_kwargs={'username': parse_user}
                )
                # можем передавать любые значения. Это важно передавать именно так, а не брать из общего
                # глобального списка потому что мы можем перебирать это в цикле и у вас будут лететь айтемы
                # в абсолютно неопределённом порядке потому что асинхронно, поэтому надо передавать явно.
                # Поэтому мы передаём этот username в следующий метод user_data_parse явно

    # принимаем username из предыдущего метода user_parse и
    # на руках будет иметь имя пользователя с которым работаем в данном методе
    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя методом fetch_user_id
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)

        # graphql+query_hash: Формируем ссылку для получения .  urlencode кодирует параметры
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})  # variables ч/з deepcopy во избежание гонок

        yield response.follow(
            url_following,
            callback=self.following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})  # variables ч/з deepcopy во избежание гонок

    # # собираем посты
    # def user_posts_parse(self, response: HtmlResponse, username, user_id,
    #                      variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
    #     j_data = json.loads(response.text)
    #     # здесь get это не get-запрос, а метод get у словаря. идём на 4 уровня в глубину.
    #     page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
    #     if page_info.get('has_next_page'):  # Если есть следующая страница
    #         variables['after'] = page_info['end_cursor']  # Новый параметр для перехода на след. страницу
    #         url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
    #         yield response.follow(
    #             url_posts,
    #             callback=self.user_posts_parse,
    #             cb_kwargs={'username': username,
    #                        'user_id': user_id,
    #                        'variables': deepcopy(variables)}
    #         )
    #     posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')  # Сами посты
    #     for post in posts:  # Перебираем посты, собираем данные
    #         item = InstaparserItem(
    #             user_id=user_id,
    #             photo=post['node']['display_url'],
    #             likes=post['node']['edge_media_preview_like']['count'],
    #             post=post['node']  # на всякий на будущее закидываем всю ноду в post, вдруг понадобятся данные
    #         )
    #     yield item  # В пайплайн

    # собираем подписчиков
    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        #page_info = j_data.get('data').get('user').ger('edge_followed_by').get('page_info')
        followers_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')  # метод get словаря
        print("followers_info =", followers_info)
        if followers_info.get('has_next_page'): # Если есть следующая страница
            variables['after'] = followers_info['end_cursor']  # Новый параметр для перехода на след. страницу
            print("variables['after'] =", variables['after'])
            url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            print("url_followers =", url_followers)
            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)
                           }
            )
        followers = j_data.get('data').get('user').get('edge_followed_by').get('edges')  # Сами подписчики
        for follower in followers:
            item = InstaparserItem(
                username=username,
                follower_id=follower['node']['id'],
                username_follower=follower['node']['username'],
                full_name=follower['node']['full_name'],
                photo=follower['node']['profile_pic_url'],
                user_attribute='follower',
                full_info=follower['node'])
        yield item

    # собираем тех, на кого подписан пользователь
    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = json.loads(response.text)
        # page_info = j_data.get('data').get('user').ger('edge_followed_by').get('page_info')
        following_info = j_data.get('data').get('user').get('edge_follow').get('page_info')  # метод get словаря
        print("following_info =", following_info)
        if following_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = following_info['end_cursor']  # Новый параметр для перехода на след. страницу
            print("variables['after'] =", variables['after'])
            url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            print("url_following =", url_following)
            yield response.follow(
                url_following,
                callback=self.following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)})
        followings = j_data.get('data').get('user').get('edge_follow').get('edges')  # Сами подписчики
        for following in followings:
            item = InstaparserItem(
                username=username,
                following_id=following['node']['id'],
                username_following=following['node']['username'],
                full_name=following['node']['full_name'],
                photo=following['node']['profile_pic_url'],
                user_attribute='following',
                full_info=following['node'])
        yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя. Т.к. в ответе id не представлен. id нужно вытаскивать из html
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')