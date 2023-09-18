from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache
import logging

from currencyconverter.settings import CACHE_TIMEOUT, API_URL
from .serializers import fetch_data

logger = logging.getLogger(__name__)


def fetch_exchange_rate_data() -> dict:
    """
    Fetches the latest exchange rate data from the Central Bank of Russia's API.
    The result is cached for one hour to avoid unnecessary API calls.

    Returns:
        dict: A dictionary containing the latest exchange rate data.
    """

    data = cache.get('exchange_rate_data')
    if not data:
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(fetch_data, API_URL)
                data = future.result()
                cache.set('exchange_rate_data', data, timeout=CACHE_TIMEOUT)

            logger.info("Successfully fetched exchange rate data")
        except Exception as e:
            logger.error(f"Error fetching exchange rate data: {e}")
            raise

    return data


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Calculates the exchange rate between two currencies using data from the Central Bank of Russia's API.

    Parameters:
        from_currency (str): The currency code to convert from.
        to_currency (str): The currency code to convert to.

    Returns:
        float: The exchange rate from 'from_currency' to 'to_currency'.
    """

    try:
        data = fetch_exchange_rate_data()

        from_rate = data['Valute'].get(from_currency, {'Value': 1, 'Nominal': 1})
        to_rate = data['Valute'].get(to_currency, {'Value': 1, 'Nominal': 1})

        rate = (from_rate['Value'] / from_rate['Nominal']) / (to_rate['Value'] / to_rate['Nominal'])

        logger.info(f"Successfully calculated exchange rate from {from_currency} to {to_currency}: {rate}")

    except Exception as e:
        logger.error(f"Error calculating exchange rate from {from_currency} to {to_currency}: {e}")
        raise

    return rate
