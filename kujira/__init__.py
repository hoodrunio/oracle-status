import requests
import json
from datetime import datetime
from threading import Thread
import threading
import traceback as tb

ENDPOINT = "/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED"


class TimeSeries:
    def __init__(self, serie_name,  maxitems):
        """
        Store at most maxitem values. Only add value if it is different
        then previous one

        TODO: add earliest value deletion if number of values is larger
        then maxitem
        """
        self.name = serie_name
        self.values = {}
        self.maxitems = maxitems

    def add_value(self, dateval, value):
        numitems = len(self.values.keys())
        if numitems > 0:
            if numitems == self.maxitem:
                firstkey = sorted(self.values.keys())[0]
                del self.values[firstkey]
            lastval = self.values[-1]
            if value != lastval:
                self.values[dateval] = value
        else:
            self.values[dateval] = value

    def first(self):
        try:
            firstkey = sorted(self.values.keys())[0]
            return self.values[firstkey]
        except KeyError:
            return 0

    def latest(self):
        try:
            lastkey = sorted(self.values.keys())[-1]
            return self.values[lastkey]
        except KeyError:
            return 0
        

class Commission:
    def __init__(self, jsonstr):
        """
        Class for commission rates

        input: commission part of validator json string
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
        self.active = True
        self.validators = {}
        self.get_validators()

    def get_validators(self):
        """
        Get details of all validators
        """
        try:
            response = requests.get(f"{self.server}{ENDPOINT}")
            temp = json.loads(response.text)
            for validator in temp["validators"]:
                temp_validator = Validator(validator)
                temp_addr = temp_validator.operator_address
                if temp_addr not in self.validators.keys():
                    self.validators[temp_addr] = temp_validator
            self.active = True
        except:
            self.active = False
            
    def list_validators(self):
        for validator in self.validators.values():
            print(validator)

    def list_missing(self):
        for validator in self.validators.values():
            print(validator.operator_address,
                  validator.missing_blocks.latest())

    def get_missing_block_numbers(self):
        SOURCE = self.server

        def worker(address):
            url = f"{SOURCE}/oracle/validators/{address}/miss"
            result = json.loads(requests.get(url).text)
            missing = int(result["miss_counter"])
            self.validators[address].add_missing_block_value(missing)

        import time
        for address in self.validators.keys():
            t = Thread(target=worker, args=(address,))
            t.start()
            time.sleep(0.01)

        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

class KujiraPool:
    """
    Pool of kujira nodes.
    """
    def __init__(self):
        self.nodes = {}
        self.selected = None
                
    def add_nodes_from_file(self, filename):
        nodenames = open(filename, "r").readlines()
        
        
    def add_node(self, node_url):
        firstnode = False
        if self.selected == None:
            firstnode = True
            
        if node_url not in self.nodes.keys():
            newnode = Kujira(node_url)
            self.nodes[node_url] = newnode

        if firstnode is True:
            self.selected = self.nodes[node_url]
            self.selected.get_validators()
        

    def get_missing_block_numbers(self):
        #TODO: check servers in intervals for their health.
        if self.selected.active:
            self.selected.get_missing_block_numbers()            
        else:
            active_found = False
            for node in self.nodes.values():
                if node.active is True:
                    self.selected = node
                    active_found = True
                    break
            if active_found == False:
                for node in self.nodes.values():
                    node.get_validators()
                    if node.active is True:
                        self.selected = node
                        break
            self.selected.get_missing_block_numbers()

            
class MissingRecord:
    def __init__(self, moniker, addr, alarmcount):
        self.moniker = moniker
        self.address = addr
        self.alarmcount = alarmcount
        self.firstnumber = None
        self.lasttime = None

    def update(self, missing):
        if self.firstnumber is None:
            self.firstnumber = missing
        else:
            if missing - self.firstnumber > self.alarmcount:
                self.firstnumber = missing
                return "ALARM"
            else:
                return None


class Validators:
    def __init__(self):
        self.validators = {}
        pass    
