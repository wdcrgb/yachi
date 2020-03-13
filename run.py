import unittest
import time
from .Common.HTMLTestRunner import HTMLTestRunner
from .Common.test_case_data import getFiles, get_excel_data
from .Common.redis_save_data import RedisClient


redis = RedisClient()
for file in getFiles("../Resource/TestData/TestCase", '.xlsx'):
    if file:
        excel_data = get_excel_data(file)
        redis.batch_insert('test_case', excel_data, 'list')
        suite = unittest.defaultTestLoader.discover("./LikeJmeter", pattern="test*.py")
        file_path = './Resource/Results/{}{}.html'.format(file.split('\\')[-1].split('.')[0], time.strftime("%Y_%m_%d %H_%M_%S"))
        with open(file_path, 'wb') as f:
            HTMLTestRunner(stream=f, title=file.split('\\')[-1].split('.')[0], description='用例执行情况:', verbosity=2).run(suite)
