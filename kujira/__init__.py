import requests
import json
from threading import Thread
import threading
import traceback as tb
from .models import User, Missing, session, initialize
import sqlalchemy
from sqlalchemy import exc as sqlalchemy_exceptions
import time
import random

ENDPOINT = "/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED"


class Validators:
    def __init__(self):
        print("Querying validators")
        self.validators = session.query(User).all()
        print(len(self.validators))

    def get_validator(self, address):
        return session.query(User).filter_by(address=address).first()

    def add_validator(self, address, moniker, alarm_threshold):
        try:
            user = User(address=address,
                        moniker=moniker,
                        alarm_threshold=alarm_threshold)
            session.add(user)
            session.commit()
        except sqlalchemy_exceptions.IntegrityError:
            print(f"address {address} is already in db")

    def refresh(self):
        self.validators = session.query(User).all()

    def address_list(self):
        return [validator.address for validator in self.validators]


class Kujira:
    """
    Class for Kujira Node

    validators : dict of Validator objects with address as the key
    """

    def __init__(self, server):
        self.server = server
        self.active = True

    def check(self):
        try:
            url = f"{self.server}{ENDPOINT}"
            result = requests.get(self.server).text
            self.active = True
        except requests.exceptions.ConnectionError:
            self.active = False

    def validator(self, address):
        url = f"{self.server}/cosmos/staking/v1beta1/validators/{address}"
        output = requests.get(url).text
        result = json.loads(output)

        if "code" in result.keys():
            return False, None
        else:
            return True, ValidatorJSON(result["validator"])

    def get_missing_block_numbers(self, list_of_addresses):
        try:
            temp = {}

            def worker(address):
                url = f"{self.server}/oracle/validators/{address}/miss"
                output = requests.get(url).text
                result = json.loads(output)
                if "miss_counter" in result.keys():
                    missing = int(result["miss_counter"])
                    temp[address] = missing

            for address in list_of_addresses:
                t = Thread(target=worker, args=(address,))
                t.start()
                time.sleep(0.01)

            main_thread = threading.currentThread()
            for t in threading.enumerate():
                if t is not main_thread:
                    t.join()
            return temp
        except:
            self.active = False
            return None


class KujiraPool:
    """
    Pool of kujira nodes.
    """

    def __init__(self):
        self.nodes = {}
        self.validators = Validators()
        self.selected = None

    def add_validator(self, discord_name, address, threshold):
        temp = self.validators.get_validator(address)
        print(temp)
        msg = ""
        if temp is None:
            state, validator = self.selected.validator(address)
            if state is True:
                self.validators.add_validator(address, validator.moniker, threshold)
                msg = f"Validator alarm for address {address} and moniker {validator.moniker} set with threshold {threshold} to user {discord_name}"
            else:
                msg = f"Couldn't find validator record for address {address}"
        else:
            msg = f"There is already a record for {address}"
            return msg
        return msg

    def get_validator(self, address):
        if self.selected is None:
            if len(self.nodes) > 0:
                self.update_selected()
            else:
                print("no nodes in pool")
        else:
            state, validator = self.selected.validator(address)
            if state is True:
                return validator
        return False

    def update_selected(self):
        """
        check all kujira nodes and select the active ones.

        randomly select one of the active ones and ask for
        missing numbers for addresses in the database.
        """
        self.check_nodes()
        active_nodes = [node
                        for node in self.nodes.values()
                        if node.active is True
                        ]
        self.selected = random.choice(active_nodes)

    def check_nodes(self):
        """
        calls check method on all available nodes. Broken nodes
        will be marked as active=False
        """
        def worker(nodeobject):
            nodeobject.check()

        if len(self.nodes) > 0:
            for node in self.nodes.values():
                t = Thread(target=worker, args=(node,))
                t.start()
                time.sleep(0.01)

            main_thread = threading.currentThread()
            for t in threading.enumerate():
                if t is not main_thread:
                    t.join()
        else:
            raise "No nodes added"

    def add_nodes_from_file(self, filename):
        for node in open(filename, "r").readlines():
            self.add_node(node.strip())

    def add_node(self, node_url):
        if node_url not in self.nodes.keys():
            new_node = Kujira(node_url)
            self.nodes[node_url] = new_node

    def get_missing_block_numbers(self):
        numbers = {}
        try:
            numbers = self.selected.get_missing_block_numbers(self.validators.address_list())
        except:
            self.update_selected()
            numbers = self.selected.get_missing_block_numbers(self.validators.address_list())
        return numbers


class ValidatorJSON:
    def __init__(self, jsonstr):
        self.jailed = jsonstr["jailed"]
        self.operator_address = jsonstr["operator_address"]
        desc = jsonstr["description"]
        self.details = desc["details"]
        self.identity = desc["identity"]
        self.moniker = desc["moniker"]
        self.security_contact = desc["security_contact"]
        self.website = desc["website"]
