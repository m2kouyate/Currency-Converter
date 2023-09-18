from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor
import requests
from rest_framework import serializers
from django.core.cache import cache
from currencyconverter.settings import API_URL, CACHE_TIMEOUT
import logging

# Step 2: Create a logger instance
logger = logging.getLogger(__name__)


def fetch_data(url):
    response = requests.get(url)
    return response.json()


def get_available_currencies() -> List[Tuple[str, str]]:
    """
    Fetches and returns a list of available currencies from the Central Bank of Russia's API.
    The result is cached for one hour to minimize unnecessary API calls.

    Returns:
        list: A list of tuples with currency codes and their respective descriptions.
    """

    available_currencies = cache.get('available_currencies')

    if not available_currencies:
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(fetch_data, API_URL)
                data = future.result()
                available_currencies = [(code, f"{code} - {details['Name']}") for code, details in data['Valute'].items()]
                available_currencies.append(('RUB', 'RUB - Российский рубль'))
                available_currencies = sorted(available_currencies, key=lambda x: x[1])
                cache.set('available_currencies', available_currencies, timeout=CACHE_TIMEOUT)

                # Log the successful fetch operation
                logger.info("Successfully fetched available currencies")
        except Exception as e:
            # Log any exception that occurs during the fetch operation
            logger.error(f"Error fetching available currencies: {e}")
            raise

    return available_currencies


class CurrencyConversionSerializer(serializers.Serializer):
    """
    Serializer for currency conversion. It includes fields for 'from' currency, 'to' currency and the value to be converted.
    The available currencies are fetched from the Central Bank of Russia's API.
    """

    available_currencies = get_available_currencies()
    from_currency = serializers.ChoiceField(choices=available_currencies)
    to_currency = serializers.ChoiceField(choices=available_currencies)
    value = serializers.FloatField(min_value=0)
