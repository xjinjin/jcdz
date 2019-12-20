# -*- coding: utf-8 -*-
import json
import pickle

import requests
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

null = ''
true = ''
false = ''
SURL = "mysql+pymysql://cic_admin:TaBoq,,1234@192.168.1.170:3306/cicjust_splinter?charset=utf8&autocommit=true"
engine = create_engine(SURL)  # 定义引擎
Base = declarative_base()
session = sessionmaker(engine)()

import logging

from logging.handlers import TimedRotatingFileHandler


class get_log():
    def __init__(self):
        self.loglevel = logging.INFO

    def config_log(self, filename=None):
        logger = logging.getLogger(__name__)
        if not bool(filename):
            return self.config_stream_log(logger)
        else:
            return self.config_file_log(logger, filename)

    def config_file_log(self, logger, filename):
        formatter = logging.Formatter(
            ('%(asctime)s  %(pathname)s %(levelname)s 第%(lineno)d行'
             ' %(message)s'))
        logger.setLevel(self.loglevel)
        ch = logging.StreamHandler()
        ch.setLevel(self.loglevel)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        '''定义文件流'''
        fh = TimedRotatingFileHandler(filename=filename, when='s', interval=1)
        fh.setLevel(self.loglevel)
        fh.setFormatter(formatter)
        fh.suffix = ''
        logger.addHandler(fh)
        return logger

    def config_stream_log(self, logger):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(pathname)s--第%(lineno)d行--%(levelname)s--%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(self.loglevel)
        return logger


class JCDZT(Base):
    __tablename__ = 'jcdzt'
    id = Column(Integer, primary_key=True)
    mobile = Column(String(40))
    ztname = Column(String(40))
    token = Column(String(1000))
    start = Column(String(30))
    finshed = Column(String(30))
    status = Column(String(40))


class JCDEXPORT(Base):
    __tablename__ = 'jcdexport'
    id = Column(Integer, primary_key=True)
    mobile = Column(String(20))
    infoid = Column(String(20))
    name = Column(String(20))
    data = Column(LONGTEXT)
    kjqj = Column(String(20))


class JCDFLOW(Base):
    __tablename__ = 'jcdflow'
    id = Column(Integer, primary_key=True)
    now_time = Column(String(40))
    url = Column(String(120))
    flow = Column(LONGTEXT)
    state = Column(String(10))


class JCDFLOWSAVE(Base):
    __tablename__ = 'jcdflowsave'
    id = Column(Integer, primary_key=True)
    now_time = Column(String(40))
    request = Column(LargeBinary())
    response = Column(LargeBinary())
    path = Column(String(100))


Base.metadata.create_all(engine)
# 中间人
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.proxy.protocol
import mitmproxy.tcp
import mitmproxy.websocket
import time


class Proxy():
    def save_data(self, request, response, now_time):
        '''存flow数据'''
        try:
            result = JCDFLOWSAVE(now_time=now_time, request=request, response=response, path='')
            session.add(result)
            session.commit()
            # session.close()
        except:
            session.rollback()
            res = pickle.loads(response)
            path = './{}.txt'.format(now_time)
            fw = open(path, 'wb')
            pickle.dump(res, fw)
            fw.close()
            result = JCDFLOWSAVE(now_time=now_time, request=request,path=path)
            session.add(result)
            session.commit()

    def request(self, flow: mitmproxy.http.HTTPFlow):
        '''拦截请求数据'''
        # 序列化存request对象
        # print(type(flow))
        # flow_res=str(pickle.dumps(flow))
        # print(flow_res,'i am flow_res')
        # import os
        # os._exit(0)
        # now_time = datetime.datetime.now()
        # state='request'
        # self.save_data(flow_res,now_time,state)
        # ------------------------------------------
        # now_time = datetime.datetime.now()
        # url = flow.request.url
        # res = self.request_other_dealdatabag(flow)
        # flow_object = str(res)
        # state = 'request'
        # result = JCDFLOW(now_time=now_time, url=url, flow=flow_object, state=state)
        # session.add(result)
        # session.close()

    def request_other_dealdatabag(self, flow):
        '''解析请求包'''
        data_bag = {}
        data_bag['time_circle'] = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
        data_bag['web_name'] = flow.request.host
        data_bag['to_server'] = flow.request.url
        data_bag['to_header'] = flow.request.headers
        return data_bag

    def response_other_dealdatabag(self, flow):
        '''解析响应包'''
        data_bag = {}
        data_bag['response'] = flow.response.text  # 返回内容，已解码
        data_bag['time_circle'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data_bag['to_server'] = flow.request.url

        return data_bag

    def response(self, flow: mitmproxy.http.HTTPFlow):
        '''拦截响应数据'''
        request = flow.request
        response = flow.response
        now_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))
        request = pickle.dumps(request)
        response = pickle.dumps(response)
        self.save_data(request, response, now_time)
        # flow_res = str(pickle.dumps(flow))
        # print(flow_res,'flow_res')


        # state='response'
        # -----------------------------------------


        # now_time = datetime.datetime.now()
        # url = flow.request.url
        # res = self.response_other_dealdatabag(flow)
        # flow_object = str(res)
        # state = 'response'
        # result = JCDFLOW(now_time=now_time, url=url, flow=flow_object, state=state)
        # session.add(result)
        # session.close()
        # CLASSIFLY.databag(flow)


