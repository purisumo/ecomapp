import requests
import base64

from django.conf import settings

class PayMongoAPI:
    BASE_URL = "https://api.paymongo.com/v1"
    
    def __init__(self):
        self.secret_key = settings.PAYMONGO_SECRET_KEY
        self.public_key = settings.PAYMONGO_PUBLIC_KEY
        
    def _get_auth_header(self):
        """Generate Basic Auth header"""
        encoded = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        return {
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json'
        }
    
    def create_source(self, amount, description, redirect_success, redirect_failed):
        """
        Create a GCash source (checkout URL)
        
        Args:
            amount: Amount in cents (e.g., 10000 = PHP 100.00)
            description: Payment description
            redirect_success: URL to redirect after successful authorization
            redirect_failed: URL to redirect after failed authorization
        
        Returns:
            dict: Source data including checkout_url
        """
        url = f"{self.BASE_URL}/sources"
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount,
                    "redirect": {
                        "success": redirect_success,
                        "failed": redirect_failed
                    },
                    "type": "gcash",
                    "currency": "PHP",
                    "description": description
                }
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_auth_header()
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'response': e.response.json() if hasattr(e, 'response') else None
            }
    
    def retrieve_source(self, source_id):
        """
        Retrieve source details to check authorization status
        
        Args:
            source_id: The source ID
        
        Returns:
            dict: Source data including status
        """
        url = f"{self.BASE_URL}/sources/{source_id}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_auth_header()
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_payment(self, source_id, amount, description):
        """
        Create a payment using the authorized source
        
        Args:
            source_id: The authorized source ID
            amount: Amount in cents
            description: Payment description
        
        Returns:
            dict: Payment data
        """
        url = f"{self.BASE_URL}/payments"
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount,
                    "source": {
                        "id": source_id,
                        "type": "source"
                    },
                    "currency": "PHP",
                    "description": description
                }
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_auth_header()
            )
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'response': e.response.json() if hasattr(e, 'response') else None
            }