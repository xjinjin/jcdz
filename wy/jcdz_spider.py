# -*- coding: utf-8 -*-
#创造页面，把eagled 和 account放在一起
import datetime
import json

from sqlalchemy import create_engine, Column, Integer, String
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
    account = Column(String(40))
    ztname = Column(String(40))
    site = Column(String(20))
    start_time = Column(String(30))
    finshed_time = Column(String(30))
    status = Column(String(40))



class JCDEXPORT(Base):
    __tablename__ = 'jcdexport'
    id = Column(Integer, primary_key=True)
    site = Column(String(20))
    account = Column(String(20))
    zt_id = Column(String(20))
    infoname_id = Column(String(20))
    infodata = Column(LONGTEXT)
    kjqj = Column(String(20))


class JCDINFONAME(Base):
    __tablename__ = 'jcdinfoname'
    id = Column(Integer, primary_key=True)
    infoname = Column(String(20))
    site = Column(String(20))



Base.metadata.create_all(engine)

# 中间人
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.proxy.protocol
import mitmproxy.tcp
import mitmproxy.websocket

TASK = {'1': '凭证', '2': '余额表', '3': '企业信息', '4': '会计科目', '5': '部门人员', '6': '客户'
    , '7': '供应商', '8': '项目', '9': '存货及服务', '10': '账户'}


class Parse():
    def save(self, data):  # 存库
        if data.get('zttask') == 'queryOrgList':  # 所有公司
            account = data['account']
            for i in data['box']:
                ztname, start_time = i['ztname'], i['start_time']
                result = session.query(JCDZT).filter(JCDZT.ztname == ztname).first()
                if result:
                    continue
                else:
                    result = JCDZT(account=account,
                                   ztname=ztname, site='jch1', start_time=start_time, finshed_time='', status='')
                    session.add(result)
        elif data.get(
                'zttask') == 'queryAll' or 'customer_queryList' or 'supplier_queryList' or 'bankAccount_queryList' or 'account_query' or 'project_queryList' or 'inventory_queryList' \
                or 'balancesumrpt_query':
            path = data.get('path')
            infodata = data.get('box')
            if data.get('zttask') == 'balancesumrpt_query':
                account, zt_id, infoname_id, kjqj = path.split('/')
            else:
                kjqj = ''
                account, zt_id, infoname_id = path.split('/')
            result = session.query(JCDEXPORT).filter(
                JCDEXPORT.infoname_id == infoname_id, JCDEXPORT.zt_id == zt_id, JCDEXPORT.kjqj == kjqj).first()
            if result:
                session.execute(
                    'update {} set infodata="{}"  where zt_id = "{}" and infoname_id="{}"'.format(
                        'jcdexport', infodata, zt_id, infoname_id))
            else:
                result = JCDEXPORT(site='jch1', account=account, zt_id=zt_id, infoname_id=infoname_id,
                                   infodata=str(infodata), kjqj=kjqj)
                session.add(result)
                session.commit()
                session.close()
                return 'success'

        elif data.get('zttask') == 'docManage/query':
            path = data.get('path')
            account, zt_id, infoname_id = path.split('/')
            box = data['box']
            for i in box:
                kjqj = i
                infodata = box[kjqj]
                result = session.query(JCDEXPORT).filter(JCDEXPORT.kjqj == i, JCDEXPORT.account == account,
                                                         JCDEXPORT.zt_id == zt_id).first()
                if result:
                    continue
                else:
                    result = JCDEXPORT(site='jch1', account=account, zt_id=zt_id, infoname_id=infoname_id,
                                       infodata=str(infodata), kjqj=kjqj)
                    session.add(result)
                session.commit()
                session.close()
            return 'success'  # 返回接口


