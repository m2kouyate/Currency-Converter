from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .currency_utils import fetch_exchange_rate_data, get_exchange_rate
from .serializers import get_available_currencies


class ConvertCurrencyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_convert_currency_get(self):
        url = reverse('convert_currency')
        response = self.client.get(url, {'from': 'USD', 'to': 'RUB', 'value': '100'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('result', response.data)

    def test_convert_currency_post(self):
        url = reverse('convert_currency')
        data = {
            "from_currency": "USD",
            "to_currency": "RUB",
            "value": 100
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('result', response.data)

    def test_convert_currency_invalid_value(self):
        url = reverse('convert_currency')
        response = self.client.get(url, {'from': 'USD', 'to': 'RUB', 'value': '-100'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_convert_currency_missing_parameters(self):
        url = reverse('convert_currency')
        response = self.client.get(url, {'from': 'USD', 'value': '100'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UtilityFunctionTests(TestCase):

    def test_get_available_currencies(self):
        currencies = get_available_currencies()
        self.assertIsInstance(currencies, list)
        self.assertGreater(len(currencies), 0)

    def test_fetch_exchange_rate_data(self):
        data = fetch_exchange_rate_data()
        self.assertIsInstance(data, dict)
        self.assertIn('Valute', data)

    def test_get_exchange_rate(self):
        rate = get_exchange_rate('USD', 'RUB')
        self.assertIsInstance(rate, float)
        self.assertGreater(rate, 0)



