import requests
import json
import asyncio
import time 
import aiohttp
from aiohttp.client import ClientSession
from datetime import datetime
from threading import Thread
import threading

ENDPOINT = "/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED" 


class TimeSeries:
    def __init__(self, serie_name,  maxnum):
        """
        Store at most maxnum values. Only add value if it is different then previous one

        TODO: add earliest value deletion if number of values is larger then maxnum
        """
        self.name = serie_name
        self.values = {}

    def add_value(self, dateval, value):
        if len(self.values.keys()) > 0:
            lastval = self.values[-1]
            if value != lastval:
                self.values[dateval] = value
        else:
            self.values[dateval] = value
                
    def latest(self):
        try:
            lastkey = sorted(self.values.keys()) [-1]
            return self.values[lastkey]
        except:
            return 0
    
class Commission:
    def __init__(self, jsonstr):
        """
        Class for commission rates

        input: commission part of validator json string

        'commission': {
        'commission_rates': {
            'max_change_rate': '0.010000000000000000',                                                                                          
            'max_rate': '0.100000000000000000',
            'rate': '0.050000000000000000'},                                                                                           
        'update_time': '2022-07-01T12:00:00Z'},     
        """
        
        self.update_time = jsonstr["update_time"]
        rates = jsonstr["commission_rates"]
        self.max_change_rate = float(rates["max_change_rate"])
        self.max_rate = float(rates["max_rate"])
        self.rate = float(rates["rate"])

        
class Description:
    def __init__(self, jsonstr):
        self.details = jsonstr["details"]
        self.identity = jsonstr["identity"]
        self.moniker = jsonstr["moniker"]
        self.security_contact = jsonstr["security_contact"]
        self.website = jsonstr["website"]
        
    
class Validator:
    """
    Class for Kujira Validator.

    Operations related to validators will be implemented under this class
    

    {'commission': {'commission_rates': {'max_change_rate': '0.010000000000000000',
                                                     'max_rate': '0.100000000000000000',
                                                     'rate': '0.050000000000000000'},
                                'update_time': '2022-07-01T12:00:00Z'},
                 'consensus_pubkey': {'@type': '/cosmos.crypto.ed25519.PubKey',
                                      'key': 'kL4NF3pkhS7NUvQfSrdNAokFUnds7sbL611go5G9eh8='},
                 'delegator_shares': '610061638794.000000000000000000',
                 'description': {'details': 'We are operating a highly secure, '
                                            'stable Validator Node for Kujira '
                                            'and 5 other mainnet chains. We '
                                            'created Cross chain bridge App '
                                            'www.CosmosBridge.app for '
                                            'Community. We post tech tutorials '
                                            'on our Youtube channel. We are '
                                            'operating multiple IBC Relayers. '
                                            'All info on our website.',
                                 'identity': 'AF9D7EF7CC70CE24',
                                 'moniker': 'Synergy Nodes',
                                 'security_contact': '',
                                 'website': 'https://www.synergynodes.com'},
                 'jailed': False,
                 'min_self_delegation': '1',
                 'operator_address': 'kujiravaloper1lcgzkqstk4jjtphfdfjpw9dd9yfczyzmcyxvj9',
                 'status': 'BOND_STATUS_BONDED',
                 'tokens': '610061638794',
                 'unbonding_height': '0',
                 'unbonding_time': '1970-01-01T00:00:00Z'}


    """
    def __init__(self, jsonstr):
        temp_comm = jsonstr["commission"]
        self.commission = Commission(temp_comm)
        self.consensus_pubkey = jsonstr["consensus_pubkey"]
        self.delegator_shares = jsonstr["delegator_shares"]
        self.jailed = jsonstr["jailed"]
        self.min_self_delegation = jsonstr["min_self_delegation"]
        self.operator_address = jsonstr["operator_address"]
        self.status = jsonstr["status"]
        self.tokens = jsonstr["tokens"]
        self.unbonding_height = jsonstr["unbonding_height"]
        self.unbonding_time = jsonstr["unbonding_time"]
        self.description = Description(jsonstr["description"]) 
        self.missing_blocks = TimeSeries("Missing Blocks", 120)
        
        
    def __str__(self):
        return f"{self.description.moniker} {self.operator_address}"

    def add_missing_block_value(self, value):
        self.missing_blocks.add_value(datetime.now(), value)


class Kujira:
    """
    Class for Kujira Node

    validators : dict of Validator objects with address as the key
    """
    def __init__(self, server):
        self.server = server
        self.validators = {}
        self.get_validators()

    def get_validators(self):
        """
        Get details of all validators
        """
        response = requests.get(f"{self.server}{ENDPOINT}")
        temp = json.loads(response.text)
        for validator in temp["validators"]:
            temp_validator = Validator(validator)
            if temp_validator.operator_address not in self.validators.keys():
                self.validators[temp_validator.operator_address] = temp_validator

    def list_validators(self):
        for validator in self.validators.values():
            print(validator)

    def list_missing(self):
        for validator in self.validators.values():
            print(validator.operator_address, validator.missing_blocks.latest())
            
    def get_missing_block_numbers(self):
        SOURCE = self.server


        """
        async not worked


        async def download_link(url:str, session:ClientSession):
            addr = url.split("/")[-2]
            print(addr)
            async with session.get(url) as response:
                result = await response.text()
                r = json.loads(result)
                missing = int(r["miss_counter"])
                self.validators[addr].add_missing_block_value(missing)

        async def download_all(urls:list):
            my_conn = aiohttp.TCPConnector(limit=10)
            async with aiohttp.ClientSession(connector=my_conn) as session:
                tasks = []
                for url in urls:
                    task = asyncio.ensure_future(download_link(url=url, session=session))
                    tasks.append(task)
                await asyncio.gather(*tasks,return_exceptions=True) # the await must be nest inside of the session
                
        temp = []
        
        for address in self.validators.keys():
            temp.append(f"{SOURCE}/oracle/validators/{address}/miss")
            
        asyncio.run(download_all(temp))
        """
        def worker(address):
            result = json.loads(requests.get(f"{SOURCE}/oracle/validators/{address}/miss").text)
            missing = int(result["miss_counter"])
            self.validators[address].add_missing_block_value(missing)

        
        for address in self.validators.keys():
            t = Thread(target=worker, args=(address,))
            t.start()
            
        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()
            
        
    

