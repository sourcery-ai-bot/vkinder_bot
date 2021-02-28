import unittest
from random import randrange
from unittest import mock
from tests.mock_server import get_free_port, start_mock_server
from сlasses.vk_api_classes import VKinderClient
from сlasses.vk_api_client import VkApiClient
from сlasses.vkinder_db_client import VKinderDb


class TestVKinderDb(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = VKinderDb('test', 'test', 'test', debug_mode=True)
        cls.mock_server_port = get_free_port()
        start_mock_server(cls.mock_server_port)

    def test_client_save_load(self):
        assert self.db.is_initialized
        mock_users_url = 'http://localhost:{port}/'.format(port=self.mock_server_port)
        with mock.patch('сlasses.vk_api_client.VkApiClient.API_BASE_URL', new_callable=mock.PropertyMock) as mock_f:
            mock_f.return_value = mock_users_url
            self.api = VkApiClient(token='', app_id='', user_id='1', debug_mode=True)
            assert self.api.is_initialized
            users = self.api.get_users('1')
            assert len(users) == 2
            user = users[0]
            client = VKinderClient(user)
            self.db.save_client(client)
            client_db = self.db.load_client_from_db('1')
            assert client_db
            client = VKinderClient(client_db)
            assert client.vk_id == '1'
            assert client.fname == 'Павел'
            assert client.lname == 'Дуров'

    def test_users_save_load(self):
        mock_users_url = 'http://localhost:{port}/'.format(port=self.mock_server_port)
        with mock.patch('сlasses.vk_api_client.VkApiClient.API_BASE_URL', new_callable=mock.PropertyMock) as mock_f:
            mock_f.return_value = mock_users_url
            self.api = VkApiClient(token='', app_id='', user_id='1', debug_mode=True)
            assert self.api.is_initialized
            users = self.api.get_users(['1', '5', 1])
            client_1 = VKinderClient(users[0])
            assert client_1
            client_2 = VKinderClient(users[1])
            assert client_2

            self.db.save_client(client_1)
            self.db.save_client(client_2)

            for i in range(self.db.search_history_limit + 1):
                client_1.reset_search()
                client_2.reset_search()

                client_1.search.sex_id = randrange(0, 2, 1)
                client_1.search.status_id = randrange(1, 8, 1)
                client_1.search.city_id = 1
                client_1.search.city_name = 'Москва'
                client_1.search.min_age = randrange(0, 60, 1)
                client_1.search.max_age = randrange(client_1.search.min_age, 127, 1)
                client_1.rating_filter = 0

                client_2.search.sex_id = randrange(0, 2, 1)
                client_2.search.status_id = randrange(1, 8, 1)
                client_2.search.city_id = 2
                client_2.search.city_name = 'Санкт-Петербург'
                client_2.search.min_age = randrange(0, 60, 1)
                client_2.search.max_age = randrange(client_2.search.min_age, 127, 1)
                client_2.rating_filter = 0

                self.db.save_search(client_1)
                self.db.save_search(client_2)

                client_1.found_users = self.api.search_users()
                client_2.found_users = self.api.search_users(q='babych')
                assert len(client_1.found_users) > 0
                assert len(client_2.found_users) > 0

                self.db.save_users(client_1)
                self.db.save_users(client_2)




