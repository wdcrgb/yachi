import time
import redis


# 工具类简单，如果是字节，转成str
def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given."""
    if isinstance(s, bytes):
        return s.decode(encoding)
    return s


class RedisClient(object):
    def __init__(self, url='redis://@localhost:6379/0'):
        self.redis = redis.from_url(url=url)

    # 保证单例，减少连接数
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            cls.__instance = object.__new__(cls)
        return cls.__instance

    # 遍历队列，获取所有keys，用cursor在keys量大时不会堵塞redis
    def get_all_keys(self, match=None, cursor=0):
        result_list = []
        while True:
            iter_result = self.redis.scan(match=match, cursor=cursor)
            cursor = iter_result[0]
            result_list.extend(iter_result[1])
            if cursor == 0:
                return map(bytes_to_str, result_list)

    # 获取队列长度，兼容不同类型的获取长度，同时可以批量检测
    def get_len(self, args):
        len_dict = dict()
        val = None
        if not isinstance(args, str):
            for key in args:
                kind = self.get_kind(key)
                if kind == 'hash':
                    val = self.redis.hlen(key)
                elif kind == 'zset':
                    val = self.redis.zcard(key)
                elif kind == 'list':
                    val = self.redis.llen(key)
                elif kind == 'set':
                    val = self.redis.scard(key)
                len_dict[key] = val
            return len_dict
        else:
            dict_len = self.get_len([args])
            return dict_len[args]

    # 获取队列类型，同时兼容批量检测类型
    def get_kind(self, args):
        if isinstance(args, str):
            return bytes_to_str(self.redis.type(args))
        else:
            kind_dict = dict()
            for item in args:
                kind_dict[item] = bytes_to_str(self.redis.type(item))
            return kind_dict

    # 批量取，因为保证进程安全，采取迭代弹出，如果是单进程可以批量查然后批量删
    def batch_fetch(self, name, count=1, kind=None):
        if not kind:
            kind = self.get_kind(name)
        pipe = self.redis.pipeline()
        if kind == 'set':
            while True:
                [pipe.spop(name=name) for i in range(count)]
                result = pipe.execute()
                clean_result = set(result) - set([None])
                if clean_result:
                    yield clean_result
                else:
                    break

        elif kind == 'list':
            while True:
                [pipe.lpop(name=name) for i in range(count)]
                result = pipe.execute()
                clean_result = set(result) - set([None])
                if clean_result:
                    yield clean_result
                else:
                    break

    # 批量查找
    def batch_find(self, name, count, kind=None, cursor=0):
        if not kind:
            kind = self.get_kind(name)
        if kind == 'set':
            cursor, result = self.redis.sscan(name=name, count=count, cursor=cursor)
            yield result
            while cursor:
                cursor, result = self.redis.sscan(name=name, count=count, cursor=cursor)
                yield result
                if not cursor:
                    break

        elif kind == 'list':
            while True:
                start = 0
                end = count - 1
                result = self.redis.lrange(name=name, start=start, end=end)
                yield result
                if not result:
                    break

    # 批量删除
    def batch_delete(self, name, value, kind=None, count=None):
        if not kind:
            kind = self.get_kind(name)

        if kind == 'set':
            self.redis.srem(name, *value)

        elif kind == 'list':
            self.redis.ltrim(name=name, start=count, end=-1)

    # 批量插入
    def batch_insert(self, name, value, kind=None):
        if not kind:
            kind = self.get_kind(name)
        insert_num = 0
        if kind == 'set':
            insert_num = self.redis.sadd(name, *value)
        elif kind == 'list':
            insert_num = self.redis.rpush(name, *value)
        return insert_num


if __name__ == '__main__':
    redis = RedisClient()
    bb = redis.get_kind('hhh')
    name = '998_info_video_queue'
    for i in redis.batch_fetch(name=name, count=10000):
        print(i)
        # redis.batch_insert(name=name, value=i)
        time.sleep(1)