#
#
class classifly:
    def __init__(self):
        self.links = {'login': 'portal/initPortal',
                      'qyxx': 'edf/org/queryAll', 'zhanghu': '/ba/bankAccount/queryList',
                      'pingzheng': '/v1/gl/docManage/init', 'cunhuo': '/ba/inventory/queryList',
                      'gongyinshang': '/ba/supplier/queryList', 'kjkm': '/account/query', 'kehu': '/customer/queryList',
                      'bmry': '/v1/ba/person/queryList', 'yeb': '/balancesumrpt/query', 'myip': 'myip.ipip'}
        self.task = {'1': '凭证', '2': '余额表', '3': '企业信息', '4': '会计科目', '5': '部门人员', '6': '客户'
            , '7': '供应商', '8': '项目', '9': '存货及服务', '10': '账户'}

        # myip  ---->mobile

    def databag(self, flow):
        '''处理url'''
        for label, link in self.links.items():
            if link in flow.request.url:
                result = self.deal_data(flow, label)

    def deal_data(self, *args):
        '''处理数据'''
        flow, label = args
        if 'login' == label:
            self.login(flow)
        elif 'qyxx' == label:
            self.qyxx(flow)
        elif 'zhanghu' == label:
            self.zhanghu(flow)
        elif 'pingzheng' == label:
            self.pingzheng(flow)
        elif 'cunhuo' == label:  # //
            self.cunhuo(flow)
        elif 'gongyinshang' == label:
            self.gongyinshang(flow)
        elif 'kjkm' == label:
            self.kjkm(flow)
        elif 'kehu' == label:
            self.kehu(flow)
        elif 'bmry' == label:
            self.bmry(flow)
        elif 'yeb' == label:
            self.yeb(flow)
        elif 'myip' == label:
            self.myip(flow)

    def bmry(self, flow):
        '''处理部门人员信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='bmry')
        dicts = self.fetch_data(dicts)

        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def kjkm(self, flow):
        '''处理会计科目信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='kjkm')
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def kehu(self, flow):
        '''处理客户信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='kehu')
        dicts = self.fetch_data(dicts)

        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def cunhuo(self, flow):
        '''处理存货信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='cunhuo')
        dicts = self.fetch_data(dicts)

        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def gongyinshang(self, flow):
        '''处理供应商信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='gongyinshang')
        dicts = self.fetch_data(dicts)

        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def yeb(self, flow):
        '''处理余额表'''
        token = dict(flow.request.headers)['token']
        beginDate = eval(flow.request.content)['beginDate']
        headers = dict(flow.request.headers)
        if ':authority' in headers:
            headers.pop(':authority')
            headers.pop('cookie')
        cookies = dict(flow.request.cookies)
        data = json.dumps(
            {'init_date_start': '2019-01-01T00:00:00.000Z', 'endAccountGrade': 5, 'showZero': 'true', 'printType': 0,
             'currencyId': '0', 'showAuxAccCalc': 'true', 'beginAccountCode': '', 'beginAccountGrade': 1,
             'init_date_end': '2019-01-01T00:00:00.000Z', 'onlyShowEndAccount': 'false', 'endAccountCode': '',
             'beginDate': '2016-01', 'beginYear': '2016', 'beginPeriod': '01', 'endDate': '2022-01',
             'endYear': '2022', 'endPeriod': '01', 'isCalcMulti': false, 'isCalcQuantity': false, 'pageSize': 100,
             'currentPage': 1, 'needPaging': true})
        resposne = requests.post(url='https://dz.jchl.com/v1/gl/report/balancesumrpt/query', headers=headers, json=data,
                                 cookies=cookies)
        if 'error' in eval(resposne.text):
            return
        else:
            data = eval(resposne.text)['value']
            dicts = dict(data=data, token=token, label='yeb', infoid='yeb', beginDate=beginDate)
            dicts = self.fetch_data(dicts)
            self.yeb_data(dicts)

    def yeb_data(self, dicts):
        '''处理余额表信息'''
        pass

    def pingzheng(self, flow):
        '''处理凭证信息'''
        token = dict(flow.request.headers)['token']
        headers = dict(flow.request.headers)
        if ':authority' in headers:
            headers.pop(':authority')
            headers.pop('cookie')
        cookies = dict(flow.request.cookies)
        data = json.dumps({'voucherState': '', 'summary': '', 'accountId': '', 'endCode': '', 'startCode': '',
                           'displayDate': '2019-10', 'endAmount': '', 'startAmount': '', 'startYear': 2016,
                           'startPeriod': 1, 'endYear': 2025, 'endPeriod': 12,
                           'page': {'pageSize': 1000, 'currentPage': 1}, 'userOrderField': '', 'order': ''})
        resposne = requests.post(url='https://dz.jchl.com/v1/gl/docManage/init', headers=headers, json=data,
                                 cookies=cookies)
        results = eval(resposne.text)['value']['dtoList']
        container = {}
        for i in results:
            voucherDate = i['voucherDate']
            if voucherDate not in container:
                container['{}'.format(voucherDate)] = [i]
            else:
                box = container['{}'.format(voucherDate)]
                box.append(i)
                container['{}'.format(voucherDate)] = box
        dicts = dict(box=container, token=token, label='pingzheng', infoid='pingzheng')
        dicts = self.fetch_data(dicts)
        self.pz_data(dicts)

    def pz_data(self, dicts):
        '''处理凭证数据'''
        box = dicts['box']
        for i in box:
            kjqj = i
            infodata = box[kjqj]
            result = session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == i,
                                                     JCDEXPORT.ztname == dicts['ztname'],
                                                     JCDEXPORT.mobile == dicts['mobile'],
                                                     JCDEXPORT.infoid == 'pingzheng').first()
            if result:
                session.execute(
                    'update {} set data="{}"  where mobile = "{}" and ztname="{}" and kjqj="{}"'.format(
                        'jcdexport', infodata, dicts['mobile'], dicts['name'], kjqj))
            else:
                result = JCDEXPORT(mobile=dicts['mobile'], infoid='pingzheng', ztname=dicts['ztname'],
                                   data=infodata, kjqj=kjqj)
                session.add(result)
            session.close()

    def zhanghu(self, flow):
        '''处理币别信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='zhanghu')
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def qyxx(self, flow):
        '''处理企业信息'''
        token = dict(flow.request.headers)['token']
        data = eval(flow.response.text)['value']
        dicts = dict(data=data, token=token, label='qyxx', infoid='qyxx')
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)
        pass

    def fetch_data(self, dicts):
        '''获取数据'''
        results = session.query(JCDZT).filter(JCDZT.token == dicts['token']).first()
        for i in results:
            dicts['mobile'] = i.mobile
            dicts['ztname'] = i.ztname
        return dicts

    def login(self, flow):
        '''解析login'''
        token = dict(flow.request.headers)['token']
        user = eval(flow.response.text)['value']['user']
        org = eval(flow.response.text)['value']['org']
        mobile = user['mobile']
        ztname = org['name']
        dicts = dict(token=token, mobile=mobile, label='login', ztname=ztname)
        if self.search_data(dicts):
            pass
        else:
            result = self.add_data(dicts)

    def search_data(self, dicts):
        '''查找数据'''
        if 'login' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.token == dicts['token']).first()
        elif 'qyxx' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'qyxx')
        elif 'zhanghu' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'zhanghu')
        elif 'cunhuo' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'cunhuo')
        elif 'gongyinshang' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'gongyinshang')
        elif 'kjkm' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'kjkm')
        elif 'kehu' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'kehu')
        elif 'bmry' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.infoid == 'bmry')

    def update_data(self, dicts):
        '''更新数据'''
        if 'qyxx' in dicts:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'cunhuo' in dicts:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'gongyinshang' in dicts:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'kjkm' in dicts:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'kehu' in dicts:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'bmry' in dicts:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))

    def myip(self, flow):
        '''处理相关请求获取账套状态'''  # 进财税
        url = flow.request.url
        mobile = url.split('mobile=')[-1]
        result = session.query(JCDZT).filter(
            JCDZT.mobile == mobile).all()
        lists = []
        dicts = {'id': '', 'mobile': '', 'ztname': '', 'start': '', 'finshed': '', 'status': ''}
        num = 1
        for i in result:
            dicts['num'] = num
            dicts['mobile'] = i.mobile
            dicts['ztname'] = i.ztname
            dicts['start'] = i.start
            dicts['finshed'] = i.finshed
            dicts['status'] = i.status
            lists.append(dicts)
            num += 1
        if not lists:
            flow.response.set_text('0')
        else:
            res = {'code': 0, 'data': lists, 'count': len(lists)}
            flow.response.set_text(json.dumps(res))

    def add_data(self, dicts):
        '''增加数据'''
        result = ''
        if 'login' in dicts.values():
            result = JCDZT(mobile=dicts['mobile'], ztname='login', token=dicts['token'],
                           start='', finshed='', status='')
        elif 'cunhuo' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], infoid='cunhuo', ztname=dicts['ztname'],
                               data=dicts['data'],
                               kjqj='')
        elif 'gongyinshang' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], infoid='gongyinshang', ztname=dicts['ztname'],
                               data=dicts['data'],
                               kjqj='')
        elif 'kjkm' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], infoid='kjkm', name=dicts['ztname'], data=dicts['data'],
                               kjqj='')
        elif 'kehu' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], infoid='kehu', name=dicts['ztname'], data=dicts['data'],
                               kjqj='')
        elif 'bmry' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], infoid='bmry', name=dicts['ztname'], data=dicts['data'],
                               kjqj='')
        session.add(result)
        session.close()


# CLASSIFLY = classifly()
# loger = get_log()
# logger = loger.config_log()
addons = [Proxy()]
