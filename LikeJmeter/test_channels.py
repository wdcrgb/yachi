import unittest
from .simulation_jmeter import simulationJmeter
from parameterized import parameterized
import sys
sys.path.append('../')
from Common.redis_save_data import RedisClient
redis = RedisClient()

class TestClannels(unittest.TestCase):
    excel_data = redis.batch_fetch('test_case', 'list')
    @parameterized.expand(excel_data)
    def test_clannels(self, request_url, request_method, request_params, request_header, request_data, response_data):
        r = simulationJmeter().api_requests(request_url, request_method, request_params, request_header, request_data)
        self.assertEquals(200, r.status_code)
        self.assertEquals(response_data, r.json())

if __name__ == '__main__':
    unittest.main()