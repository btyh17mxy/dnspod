#!/usr/bin/env python
# -*-coding:utf-8-*-

__version__ = '0.1'
__author__ = 'Mush (btyh17mxy@gmail.com)'

'''
Copyright (c) 2014 Mush Mo
All rights reserved.

file:       dnspod.py
summary:    提供DNSPod域名和记录的增删改查.

version:    0.1
authors:    Mush (btyh17mxy@gmail.com)

time:       2014-06-07
'''
import requests
import json
import logging
import unittest
import csv
import os
import unicodecsv
import cStringIO
import codecs
DEBUG_LEVEL = logging.DEBUG
try:
    import colorizing_stream_handler
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(colorizing_stream_handler.ColorizingStreamHandler())
except Exception, e:
    print 'can not import colorizing_stream_handler, using logging.StreamHandler()'
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(logging.StreamHandler())

'''
-1 登陆失败
-2 API使用超出限制
-3 不是合法代理 (仅用于代理接口)
-4 不在代理名下 (仅用于代理接口)
-7 无权使用此接口
-8 登录失败次数过多，帐号被暂时封禁
85 帐号异地登录，请求被拒绝
-99 此功能暂停开放，请稍候重试
1 操作成功
2 只允许POST方法
3 未知错误
6 用户ID错误 (仅用于代理接口)
7 用户不在您名下 (仅用于代理接口)
83 该帐户已经被锁定，无法进行任何操作
85 该帐户开启了登录区域保护，当前IP不在允许的区域内
50 您开启了D令牌，需要验证码
51 没有开启D令牌
52 验证码不正确
53 您已经开启了D令牌
54 域名所有者开启了D令牌，您也需要开启D令牌才能管理该域名
'''
'''
1.	使用 DNSPod API 完成 域名和记录的基本增、删、改、查操作；
2.	域名记录的导入、导出；
•	要求：
1.	有基本的 UI；
2.	使用原生Python或者任意一款 Python 框架进行开发；
3.	将代码推至 github，并给出项目地址；
4.	时间为一周，越快越好
'''

'''
异常基类.
'''
class DNSPodError(Exception):
    pass


'''
登陆异常，在登陆失败时抛出.
'''
class LoginError(DNSPodError):
    pass


'''
域名操作异常
'''
class DomainError(DNSPodError):
    pass


ERROR_CODE = {
        '-1':LoginError,
        }

DOMAIN_TYPE={
        'all':u'所有域名',
        'mine':u'我的域名',
        'share':u'共享给我的域名',
        'ismark':u'星标域名',
        'pause':u'暂停域名',
        'vip':u'VIP域名',
        'recent':u'最近操作过的域名',
        'share_out':u'我共享出去的域名',
        }
'''
API基类.
'''
class DNSPodBase(object):
    
    def __init__(self, email, pwd, cookie='', **kwargs):
        '''初始化.
        设置url和基本参数及请求头.
        '''
        self.base_url = 'https://dnsapi.cn/'
        self.payload = {
                'login_email':email,
                'login_password':pwd,
                'format':"json",
                }
        self.headers = {
                'User-Agent':'DNSPodDemo/0.1(btyh17mxy@gmail.com)',
                "Accept": "text/json",
                'Cookies':cookie,
                }

    def request(self, url, **kwargs):
        '''发起请求.
        '''
        data = self.payload
        data.update(kwargs)

        logging.info('request :%s'%url)
        logging.info('payload :%s'%data)
        r = requests.post(url, data = data, headers = self.headers)

        try:
            response = r.json()
        except Exception,e:
            logging.error(e)
            raise DNSPodError(e)

        code = response[u'status']['code']
        message = response[u'status']['message']

        if code == u'1':
            logging.info(message)
            response.pop(u'status')
            logging.info(response)
            return response

        logging.error(message)
        if code in ERROR_CODE:
            raise ERROR_CODE[code](message)

        raise DNSPodError(message)


