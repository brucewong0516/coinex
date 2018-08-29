import requests
from requests import RequestException
import json
import time
import hashlib


class Coinex_API(object):
    __headers = {
        'Content-Type': 'application/json; charset=latin-1',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
    }

    def __init__(self, headers={}):
        self.access_id = ''
        self.secret_key = ''
        # 在此添加access_id,secret_key
        self.url = 'https://api.coinex.com'
        self.headers = self.__headers
        self.headers.update(headers)

    def get_sign(self, params, secret_key):
        '''
        params: 传递的参数
        secret_key: 密钥
        return 加密后的签名，签名在Trade_API和Account_API中都需要加入到headers中
        '''
        sorted_params_key = sorted(params)
        data = {}
        for item in sorted_params_key:
            data[item] = params[item]
        str_params = requests.get('http://httpbin.org/get', params=data).url.split('http://httpbin.org/get?')[1]
        token = hashlib.md5(str_params.encode('utf-8')).hexdigest().upper()
        return token

    def set_authorization(self, params):
        '''
        params:传递的参数
        return: 返回含有access_id与tonce的字典，即把access_id与tonce添加进传递的参数里(self.headers中已经含有加密后的签名)
        '''
        params['access_id'] = self.access_id
        params['tonce'] = int(time.time()*1000)
        self.headers['AUTHORIZATION'] = self.get_sign(params, self.secret_key)
        return params

    def request(self, url, method, params={}):
        '''
        url:访问的api
        method:可选'get','post','delete'
        params: 传递的参数（不需要填写access_id与tonce两个参数）
        return: 访问成功返回一个json列表，失败返回空字典
        该方法在Trade_API与Account_API中可直接调用，无须再次调用前面的方法
        '''
        postdata = self.set_authorization(params)
        if method == 'get':
            try:
                res = requests.get(url, headers=self.headers, params=postdata)
                requests_data = json.loads(res.text)
                return requests_data
            except RequestException:
                print('Network connection error! Please check your network and your params!')
                return {}
        elif method == 'post':
            try:
                res = requests.post(url, headers=self.headers, params=postdata)
                requests_data = json.loads(res.text)
                return requests_data
            except RequestException:
                print('Network connection error! Please check your network and your params!')
                return {}
        elif method == 'delete':
            try:
                res = requests.delete(url, headers=self.headers, params=postdata)
                requests_data = json.loads(res.text)
                return requests_data
            except RequestException:
                print('Network connection error! Please check your network and your params!')
                return {}

    class Account_API(object):
        # 账户信息api

        def __init__(self):
            self.Inquire_Account_Info_url = 'https://api.coinex.com/v1/balance/info'
            self.Inquire_Withdraw_List_url = 'https://api.coinex.com/v1/balance/coin/withdraw'
            self.Submit_A_Withdrawal_Order_url = 'https://api.coinex.com/v1/balance/coin/withdraw'
            self.Cancel_Withdraw_url = 'https://api.coinex.com/v1/balance/coin/withdraw'

        def Inquire_Account_Info(self):
            '''
            该方法作用是查询账户信息
            return: frozen冻结的货币数量，available可用的货币数量
            '''
            requests_data = Coinex_API().request(self.Inquire_Account_Info_url, 'get')
            return requests_data

        def Inquire_Withdraw_List(self, coin_type=None, coin_withdraw_id=None, page=None, limit=None):
            '''
            该方法的作用是查询提款清单
            coin_type:货币类型
            coin_withdraw_id:货币撤回id
            page:页面，从1开始
            limit:每页金额（1-100）
            return: coin_withdraw_id硬币提取ID
                    creat_time:创造时间
                    amount:提款金额
                    actual_amount:实际提款金额
                    tx_id：提现id
                    coin_address：提款地址
                    tx_free：tx free
                    confirmations：确认
                    coin_type：货币类型
                    status：audit;pass;processing;confirming;not_pass;cancel;finish;fail;
            '''
            params = {}
            params['coin_type'] = coin_type
            params['coin_withdraw_id'] = coin_withdraw_id
            params['page'] = page
            params['limit'] = limit
            requests_data = Coinex_API().request(self.Inquire_Withdraw_List_url, 'get', params)
            return requests_data

        def Submit_A_Withdrawal_Order(self, coin_type, coin_address, actual_amount):
            '''
            该方法的作用是提交提款订单
            coin_type:货币类型
            coin_address:提款地址
            actual_amount:提款实际金额
            return: coin_withdraw_id：货币提取的id
                    create_time：创建时间
                    amount：提款金额
                    actual_amount：实际金额
                    tx_id：提款id
                    coin_address：提款地址
                    tx_free：tx free
                    confirmations：确认
                    coin_type：货币类型
                    status：状态
            '''
            params = {}
            params['coin_type'] = coin_type,
            params['coin_address'] = coin_address
            params['actual_amount'] = actual_amount
            requests_data = Coinex_API().request(self.Submit_A_Withdrawal_Order_url, 'post', params)
            return requests_data

        def Cancel_Withdraw(self, coin_withdraw_id):
            '''
            coin_withdraw_id:提款订单id
            return:
            # Response
            {
                "code": 0,
                "data": {},
                "message": "Ok"
            }
            '''
            params = {}
            params['coin_withdraw_id'] = coin_withdraw_id
            requests_data = Coinex_API().request(self.Cancel_Withdraw_url, 'delete', params)
            return requests_data

    class Trading_API(object):
        # 交易api

        def __init__(self):
            self.Place_Limit_Order_url = 'https://api.coinex.com/v1/order/limit'
            self.Place_Market_Order_url = 'https://api.coinex.com/v1/order/market'
            self.Place_IOC_Order_url = 'https：//api.coinex.com/v1/order/ioc'
            self.Acquire_Unexecuted_Order_List_url = 'https：//api.coinex.com/v1/order/pending'
            self.Acquire_Executed_Order_List_url = 'https://api.coinex.com/v1/order/finished'
            self.Acquire_Order_Status_url = 'https://api.coinex.com/v1/order/status'
            self.Acquire_Executed_Order_Detail_url = 'https://api.coinex.com/v1/order/deals'
            self.Acquire_User_deals_url = 'https://api.coinex.com/v1/order/user/deals'
            self.Cancel_Order_url = 'https://api.coinex.com/v1/order/pending'
            self.Mining_Difficulty_url = 'https://api.coinex.com/v1/order/mining/difficulty'

        def Place_Limit_Order(self, market, type, amount, price, source_id = None):
            '''
            该方法的作用是限价单
            market: 交易市场名称
            type:可选参数'sell','buy'
            amount:订单金额
            price:订单数量
            source_id:？？？
            return: amount：订单数量
                    avg_price：平均价格
                    create_time：订单创建时间
                    deal_amount：计数
                    deal_fee：手续费
                    deal_money：？？？
                    finished_time：订单完成时间
                    id：订单号
                    maker_fee_rate：交易费率
                    market：市场
                    order_type：订单类型（limit:limit order;market:market order）
                    price：订单价格
                    status：状态 （not_deal: 未执行 part_deal:部分执行 done：已执行）
                    taker_fee_rate：接受费
                    type：类型 （sell, buy）
            '''
            params = {}
            params['market'] = market
            params['type'] = type
            params['amount'] = amount
            params['price'] = price
            params['source_id'] = source_id
            requests_data = Coinex_API().request(self.Place_Limit_Order_url, 'post', params)
            return requests_data

        def Place_Market_Order(self, market, type, amount):
            '''
            该方法的作用是市场订单
            market: 交易市场名称
            type:可选参数'sell','buy'
            amount:订单金额
            return: amount：订单数量
                    avg_price：平均价格
                    create_time：订单创建时间
                    deal_amount：计数
                    deal_fee：手续费
                    deal_money：？？？
                    finished_time：订单完成时间
                    id：订单号
                    maker_fee_rate：交易费率
                    market：市场
                    order_type：订单类型（limit:limit order;market:market order）
                    price：订单价格
                    status：状态 （not_deal: 未执行 part_deal:部分执行 done：已执行）
                    taker_fee_rate：接受费
                    type：类型 （sell, buy）

            '''
            params = {}
            params['market'] = market
            params['type'] = type
            params['amount'] = amount#
            requests_data = Coinex_API().request(self.Place_Market_Order_url, 'post', params)
            return requests_data

        def Place_IOC_Order(self, market, type, amount, price, source_id=None):
            '''
            立即或取消订单
            market: 市场
            type:类型
            amount:订单金额
            price:价钱
            source_id:？？？
            return:amount：订单数量
                    avg_price：平均价格
                    create_time：订单创建时间
                    deal_amount：计数
                    deal_fee：手续费
                    deal_money：？？？
                    finished_time：订单完成时间
                    id：订单号
                    maker_fee_rate：交易费率
                    market：市场
                    order_type：订单类型（limit:limit order;market:market order）
                    price：订单价格
                    status：状态 （not_deal: 未执行 part_deal:部分执行 done：已执行）
                    taker_fee_rate：接受费
                    type：类型 （sell, buy）

            '''
            params = {}
            params['market'] = market
            params['type'] = type
            params['amount'] = amount
            params['price'] = price
            params['source_id'] = source_id
            requests_data = Coinex_API().request(self.Place_IOC_Order_url, 'post', params)
            return requests_data

        def Acquire_Unexecuted_Order_List(self, market, page, limit):
            '''
            获取未执行的订单列表
            market:市场
            page:页面
            limit:限制
            return：
            # Response
            {
                "code": 0,
                "data": {
                    "count": 1,  # current page rows
                    "curr_page": 1,  # current page
                    "data": [  # return in reverse of order time with latest order on top
                        {
                            "amount": "1.00",  # 订单数目
                            "avg_price": "0.00",  # 平均订单价格
                            "create_time": 1494320533,  # 创建时间
                            "deal_amount": "0.001",  # 交易数目
                            "deal_fee": "130.3792",  # 手续费
                            "deal_money": "65189.6",  # 执行价值
                            "id": 32,  # 订单number.
                            "left": 32,  # 未执行数目
                            "maker_fee_rate": "0",  # ？？？
                            "market": "BTCBCH",  # 市场
                            "order_type": "limit",  # 订单类型
                            "price": "10.00",  # 订单价格
                            "status": "not_deal",  # 订单的状态
                            "taker_fee_rate": "0.002",  # 费率
                            "type": "sell"  # buy/sell 类型
                        }
                    ],
                    "has_next": true  # Is there a next page
                },
                "message": "Ok"
            }
            '''
            params = {}
            params['market'] = market
            params['page'] = page
            params['limit'] = limit
            requests_data = Coinex_API().request(self.Acquire_Unexecuted_Order_List_url, 'post', params)
            return requests_data

        def Acquire_Executed_Order_List(self, market, page, limit):
            '''
            获取已执行订单
            market:市场
            page: 页
            limit: 限制
            return：与上个方法相同
            '''
            params = {}
            params['market'] = market
            params['page'] = page
            params['limit'] = limit
            requests_data = Coinex_API().request(self.Acquire_Executed_Order_List_url, 'get', params)
            return requests_data

        def Acquire_Order_Status(self, id, market):
            '''
            获取订单的状态
            id:订单号
            market: 市场
            return:
            # Response
            {
                "code": 0,
                "data": {  # order data
                    "amount": "1000",  # 订单数量
                    "avg_price": "11782.28",  # 平均价格
                    "create_time": 1496761108,  # 订单创建时间
                    "deal_amount": "1000",  # 执行数目
                    "deal_fee": "23564.5798468",  # 手续费
                    "deal_money": "11782289.9234",  # 执行价值
                    "id": 300021,  # 订单号
                    "left": "9.4",  # 未执行量
                    "maker_fee_rate": "0.001",  # 费率
                    "market": "BTCBCH",  # 市场
                    "order_type": "limit",  # 订单类型
                    "price": "7000",  # 订单价格
                    "status": "done",  # 状态
                    "taker_fee_rate": "0.002",  # 费率
                    "type": "sell"  # 类型
                }
            },
            "message": "Ok"
            }
           '''
            params = {}
            params['market'] = market
            params['id'] = id
            requests_data = Coinex_API().request(self.Acquire_Order_Status_url, 'get', params)
            return requests_data

        def Acquire_Executed_Order_Detail(self, id, page, limit):
            '''
            获取已执行订单明细
            id: 订单号
            page:页面
            limit: 每页金额
            return:
            # Response
            {
                "code": 0,
                "data": {
                    "count": 1,
                    "curr_page": 1,
                    "data": [
                        {
                            "amount": "0.622",  # 执行金额
                            "create_time": 1496799439,  # 执行时间
                            "deal_money": "7240.6398",  # 执行价值
                            "fee": "0.008196",  # 手续费
                            "fee_asset": "CET",  # 交易费资产
                            "id": 1012977,  # 执行id
                            "order_id": 4955055,  # 订单号.
                            "price": "10.9",  # 订单价格
                            "role": "taker"  # 订单角色
                            "type": "sell"  # 订单类型
            }
            ],
            "has_next": true
            },
            "message": "Ok"
            }
            '''
            params = {}
            params['page'] = page
            params['id'] = id
            params['limit'] = limit
            requests_data = Coinex_API().request(self.Acquire_Executed_Order_Detail_url, 'get', params)
            return requests_data

        def Acquire_User_deals(self, market, page, limit):
            '''
            获取用户交易
            market:市场
            page:页面
            limit:每页金额
            return:
            # Response
            {
                "code": 0,
                "data": {
                    "count": 1,
                    "curr_page": 1,
                    "data": [
                        {
                            "amount": "0.622",  # 执行数目
                            "create_time": 1496799439,  # 执行时间
                            "deal_money": "7240.6398",  # 执行价值
                            "fee": "0.008196",  # 手续费
                            "fee_asset": "CET",  # 手续费资产
                            "id": 1012977,  # 执行id
                            "order_id": 12977,  # 订单号
                            "price": "10.9",  # 订单价格
                            "role": "taker"  # 订单角色
                            "type": "sell"  # 订单类型
            }
            ],
            "has_next": true
            },
            "message": "Ok"
            }
            '''
            params = {}
            params['page'] = page
            params['market'] = market
            params['limit'] = limit
            requests_data = Coinex_API().request(self.Acquire_User_deals_url, 'get', params)
            return requests_data

        def Cancel_Order(self, id, market):
            '''
            取消订单
            id:未执行的订单号
            market:市场
            return:
            # Response
            {
                "code": 0,
                "data": {
                    "amount": "56.5",  # 订单数
                    "avg_price": "11641.3",  # 平均价格
                    "create_time": 1496798479,  # 订单时间
                    "deal_amount": "56.5",  # 执行数目
                    "deal_fee": "1315.4669122",  # 手续费
                    "deal_money": "657733.4561",  # 执行价值
                    "id": 300032,  # 订单号.
                    "left": "0",  # 未执行数目
                    "maker_fee_rate": "0.001",  # ？？？
                    "market": "BTCBCH",  # 市场
                    "order_type": "limit",  # 订单类型: limit:limit order;market:market order;
                    "price": "10",  # 订单价格
                    "source_id": "123",  # 用户定义的数字？.
                    "status": "done",  # 订单状态: done:executed;part_deal:partly executed;not_deal:unexecuted;
                    "taker_fee_rate": "0.002",  # 费率
                    "type": "sell"  # 订单类型: sell:sell;buy:buy;
                },
                "message": "Ok"
            }
            '''
            params = {}
            params['id'] = id
            params['market'] = market
            requests_data = Coinex_API().request(self.Cancel_Order_url, 'delete', params)
            return requests_data

        def Mining_Difficulty(self):
            '''
            挖矿难度
            return：
            # Response
            {
                "code": 0,
                "data": {
                    "difficulty": "50000",
                    "prediction": "0",
                    "update_time": 1530629026
                },
                "message": "Ok"
            }
            '''
            requests_data = Coinex_API().request(self.Mining_Difficulty_url, 'get')
            return requests_data

    class Market_API(object):
        # 市场api

        def __init__(self):
            self.Acquire_Market_List_url = 'https://api.coinex.com/v1/market/list'
            self.Acquire_Market_Statistics_url = ' https://api.coinex.com/v1/market/ticker'
            self.Acquire_Market_Depth_url = 'https://api.coinex.com/v1/market/depth'
            self.Acquire_Latest_Transaction_Data_url = 'https://api.coinex.com/v1/market/deals'
            self.Acquire_KLine_Data_url = 'https://api.coinex.com/v1/market/kline'
            self.headers = Coinex_API().headers

        def Acquire_Market_List(self):
            '''
            获取市场列表
            '''
            res = requests.get(self.Acquire_Market_List_url, headers=self.headers)
            requests_data = json.loads(res.text)
            return requests_data

        def Acquire_One_Market_Statistics(self, market):
            '''
            获取市场统计数据
            market: 市场名称
            return:
            # Response
            {
                "code": 0,
                "data": {
                    "date": 1494310546,  # 返回时的服务器时间
                    "ticker": {
                        "buy": "10.00",  # 买 1
                        "buy_amount": "10.00",  # buy 1 amount
                        "open": "10",  # 开盘价
                        "high": "10",  # 最高价
                        "last": "10.00",  # 最新价
                        "low": "10",  # 最低价
                        "sell": "10.00",  # 卖1
                        "sell_amount": "0.78",  # sell 1 amount
                        "vol": "110"  # 24小时交易量
                    }
                },
                "message": "Ok"
            }
            '''
            params = {}
            params['market'] = market
            res = requests.get(self.Acquire_Market_Statistics_url, headers=self.headers, params=params)
            requests_data = json.loads(res.text)
            return requests_data

        def Acquire_All_Market_Statistics(self):
            '''
            return:同上
            '''
            res = requests.get(self.Acquire_Market_Statistics_url+'/all', headers=self.headers)
            requests_data = json.loads(res.text)
            return requests_data

        def Acquire_Market_Depth(self, market, merge, limit=5):
            '''
            获得市场买入卖出统计数据，最多返回20
            market:市场
            merge:合并（可选，'0'，'0.1'，'0.01'，'0.001'，'0.0001'，'0.00001'，'0.000001'，'0.0000001'，'0.00000001）
            limit:可选范围：5/10/20
            return:
            # Response
            {
                "code": 0,
                "data": {
                    "last": "10.00",
                    "asks": [  # 卖家深度
                        [
                            "10.00",  # 订单价格
                            "0.9999"  # 订单金额
                        ]
                    ],
                    "bids": [  # 买家深度
                        [
                            "10.00",  # 订单价格
                            "1.0000"  # 订单金额
                        ]
                    ]
                },
                "message": "Ok"
            }
            '''
            params = {}
            params['market'] = market
            params['merge'] = merge
            params['limit'] = limit
            res = requests.get(self.Acquire_Market_Depth_url, headers=self.headers, params=params)
            requests_data = json.loads(res.text)
            return requests_data

        def Acquire_Latest_Transaction_Data(self, market, last_id=0):
            '''
            获取最新交易数据，最多返回1000
            market:市场
            last_id:交易历史ID，发送0从最新记录中提取
            return:
            # Response
            {
                "code": 0,
                "data": [
                    {
                        "amount": "0.0001",  # 交易数目
                        "date": 1494214689,  # 交易时间
                        "date_ms": 1494214689067,  # 交易时间（毫秒）
                        "id": 5,  # 交易号
                        "price": "10.00",  # 交易价格
                        "type": "buy"  # 交易类型: buy, sell
                    }
                ],
                "message": "Ok"
            }
            '''
            params = {}
            params['market'] = market
            params['last_id'] = last_id
            res = requests.get(self.Acquire_Latest_Transaction_Data_url, headers=self.headers, params=params)
            requests_data = json.loads(res.text)
            return requests_data

        def Acquire_KLine_Data(self, market, type, limit=None):
            '''
            获取K线数据
            market: 市场
            type: 类型（1min;3min;5min;15min;30min;1hour;2hour;4hour;6hour;12hour;1day;3day;1week）
            limit: 限制
            return:
            # Response
            {
                "code": 0,
                "data": [
                    [
                        1492358400,  # 时间
                        "10.0",  # 开盘价
                        "10.0",  # 收盘价
                        "10.0",  # 最高价
                        "10.0",  # 最低价
                        "10",  # 交易量
                        "100",  # 数量
                        "BCHUSDT",  # 市场
                    ]
                ],
                "message": "Ok"
            }
            '''
            params = {}
            params['market'] = market
            params['type'] = type
            params['limit'] = limit
            res = requests.get(self.Acquire_KLine_Data_url, headers=self.headers, params=params)
            requests_data = json.loads(res.text)
            return requests_data
if __name__ == '__main__':
    Access_ID=''
    Secret_Key=''
    