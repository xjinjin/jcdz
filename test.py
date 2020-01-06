
import mitmproxy.addonmanager
import mitmproxy.connections
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
import mitmproxy.proxy.protocol

null = ''
true = ''
false = ''
class Events:

    def __init__(self):
        self.links = {'login': 'portal/initPortal',
                      'qyxx': 'edf/org/queryAll', 'zhanghu': '/ba/bankAccount/queryList',
                      'pingzheng': '/v1/gl/docManage/init', 'cunhuo': '/ba/inventory/queryList',
                      'gongyinshang': '/ba/supplier/queryList', 'kjkm': '/account/query', 'kehu': '/customer/queryList',
                      'bmry': '/v1/ba/person/queryList', 'yeb': '/balancesumrpt/query', 'myip': 'myip.ipip'}

        self.task = {'1': '凭证','2': '余额表','3': '企业信息','4': '会计科目','5': '部门人员','6': '客户'
            ,'7': '供应商','8': '项目','9': '存货及服务','10': '账户'}

    def request(self, flow: mitmproxy.http.HTTPFlow):
        """
            The full HTTP request has been read.
        """

    def response(self, flow: mitmproxy.http.HTTPFlow):
        """
            The full HTTP response has been read.
        """

        if '/balancesumrpt/query' in flow.request.url:
            print('####################################')
            data = eval(flow.response.text)['value']
            print(data)
            print(type(eval(flow.response.text)))
            print(type(data))


            print('####################################')


addons = [Events()]