class Domain(DNSPodBase):
    '''
    提供域名操作.
    '''
    def __init__(self,email, pwd, cookie='', **kwargs):
        super(Domain,self).__init__(email, pwd, cookie, **kwargs)
        self.base_url = self.base_url+'Domain'

    def create(self, domain, group_id = '', is_mark = False):
        '''
        增加域名.

        Args:
            domain 域名, 没有 www, 如 dnspod.com
            group_id 域名分组ID，可选参数
            is_mark {yes|no} 是否星标域名，可选参数

        Raise:
            6 域名无效
            7 域名已存在
            11 域名已经存在并且是其它域名的别名
            12 域名已经存在并且您没有权限管理
            41 网站内容不符合DNSPod解析服务条款，域名添加失败
        '''
        url = self.base_url + '.Create'
        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def remove(self, domain = None, domain_id = None,):
        '''
        删除域名

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可

        Raises:
            -15 域名已被封禁
            6 域名ID错误
            7 域名已锁定
            8 VIP域名不可以删除
            9 非域名所有者
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')
        
        url = self.base_url + '.Remove'
        
        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def list(self, type = 'all', offset = 0, length = 3000, group_id = None):
        '''
        获取域名列表.

        Args:
            type 域名权限种类，可选参数，默认为’all’。包含以下类型：
                all：所有域名
                mine：我的域名
                share：共享给我的域名
                ismark：星标域名
                pause：暂停域名
                vip：VIP域名
                recent：最近操作过的域名
                share_out：我共享出去的域名
            offset 记录开始的偏移，第一条记录为 0，依次类推，可选参数
            length 共要获取的记录的数量，比如获取20条，则为20，可选参数
            group_id 分组ID，获取指定分组的域名，可选参数

        Raises:
            6 记录开始的偏移无效
            7 共要获取的记录的数量无效
            9 没有任何域名
        '''
        if type not in DOMAIN_TYPE.keys():
            logging.error(u'域名类型错误，可选类型为all,mine,share,ismark,pause,vip,recent,share_out')
            raise DNSPodError('域名类型错误')
        
        url = self.base_url + '.List'
        
        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def status(self,  status, domain = None, domain_id = None):
        '''设置域名状态.
        
        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可
            status {enable, disable} 域名状态

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 域名被锁定
            8 非域名所有者
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')
        if status not in ('enable','disable'):
            logging.error(u'域名状态必须为enable 或 disable')
            raise DNSPodError(u'域名状态必须为enable 或 disable')

        url = self.base_url + '.Status'
        
        data = locals().copy()
        data.pop('self')

        return self.request(**data)


    def info(self, domain = None, domain_id = None):
        '''获取域名信息

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可

        Raises:
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            8 非域名所有者
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')

        url = self.base_url + '.Info'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def lockstatus (self, domain = None, domain_id = None):
        '''获取域名锁定状态

        Args:
            domain_id 或 domain，分别对应域名ID和域名，提交其中一个即可

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 域名没有锁定
        '''
        if not domain_id and not domain:
            logging.error(u'必须指定一个domain_id或domain, 二者不能都为空')
            raise DNSPodError(u'必须指定一个domain_id或domain, 二者不能都为空')

        url = self.base_url + '.Lockstatus'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)


class Record(DNSPodBase):
    '''记录操作.
    '''

    def __init__(self,email, pwd, cookie='', **kwargs):
        super(Record,self).__init__(email, pwd, cookie, **kwargs)
        self.base_url = self.base_url+'Record'

 
    #FIXME:校验record_type和record_line是否合法
    def create(self, domain_id, value, record_line, record_type=u'默认', mx = None, 
            ttl = 600, sub_domain = u'@'):
        '''添加记录.
        
        Args:
            domain_id 域名ID, 必选
            sub_domain 主机记录, 如 www, 默认@，可选
            record_type 记录类型，通过API记录类型获得，大写英文，比如：A, 必选
            record_line 记录线路，通过API记录线路获得，中文，比如：默认, 必选
            value 记录值, 如 IP:200.200.200.200, CNAME: cname.dnspod.com., MX: mail.dnspod.com., 必选
            mx {1-20} MX优先级, 当记录类型是 MX 时有效，范围1-20, MX记录必选
            ttl {1-604800} TTL，范围1-604800，不同等级域名最小值不同, 可选
        
        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 缺少参数或者参数错误
            7 不是域名所有者或者没有权限
            21 域名被锁定
            22 子域名不合法
            23 子域名级数超出限制
            24 泛解析子域名错误
            25 轮循记录数量超出限制
            26 记录线路错误
            27 记录类型错误
            30 MX 值错误，1-20
            31 存在冲突的记录(A记录、CNAME记录、URL记录不能共存)
            32 记录的TTL值超出了限制
            33 AAAA 记录数超出限制
            34 记录值非法
            36 @主机的NS纪录只能添加默认线路
            82 不能添加黑名单中的IP
        '''

        ttl = int(ttl)
        if mx and not mx in range(1,21):
            logging.error(u'mx out of range')
            raise DNSPodError(u'mx out of range')
        if not ttl in range(1,604801):
            logging.error(u'ttl out of range')
            raise DNSPodError(u'ttl out of range')
        if record_type == 'MX' and not mx:
            logging.error(u'MX记录必须指定mx优先级')
            raise DNSPodError(u'MX记录必须指定mx优先级')

        url = self.base_url + '.Create'
        
        data = locals().copy()
        data.pop('self')
        return self.request(**data)


    def modify(self, domain_id, record_id, record_type, value, 
            record_line, sub_domain = '@', mx = 1, ttl = 600):
        '''修改记录
        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            sub_domain 主机记录，默认@，如 www，可选
            record_type 记录类型，通过API记录类型获得，大写英文，比如：A，必选
            record_line 记录线路，通过API记录线路获得，中文，比如：默认，必选
            value 记录值, 如 IP:200.200.200.200, CNAME: cname.dnspod.com., MX: mail.dnspod.com.，必选
            mx {1-20} MX优先级, 当记录类型是 MX 时有效，范围1-20, mx记录必选
            ttl {1-604800} TTL，范围1-604800，不同等级域名最小值不同，可选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
            22 子域名不合法
            23 子域名级数超出限制
            24 泛解析子域名错误
            25 轮循记录数量超出限制
            26 记录线路错误
            27 记录类型错误
            29 TTL 值太小
            30 MX 值错误，1-20
            31 URL记录数超出限制
            32 NS 记录数超出限制
            33 AAAA 记录数超出限制
            34 记录值非法
            35 添加的IP不允许
            36 @主机的NS纪录只能添加默认线路
            82 不能添加黑名单中的IP
        '''
        if not mx in range(1,21):
            logging.error(u'mx out of range')
            raise DNSPodError(u'mx out of range')
        if not ttl in range(1,604801):
            logging.error(u'ttl out of range')
            raise DNSPodError(u'ttl out of range')
        if record_type == 'MX' and not mx:
            logging.error(u'MX记录必须指定mx优先级')
            raise DNSPodError(u'MX记录必须指定mx优先级')
        
        url = self.base_url + '.Modify'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def list(self, domain_id, offset = 0, length = None, sub_domain = None):
        '''记录列表.

        Args:
            domain_id 域名ID，必选
            offset 记录开始的偏移，第一条记录为 0，依次类推，可选
            length 共要获取的记录的数量，比如获取20条，则为20，可选
            sub_domain 子域名，如果指定则只返回此子域名的记录，可选

        Raises:
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 记录开始的偏移无效
            8 共要获取的记录的数量无效
            9 不是域名所有者
            10 没有记录
        '''
        url = self.base_url + '.List'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

    def remove(self, domain_id, record_id):
        '''删除记录.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
        '''
        url = self.base_url + '.Remove'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)


    def dDNS(self, domain_id, record_id, sub_domain, record_line, value = None):
        '''更新动态DNS记录.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            sub_domain 主机记录，如 www
            record_line 记录线路，通过API记录线路获得，中文，比如：默认，必选
            value IP地址，例如：6.6.6.6，可选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
            22 子域名不合法
            23 子域名级数超出限制，比如免费套餐域名不支持三级域名
            24 泛解析子域名错误，比如免费套餐载名不支持 a*
            25 轮循记录数量超出限制，比如免费套餐域名只能存在两条轮循记录
            26 记录线路错误，比如免费套餐域名不支持移动、国外
        '''
        #TODO: record_line
        url = self.base_url + '.Ddns'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)


    def remark(self, domain_id, record_id, remark):
        '''设置记录备注.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            remark 域名备注，删除备注请提交空内容，必选
            
        Raises:
            6 域名ID错误
            8 记录 ID 错误
        '''
        url = self.base_url + '.Remark'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)
    

    def info(self, domain_id, record_id):
        '''获取记录信息.

        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
        '''
        url = self.base_url +'.Info'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)


    def status(self, domain_id, record_id, status):
        '''设置记录状态.
        
        Args:
            domain_id 域名ID，必选
            record_id 记录ID，必选
            status {enable|disable} 新的状态，必选

        Raises:
            -15 域名已被封禁
            -7 企业账号的域名需要升级才能设置
            -8 代理名下用户的域名需要升级才能设置
            6 域名ID错误
            7 不是域名所有者或没有权限
            8 记录ID错误
            21 域名被锁定
        '''
        if not status in ('enable','disable'):
            logging.error(u'记录状态必须为enable 或 disable')
            raise DNSPodError(u'记录状态必须为enable 或 disable')

        url = self.base_url + '.Status'

        data = locals().copy()
        data.pop('self')

        return self.request(**data)

class DomainTest(unittest.TestCase):
    
    def setUp(self):
        self.domain = Domain('btyh17mxy@gmail.com','mushcode')
        try:
            self.domain.create('btyh17mxy.com')
        except Exception,e:
            logging.error(e)
    
    def tearDown(self):
        try:
            self.domain.remove(domain = 'btyh17mxy.com')
        except Exception,e:
            logging.error(e)
    
    def testCreate(self):
        self.domain.create('btyh17mxytest.com')
        self.domain.remove('btyh17mxytest.com')
        self.domain.list()
        self.domain.status('disable','btyh17mxy.com')
        self.domain.info('btyh17mxy.com')

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")
class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class Utils(object):
    
    def __init__(self):
        pass

    def export_records(self, record, domain_id, f):
        records = record.list(domain_id = domain_id)['records']
        csvwriter = UnicodeWriter(f, encoding='utf-8')

        write_header = True
        for record in records:
            if write_header:
                headers = record.keys()
                try:
                    headers.remove('hold')
                except Exception:
                    pass
                csvwriter.writerow(headers)

            record.pop(u'hold','')
            values = record.values()
            csvwriter.writerow(values)
            write_header = False

    def import_records(self, record, domain_id, f):
        #f = open(path,'r')
        csvreader = UnicodeReader(f, encoding='utf-8')
        
        headers = csvreader.next()[0].split(';')
        print headers
        records_data = []
        for line in csvreader:
            records_data.append(line[0].split(';'))
        
        for data in records_data:
            i = 0
            item = {}
            while i < len(headers):
                item[headers[i]]=data[i]
                i+=1
                print i
            item['domain_id'] = domain_id
            print item
            record.create(**item)
        
        
if __name__ == '__main__':
    logging.info('test')
    #unittest.main()
    record = Record('btyh17mxy@gmail.com','mushcode')
    #record.list('15566157')
    utils = Utils()
    #utils.export_records_csv(record, '15566157', 'records.csv')
    utils.import_records(record, '15566157', 'read.csv')