class Proxy():
    def request(self, flow: mitmproxy.http.HTTPFlow):
        pass

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 如果task为end则将这个公司的最后期限填上即可。之后判断这地方时候有期限，且本月是否等于该期限，如果等于则换一个,这个就是即将需要爬取的任务。
        # 每次更新一次批次就将这个id发给阮工。
        if 'myip.ipip' in flow.request.url:
            if 'all' in flow.request.url:  # 需要完成的账套
                cookies = dict(flow.request.cookies)
                account = cookies['account']
                result = session.query(JCDZT).filter(
                    JCDZT.account == account).all()
                dict_ = {}
                datetimenowTime = datetime.datetime.now().strftime('%Y%m')
                for i in result:
                    start_time = i.start_time
                    finshed_time = i.finshed_time
                    if not start_time:
                        a, b = str(i.id), i.ztname  # {'1','xxxx公司'}
                        dict_[a] = b
                    elif not finshed_time:
                        a, b = str(i.id), i.ztname  # {'1','xxxx公司'}
                        dict_[a] = b
                    else:
                        if start_time[0:7].replace('-', '') < datetimenowTime or finshed_time[0:7].replace('-',

                                                                       '') < datetimenowTime:
                            a, b = str(i.id), i.ztname  # {'1','xxxx公司'}
                            dict_[a] = b
                print(dict_)
                flow.response.set_text(json.dumps(dict_))

            elif 'end' in flow.request.url:
                cookies = dict(flow.request.cookies)
                zt_id = cookies['zt_id']
                datetimenowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session.execute(
                    'update {} set finshed_time="{}" ,state="入库" where zt_id = "{}"'.format(
                        'jcdzt', datetimenowTime, zt_id))
                # 调阮工接口
                print('成功zt_id是{}'.format(zt_id))

            elif 'user' in flow.request.url:  # 获取进度跟踪
                url = flow.request.url
                account = url.split('user=')[-1]
                result = session.query(JCDZT).filter(
                    JCDZT.account == account).all()
                lists = []
                dicts = {'id': '', 'account': '', 'password': '', 'time_scope': '', 'complete_state': '', 'unlock': ''}
                num = 1
                for i in result:
                    account = i.account
                    password = i.ztname
                    time_scope = i.start_time
                    complete_state = i.finshed_time
                    unlock = i.status
                    dicts['id'] = num
                    dicts['account'] = account
                    dicts['password'] = password
                    dicts['time_scope'] = time_scope
                    dicts['complete_state'] = complete_state
                    dicts['unlock'] = unlock
                    lists.append(dicts)
                    num += 1
                if not lists:
                    flow.response.set_text('0')
                else:
                    res = {'code': 0, 'data': lists, 'count': len(lists)}
                    flow.response.set_text(json.dumps(res))

        elif 'docManage/query' in flow.request.url:  # 凭证

            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '1'
            data = eval(flow.response.text)['value']['dtoList']
            container = {}
            for i in data:
                voucherDate = i['voucherDate']
                if voucherDate not in container:
                    container['{}'.format(voucherDate)] = [i]
                else:
                    box = container['{}'.format(voucherDate)]
                    box.append(i)
                    container['{}'.format(voucherDate)] = box
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            zttask = 'docManage/query'
            handout = {'zttask': zttask, 'box': container, 'path': path}
            state = parse.save(handout)

        elif '/balancesumrpt/query' in flow.request.url:  # 余额表
            data = eval(flow.response.text)
            if 'error' in data:
                return
            else:
                data = data['value']
                zttask = 'balancesumrpt_query'
                cookies = dict(flow.request.cookies)
                account = cookies['account']
                zt_id = cookies['zt_id']
                infoname_id = '2'
                beginDate = eval(flow.request.content)['beginDate']
                path = '{}/{}/{}/{}'.format(account, zt_id, infoname_id, beginDate)
                handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
                state = parse.save(handout)

        elif 'org/queryAll' in flow.request.url:  # 企业信息
            data = eval(flow.response.text)['value']
            zttask = 'queryAll'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '3'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
            state = parse.save(handout)

        elif '/account/query' in flow.request.url:  # 会计科目
            data = eval(flow.response.text)['value']
            zttask = 'account_queryList'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '4'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
            state = parse.save(handout)

        elif '/customer/queryList' in flow.request.url:
            data = eval(flow.response.text)['value']  # 获取客户
            if not data['list']:
                return
            zttask = 'customer_queryList'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '6'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
            state = parse.save(handout)

        elif 'supplier/queryList' in flow.request.url:
            data = eval(flow.response.text)['value']  # 获取供应商
            if not data['list']:
                return
            zttask = 'supplier_queryList'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '7'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
            state = parse.save(handout)

        elif 'project/queryList' in flow.request.url:  # 获取项目
            data = eval(flow.response.text)['value']
            if not data['list']:
                return ''
            zttask = 'project_queryList'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '8'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
            state = parse.save(handout)

        elif 'inventory/queryList' in flow.request.url:  # 存货及服务
            data = eval(flow.response.text)['value']
            if not data['list']:
                return
            zttask = 'inventory_queryList'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '9'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}
            state = parse.save(handout)

        elif 'bankAccount/queryList' in flow.request.url:  # 账户
            data = eval(flow.response.text)['value']
            if not data['list']:
                return
            zttask = 'queryAll'
            cookies = dict(flow.request.cookies)
            account = cookies['account']
            zt_id = cookies['zt_id']
            infoname_id = '10'
            path = '{}/{}/{}'.format(account, zt_id, infoname_id)
            handout = {'zttask': zttask, 'box': data, 'path': path}  # Aa111111
            state = parse.save(handout)

        elif 'queryOrgList' in flow.request.url:  # 所有账套
            data = eval(flow.response.text)['value']
            print(flow.request.headers)
            box = []
            for i in data:
                infos = {}
                infos['ztname'] = i['name']
                infos['zt_id']=i['id']
                infos['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                box.append(infos)
            zttask = 'queryOrgList'
            try:
                cookies = dict(flow.request.cookies)
                print(cookies)
            except Exception as e:
                pass
            else:
                account = cookies['account']
                handout = {'zttask': zttask, 'box': box, 'account': account}

            state = parse.save(handout)


parse = Parse()
addons = [Proxy()]
