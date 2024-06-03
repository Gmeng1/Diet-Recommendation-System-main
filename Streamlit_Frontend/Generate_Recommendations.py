import time

import requests
import json


class Generator:
    def __init__(self, nutrition_input: list, ingredients: list = [],
                 params: dict = {'n_neighbors': 5, 'return_distance': False}):
        self.nutrition_input = nutrition_input
        self.ingredients = ingredients
        self.params = params

    def set_request(self, nutrition_input: list, ingredients: list, params: dict):
        self.nutrition_input = nutrition_input
        self.ingredients = ingredients
        self.params = params

    def generate(self, ):
        request = {
            'nutrition_input': self.nutrition_input,
            'ingredients': self.ingredients,
            'params': self.params
        }
        max_retries = 10
        retry_interval = 5  # seconds
        for _ in range(max_retries):
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url='http://127.0.0.1:8081/predict/', data=json.dumps(request), json=request,
                                         headers=headers)
                if response.status_code == 503:
                    print("503 Service Unavailable - retrying...")
                    time.sleep(retry_interval)
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Request failed: {e}")

        return None
