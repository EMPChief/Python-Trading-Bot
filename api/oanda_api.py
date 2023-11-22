import requests
import constants.defs as defs

class OandaApi:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {defs.API_KEY}'
        })
    
    def make_request(self, url, verb='get', code=200, params=None, data=None, headers=None):
        full_url = f'{defs.OANDA_URL}{url}'
        try:
            response = None
            if verb == 'get':
                response = self.session.get(self, url, params=params, data=data, headers=headers)
            if response == None:
                return False, {'error': 'verb not found'}
            if response.status_code == code:
                return True, response.json()
            else:
                return False, response.json()
        except Exception as e:
            return False, {'error': e}
        
    def get_account_ep(self, ep, data_key):
        url = f"accounts/{defs.ACCOUNT_ID}/{ep}"
        ok, data = self.make_request(url);
        if ok == True and data_key in data:
            return data[data_key]
        
        else:
            print("ERROR get_account_ep", data)
            None
        
    def get_account_summary(self):
        return self.get_account_ep("summary", "account")
    
    def get_instruments(self):
        return self.get_account_ep("instruments", "instruments")