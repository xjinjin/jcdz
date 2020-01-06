# -*- coding: utf-8 -*-

from db_proxy import JCDFLOWSAVE,session

import pickle
import time

import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.proxy.protocol
import mitmproxy.tcp
import mitmproxy.websocket


class Proxy():

    def __init__(self):
        self.links = ['portal/initPortal',
                      'edf/org/queryAll',
                      '/ba/bankAccount/queryList',
                      '/v1/gl/docManage/query',
                      '/ba/inventory/queryList',
                      '/ba/supplier/queryList',
                      '/account/query',
                      '/customer/queryList',
                      '/v1/ba/person/queryList',
                      '/balancesumrpt/query',
                      '/balanceauxrpt/query',
                      'myip.ipip']

    def save_data(self, request, response, now_time):
        '''存flow数据'''
        try:
            result = JCDFLOWSAVE(now_time=now_time, request=request, response=response, path='',status=False) # 创建对象，即表中一条记录
            session.add(result)     # 对象存入数据库
            session.commit()        # 所有的数据处理准备好之后，执行commit才会提交到数据库
        except Exception as e:
            print(e)
            session.rollback()              # 加入数据库commit提交失败，回滚
            res = pickle.loads(response)    # 从字节对象中读取被封装的对象
            path = './{}.txt'.format(now_time)
            with open(path,'wb') as fw:     # 将数据通过特殊的形式转换为只有python语言认识的字符串，并写入文件
                pickle.dump(res, fw)
            result = JCDFLOWSAVE(now_time=now_time, request=request,path=path,status=False)
            session.add(result)
            session.commit()

    def response(self, flow: mitmproxy.http.HTTPFlow):
        '''拦截响应数据'''
        for l in self.links:
            if '/account/queryCalcUsage' in flow.request.url:  # 解决/account/query、/account/queryCalcUsage 相似问题
                pass
            elif l in flow.request.url:
                request = flow.request
                response = flow.response
                now_time = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())) # 2019_12_25_10_12_10 str
                request = pickle.dumps(request)         # 以字节对象形式返回封装的对象
                response = pickle.dumps(response)
                self.save_data(request, response, now_time)

addons = [Proxy()]
