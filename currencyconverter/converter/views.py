from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
import logging

from .currency_utils import get_exchange_rate, fetch_exchange_rate_data
from .serializers import CurrencyConversionSerializer

# Step 2: Create a logger instance
logger = logging.getLogger(__name__)

class ConvertCurrency(APIView):
    """
    API view for currency conversion. It supports both GET and POST methods for conversion.
    The actual conversion is handled by the 'handle_request' method.
    """

    serializer_class = CurrencyConversionSerializer

    def handle_request(self, from_currency, to_currency, value):
        """
        Handles the currency conversion request. It validates the input value and performs the conversion using the latest exchange rates.

        Parameters:
            from_currency (str): The currency code to convert from.
            to_currency (str): The currency code to convert to.
            value (str): The value to be converted.

        Returns:
            Response: A Response object containing the result of the conversion or an error message.
        """

        try:
            value = float(value)
            if value < 0:
                logger.warning(f"Attempt to convert a negative value: {value}")
                return Response({"error": "Value cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)

            rate = get_exchange_rate(from_currency, to_currency)
            result = rate * value
            logger.info(f"Conversion successful: {from_currency} to {to_currency}, value: {value}, result: {result}")
            return Response({"result": result}, status=status.HTTP_200_OK)
        except ValueError as e:
            logger.error(f"Invalid value parameter: {e}")
            return Response({"error": "Invalid value parameter"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return Response(
                {"error": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Converts currency from one to another based on the current exchange rate.",
        manual_parameters=[
            openapi.Parameter(name='from', in_=openapi.IN_QUERY, description='From Currency', type=openapi.TYPE_STRING,
                              required=True),
            openapi.Parameter(name='to', in_=openapi.IN_QUERY, description='To Currency', type=openapi.TYPE_STRING,
                              required=True),
            openapi.Parameter(name='value', in_=openapi.IN_QUERY, description='Value to Convert',
                              type=openapi.TYPE_NUMBER, required=True),
        ]
    )
    def get(self, request: Request) -> Response:
        """
        Handles GET requests for currency conversion. It retrieves the 'from' currency,
        'to' currency, and value from the query parameters and performs the conversion.

        Parameters:
            request (Request): The HTTP GET request object.

        Returns:
            Response: A Response object containing the result of the conversion or an error message.
        """

        from_currency = request.query_params.get('from')
        to_currency = request.query_params.get('to')
        value = request.query_params.get('value')

        if not from_currency or not to_currency or not value:
            logger.warning("Missing required parameters in GET request")
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"GET request for conversion from {from_currency} to {to_currency} with value {value}")
        return self.handle_request(from_currency, to_currency, value)

    @swagger_auto_schema(
        operation_description="Converts currency from one to another based on the current exchange rate.",
        request_body=CurrencyConversionSerializer
    )
    def post(self, request: Request) -> Response:
        """
        Handles POST requests for currency conversion. It validates the data from the request body
        using the CurrencyConversionSerializer and performs the conversion if the data is valid.

        Parameters:
            request (Request): The HTTP POST request object.

        Returns:
            Response: A Response object containing the result of the conversion or an error message.
        """

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            from_currency = serializer.validated_data['from_currency']
            to_currency = serializer.validated_data['to_currency']
            value = serializer.validated_data['value']

            logger.info(f"POST request for conversion from {from_currency} to {to_currency} with value {value}")
            return self.handle_request(from_currency, to_currency, value)
        else:
            logger.warning("Invalid data received in POST request")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





