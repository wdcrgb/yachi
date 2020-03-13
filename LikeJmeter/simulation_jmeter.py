import requests

class SimulationJmeter():

    def api_requests(self, request_url, request_method, request_params, request_header, request_data):
        try:
            return requests.request(request_method, request_url, params=request_params, data=request_data, headers=request_header, timeout=5)
        except (requests.ConnectionError, requests.HTTPError, requests.URLRequired, requests.Timeout, requests.ConnectTimeout) as e:
            print(e)