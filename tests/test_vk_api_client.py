import unittest
from unittest import mock
from tests.mock_server import get_free_port, start_mock_server
from сlasses.vk_api_client import VkApiClient


class TestVkApiClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_server_port = get_free_port()
        start_mock_server(cls.mock_server_port)

    def test_request_response(self):
        mock_users_url = 'http://localhost:{port}/'.format(port=self.mock_server_port)
        with mock.patch('сlasses.vk_api_client.VkApiClient.API_BASE_URL', new_callable=mock.PropertyMock) as mock_f:
            mock_f.return_value = mock_users_url
            self.api = VkApiClient(token='', app_id='', user_id='1', debug_mode=True)
            assert self.api.is_initialized
            assert self.api.get_fname == 'Павел'
            assert self.api.get_lname == 'Дуров'
            assert len(self.api.get_countries()) == 234
            assert len(self.api.search_cities(country_id=1, city_name='Нижн')) == 80
            assert len(self.api.search_users(q='Дуров')) == 16
            assert len(self.api.get_user_photos(owner_id='1', needed_qty=1000)) == 9
