# -*- coding: utf-8 -*-
import json
import pickle
import time

import pandas
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
    label = Column(String(20))
    ztname = Column(String(20))
    data = Column(LONGTEXT)
    kjqj = Column(String(20))


class JCDFLOWSAVE(Base):
    __tablename__ = 'jcdflowsave'
    id = Column(Integer, primary_key=True)
    now_time = Column(String(40))
    request = Column(LargeBinary())
    response = Column(LargeBinary())


Base.metadata.create_all(engine)

null = ''
true = ''
false = ''
SURL = "mysql+pymysql://cic_admin:TaBoq,,1234@192.168.1.170:3306/cicjust_splinter?charset=utf8&autocommit=true"
engine = create_engine(SURL)  # 定义引擎
Base = declarative_base()
session = sessionmaker(engine)()


# request=row_data['request']
# res=pickle.loads(request)


class classifly:
    def __init__(self):
        self.links = {'login': 'portal/initPortal',
                      'qyxx': 'edf/org/queryAll',
                      'zhanghu': '/ba/bankAccount/queryList',
                      # 'pingzhenginit': '/v1/gl/docManage/init',
                      'pingzheng': '/v1/gl/docManage/query',
                      'cunhuo': '/ba/inventory/queryList',
                      'gongyinshang': '/ba/supplier/queryList',
                      'kjkm': '/account/query',
                      'kehu': '/customer/queryList',
                      'bmry': '/v1/ba/person/queryList',
                      'yeb': '/balancesumrpt/query',
                      'fzyeb':'/balanceauxrpt/query',
                      'myip': 'myip.ipip'}
        self.task = {'1': '凭证', '2': '余额表', '3': '企业信息', '4': '会计科目', '5': '部门人员', '6': '客户'
            , '7': '供应商', '8': '项目', '9': '存货及服务', '10': '账户'}

    def fetch_sql(self):
        '''从数据库里取数据'''
        while True:
            data = pandas.read_sql("select * from jcdflowsave", engine)
            if len(data.index) == 0:
                time.sleep(10)  # 睡600秒
                # continue
            else:
                for i in data.index.values:  # 获取行号的索引，并对其进行遍历：
                    # 根据i来获取每一行指定的数据 并利用to_dict转成字典
                    row_data = data.loc[i, ['id', 'now_time', 'request', 'response', 'path']].to_dict()
                    print(row_data['id'])
                    session.query(JCDFLOWSAVE).filter(JCDFLOWSAVE.id == int(row_data['id'])).delete()
                    session.commit()
                    self.databag(row_data)
                # results = session.query(JCDFLOWSAVE).all()
                # # session.query(JCDFLOWSAVE).filter(JCDFLOWSAVE.id == int(row_data['id'])).delete()
                # session.delete(results)
                # session.commit()

    def databag(self, row_data):
        '''处理url'''
        id_ = row_data['id']
        # print(id_)
        # now_time = row_data['now_time']
        flow_request = pickle.loads(row_data['request'])
        try:
            flow_response = pickle.loads(row_data['response'])
        except TypeError as e:
            path=row_data['path']
            # print(path)
            with open(file=path,mode='rb')  as f:
                result=f.read()
                flow_response=pickle.loads(result)
        path = row_data['path']
        num = 0
        for label, link in self.links.items():  # 确定此url是否有效    1.入库    2.JCDFLOWSAVE库中删除
            if link in flow_request.url:
                num += 1
                self.deal_data(flow_request, flow_response, label, path)
                break
        if num == 0:        # 说明这条记录是无效的url，直接删除
            try:
                user = session.query(JCDFLOWSAVE).get(str(id_))
                session.delete(user)
                session.commit()
            except Exception as e:
                print(id_, 'error')
        else:
            pass  # 将相关信息在存到另一个数据库中

    def deal_data(self, *args):       # 处理需要的数据，有效的url
        '''处理数据'''
        flow_request, flow_response, label, path = args
        # print(label)
        if 'login' == label:
            self.login(flow_request, flow_response, label)
        elif 'qyxx' == label:
            self.qyxx(flow_request, flow_response, label,path)
        elif 'zhanghu' == label:
            self.zhanghu(flow_request, flow_response, label)
        # elif 'pingzhenginit' == label or 'pingzhengquery' == label:
        elif 'pingzheng' == label:
            self.pingzheng(flow_request, flow_response, label, path)
        elif 'cunhuo' == label:  # //
            self.cunhuo(flow_request, flow_response, label)
        elif 'gongyinshang' == label:
            self.gongyinshang(flow_request, flow_response, label)
        elif 'kjkm' == label:
            self.kjkm(flow_request, flow_response, label)
        elif 'kehu' == label:
            self.kehu(flow_request, flow_response, label)
        elif 'bmry' == label:
            self.bmry(flow_request, flow_response, label)
        elif 'yeb' == label:
            self.yeb(flow_request, flow_response, label, path)
            # elif 'myip' == label:
            #     self.myip(flow_request, flow_response, label)
        elif 'fzyeb' == label:
            self.fzyeb(flow_request, flow_response, label)

    def bmry(self, flow_request, flow_response, label):
        '''处理部门人员信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            # real = self.search_data(dicts)
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def kjkm(self, flow_request, flow_response, label):
        '''处理会计科目信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def kehu(self, flow_request, flow_response, label):
        '''处理客户信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)

        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def cunhuo(self, flow_request, flow_response, label):
        '''处理存货信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)

        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def gongyinshang(self, flow_request, flow_response, label):
        '''处理供应商信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            result = self.add_data(dicts)

    def fzyeb(self, flow_request, flow_response, label):  # 每个月的值
        '''处理余额表'''
        token = dict(flow_request.headers)['token']
        beginPeriod = eval(flow_request.content)['beginPeriod']  # dict,str
        beginYear = eval(flow_request.content)['beginYear']  # dict,str
        date = '{}-{}'.format(beginYear,beginPeriod)
        data = eval(flow_response.text)['value']    # dict
        if data:
            dicts = dict(data=data, token=token, label=label, date=date)
            dicts = self.fetch_data(dicts)
            self.yeb_data(dicts)
        else:
            pass

        # token = dict(flow_request.headers)['token']
        # beginDate = eval(flow_request.content)['beginDate']
        # headers = dict(flow_request.headers)
        # if ':authority' in headers:
        #     headers.pop(':authority')
        #     headers.pop('cookie')
        # cookies = dict(flow_request.cookies)
        # data = json.dumps(
        #     {'init_date_start': '2019-01-01T00:00:00.000Z', 'endAccountGrade': 5, 'showZero': 'true', 'printType': 0,
        #      'currencyId': '0', 'showAuxAccCalc': 'true', 'beginAccountCode': '', 'beginAccountGrade': 1,
        #      'init_date_end': '2019-01-01T00:00:00.000Z', 'onlyShowEndAccount': 'false', 'endAccountCode': '',
        #      'beginDate': '2016-01', 'beginYear': '2016', 'beginPeriod': '01', 'endDate': '2022-01',
        #      'endYear': '2022', 'endPeriod': '01', 'isCalcMulti': false, 'isCalcQuantity': false, 'pageSize': 100,
        #      'currentPage': 1, 'needPaging': true})
        # resposne = requests.post(url='https://dz.jchl.com/v1/gl/report/balancesumrpt/query', headers=headers, json=data,
        #                          cookies=cookies)
        # if 'error' in eval(resposne.text):
        #     return
        # else:
        #     data = eval(resposne.text)['value']
        #     dicts = dict(data=data, token=token, label=label, beginDate=beginDate)
        #     dicts = self.fetch_data(dicts)
        #     self.yeb_data(dicts)

    def fzyeb_data(self, dicts):
        '''处理余额表信息'''
        result = session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == dicts['date'],
                                                 JCDEXPORT.ztname == dicts['ztname'],
                                                 JCDEXPORT.mobile == dicts['mobile'],
                                                 JCDEXPORT.label == dicts['label']).first()
        if result:
            # session.execute(
            #     'update {} set data="{}"  where mobile = "{}" and ztname="{}" and kjqj="{}" and label="{}"'.format(
            #         'jcdexport', json.dumps(dicts['data']), dicts['mobile'], dicts['ztname'], dicts['date'],dicts['label']))

            session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == dicts['date'], JCDEXPORT.ztname == dicts['ztname'],
                                              JCDEXPORT.mobile == dicts['mobile'], JCDEXPORT.label == dicts['label']
                                              ).update({'data': json.dumps(dicts['data'])})
        else:
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']), kjqj=dicts['date'])
            session.add(result)
        session.commit()

    def yeb(self, *args):  # 每个月的值
        '''处理余额表'''
        flow_request, flow_response, label, path = args
        token = dict(flow_request.headers)['token']
        beginDate = eval(flow_request.content)['beginDate']  # dict,str
        data = eval(flow_response.text)['value']    # dict
        dicts = dict(data=data, token=token, label=label, beginDate=beginDate)
        # print(dicts)
        dicts = self.fetch_data(dicts)
        self.yeb_data(dicts)

        # token = dict(flow_request.headers)['token']
        # beginDate = eval(flow_request.content)['beginDate']
        # headers = dict(flow_request.headers)
        # if ':authority' in headers:
        #     headers.pop(':authority')
        #     headers.pop('cookie')
        # cookies = dict(flow_request.cookies)
        # data = json.dumps(
        #     {'init_date_start': '2019-01-01T00:00:00.000Z', 'endAccountGrade': 5, 'showZero': 'true', 'printType': 0,
        #      'currencyId': '0', 'showAuxAccCalc': 'true', 'beginAccountCode': '', 'beginAccountGrade': 1,
        #      'init_date_end': '2019-01-01T00:00:00.000Z', 'onlyShowEndAccount': 'false', 'endAccountCode': '',
        #      'beginDate': '2016-01', 'beginYear': '2016', 'beginPeriod': '01', 'endDate': '2022-01',
        #      'endYear': '2022', 'endPeriod': '01', 'isCalcMulti': false, 'isCalcQuantity': false, 'pageSize': 100,
        #      'currentPage': 1, 'needPaging': true})
        # resposne = requests.post(url='https://dz.jchl.com/v1/gl/report/balancesumrpt/query', headers=headers, json=data,
        #                          cookies=cookies)
        # if 'error' in eval(resposne.text):
        #     return
        # else:
        #     data = eval(resposne.text)['value']
        #     dicts = dict(data=data, token=token, label=label, beginDate=beginDate)
        #     dicts = self.fetch_data(dicts)
        #     self.yeb_data(dicts)

    def yeb_data(self, dicts):
        '''处理余额表信息'''
        result = session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == dicts['beginDate'],
                                                 JCDEXPORT.ztname == dicts['ztname'],
                                                 JCDEXPORT.mobile == dicts['mobile'],
                                                 JCDEXPORT.label == dicts['label']).first()
        if result:
            # session.execute(
            #     'update {} set data="{}"  where mobile = "{}" and ztname="{}" and kjqj="{}" and label="{}"'.format(
            #         'jcdexport', json.dumps(dicts['data']), dicts['mobile'], dicts['ztname'], dicts['beginDate'],dicts['label']))
            # print('true')
            session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == dicts['beginDate'], JCDEXPORT.ztname == dicts['ztname'],
                                              JCDEXPORT.mobile == dicts['mobile'], JCDEXPORT.label == dicts['label']
                                              ).update({'data': json.dumps(dicts['data'])})
        else:
            # print('false')
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']), kjqj=dicts['beginDate'])
            session.add(result)
        session.commit()

    def pingzheng(self, *args):
        '''处理凭证信息'''
        flow_request, flow_response, label, path = args
        token = dict(flow_request.headers)['token']
        # headers = dict(flow_request.headers)
        # print(headers)
        # if ':authority' in headers:
        #     headers.pop(':authority')
        #     headers.pop('cookie')
        # cookies = dict(flow_request.cookies)
        # print(cookies)
        # voucherState":null,"summary":null,"accountId":null,"endCode":null,"simpleCondition":null,"startCode":null,
        # "displayDate":"2019-12","endAmount":null,"startAmount":null,"startYear":2019,"startPeriod":1,"endYear":2025,"
        # endPeriod":12,"page":{"pageSize":10,"currentPage":1},"userOrderField":null,"order":null}
        # data = json.dumps({'voucherState': '', 'summary': '', 'accountId': '', 'endCode': '', 'startCode': '',
        #                    'displayDate': '2019-10', 'endAmount': '', 'startAmount': '', 'startYear': 2016,
        #                    'startPeriod': 1, 'endYear': 2025, 'endPeriod': 12,
        #                    'page': {'pageSize': 1000, 'currentPage': 1}, 'userOrderField': '', 'order': ''})
        # resposne = requests.post(url='https://dz.jchl.com/v1/gl/docManage/query', headers=headers, json=data,
        #                          cookies=cookies)
        # print(resposne.text)
        results = eval(flow_response.text)['value']['dtoList']
        if results:
            container = {}
            for i in results:   # i 是一行凭证数据，字典形式
                voucherDate = i['voucherDate']
                if voucherDate not in container:
                    container['{}'.format(voucherDate)] = [i]
                else:
                    box = container['{}'.format(voucherDate)]
                    box.append(i)
                    container['{}'.format(voucherDate)] = box
            dicts = dict(box=container, token=token, label=label)
            dicts = self.fetch_data(dicts)      # 字典 补充账套名，电话
            self.pingzheng_data(dicts)

    def pingzheng_data(self, dicts):
        '''处理凭证数据'''
        box = dicts['box']
        for i in box:
            kjqj = i                # 日期:'2019-11-30'
            infodata = box[kjqj]    # 每个日期的列表有多个字典凭证
            result = session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == i,
                                                     JCDEXPORT.ztname == dicts['ztname'],
                                                     JCDEXPORT.mobile == dicts['mobile'],
                                                     JCDEXPORT.label == dicts['label']).first()
            if result:
                # session.execute(
                #     'update {} set data="{}"  where mobile = "{}" and ztname="{}" and kjqj="{}"'.format(
                #         'jcdexport', json.dumps(infodata), dicts['mobile'], dicts['ztname'], kjqj))
                session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == i,JCDEXPORT.ztname == dicts['ztname'],
                                                  JCDEXPORT.mobile == dicts['mobile'],JCDEXPORT.label == dicts['label']
                                                  ).update({'data': json.dumps(infodata)})
            else:
                result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                                   data=json.dumps(infodata), kjqj=kjqj)
                session.add(result)
            session.commit()
            # session.close()

    def zhanghu(self, flow_request, flow_response, label):
        '''处理账户信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']  # dict
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)
        if self.search_data(dicts):
            self.update_data(dicts)
        else:
            self.add_data(dicts)

    def qyxx(self, flow_request, flow_response, label,path):
        '''处理企业信息'''
        token = dict(flow_request.headers)['token']
        data = eval(flow_response.text)['value']
        dicts = dict(data=data, token=token, label=label)
        dicts = self.fetch_data(dicts)      # 补：ztname,mobile
        if self.search_data(dicts):         # 判断数据库中是否有此公司的企业信息
            self.update_data(dicts)         # 用现在的数据更新数据库
        else:
            result = self.add_data(dicts)   # 没有则添加

    def fetch_data(self, dicts):
        '''获取数据'''
        result = session.query(JCDZT).filter(JCDZT.token == dicts['token']).all()
        for i in result:
            dicts['mobile'] = i.mobile
            dicts['ztname'] = i.ztname
        return dicts

    def login(self, flow_request, flow_response, label):
        '''解析login'''
        token = dict(flow_request.headers)['token']
        user = eval(flow_response.text)['value']['user']   # dict
        org = eval(flow_response.text)['value']['org']
        mobile = user['mobile']
        ztname = org['name']
        dicts = dict(token=token, mobile=mobile, label=label, ztname=ztname)
        if self.search_data(dicts):         # 根据token判断此公司是否在JCDZT数据库中    1.pass    2.添加到JCDZT
            pass
        else:
            result = self.add_data(dicts)

    def search_data(self, dicts):
        '''查找数据'''
        if 'qyxx' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()
        elif 'zhanghu' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()
        elif 'cunhuo' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()
        elif 'gongyinshang' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()
        elif 'kjkm' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()
        elif 'kehu' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()
        elif 'bmry' in dicts.values():
            return session.query(JCDEXPORT).filter(JCDEXPORT.mobile == dicts['mobile'],
                                                   JCDEXPORT.ztname == dicts['ztname'],
                                                   JCDEXPORT.label == dicts['label']).first()

        elif 'login' in dicts.values():
            return session.query(JCDZT).filter(JCDZT.token == dicts['token']).first()

    def update_data(self, dicts):
        '''更新数据'''
        if 'qyxx' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif  'zhanghu' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif  'cunhuo' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'gongyinshang' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'kjkm' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'kehu' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))
        elif 'bmry' == dicts['label']:
            session.execute(
                'update {} set data="{}"  where mobile = "{}" and ztname="{}"'.format(
                    'jcdexport', dicts['data'], dicts['mobile'], dicts['ztname']))

    # def myip(self, flow_request, flow_response, label):
    #     '''处理相关请求获取账套状态'''  # 进财税
    #     url = flow_request.url
    #     mobile = url.split('mobile=')[-1]
    #     result = session.query(JCDZT).filter(
    #         JCDZT.mobile == mobile).all()
    #     lists = []
    #     dicts = {'id': '', 'mobile': '', 'ztname': '', 'start': '', 'finshed': '', 'status': ''}
    #     num = 1
    #     for i in result:
    #         dicts['num'] = num
    #         dicts['mobile'] = i.mobile
    #         dicts['ztname'] = i.ztname
    #         dicts['start'] = i.start
    #         dicts['finshed'] = i.finshed
    #         dicts['status'] = i.status
    #         lists.append(dicts)
    #         num += 1
    #     if not lists:
    #         flow_response.set_text('0')
    #     else:
    #         res = {'code': 0, 'data': lists, 'count': len(lists)}
    #         flow_response.set_text(json.dumps(res))

    def add_data(self, dicts):
        '''增加数据'''
        result = ''
        if 'login' in dicts.values():
            result = JCDZT(mobile=dicts['mobile'], ztname=dicts['ztname'], token=dicts['token'],
                           start='', finshed='', status='')
        elif 'cunhuo' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']),
                               kjqj='')
        elif 'gongyinshang' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']),
                               kjqj='')
        elif 'kjkm' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']),
                               kjqj='')
        elif 'kehu' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']),
                               kjqj='')
        elif 'bmry' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']),
                               kjqj='')

        elif 'zhanghu' in dicts.values():
            result = JCDEXPORT(mobile=dicts['mobile'], label=dicts['label'], ztname=dicts['ztname'],
                               data=json.dumps(dicts['data']))
        elif 'qyxx' in dicts.values():
            result=JCDEXPORT(mobile=dicts['mobile'],label=dicts['label'],ztname=dicts['ztname'],data=json.dumps(dicts['data']))
        session.add(result)
        session.commit()


CLASSIFLY = classifly().fetch_sql()
# loger = get_log()
# logger = loger.config_log()
# addons = [Proxy()]
