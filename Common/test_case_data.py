import xlrd
import os
import json


def getFiles(dir, suffix):
    '''
    遍历读取文件下的所有指定类型的文件
    :param dir: 目录
    :param suffix: 文件后缀
    :return: 目录内符合文件后缀的文件地址
    '''
    res = []
    for root, directory, files in os.walk(dir):
        for filename in files:
            name, suf = os.path.splitext(filename)
            if suf == suffix:
                res.append(os.path.join(root, filename))
    return res


def get_excel_data(file):
    '''
    获取excel文件中的数据
    :param file: excel文件中的地址
    :return:
    '''
    excel_data = xlrd.open_workbook(file)
    sheet = excel_data.sheet_by_index(0)
    rows = sheet.nrows
    cols = sheet.ncols
    data = []
    # 遍历excel内数据并拼装成数组含元组格式
    for i in range(1, rows):
        d = {}
        for j in range(0, cols):
            q = sheet.cell(0, j).value
            d[q] = sheet.cell(i, j).value
        ap = []
        for k, v in d.items():
            if isinstance(v, float):
                ap.append(v)
            else:
                ap.append(v)
        bp = (ap[3], eval(ap[6]), eval(ap[7]), eval(ap[8]), eval(ap[9]), eval(ap[10]))
        # request_url, request_method, request_params, request_header, request_data, response_data
        data.append(bp)
    return data


if __name__ == '__main__':
    for file in getFiles("../Resource/TestData/TestCase", '.xlsx'):  # 查找以.py结尾的文件
        print(file)
    print(get_excel_data('../Resource/TestData/TestCase\yache.xlsx'))


# request_url, request_method, request_params, request_header, request_data