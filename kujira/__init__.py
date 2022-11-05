import requests
import json
from threading import Thread
import threading
import traceback as tb
from .models import User, Missing, session, initialize
import sqlalchemy
import time
import random

ENDPOINT = "/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED"


class Validators:
    def __init__(self):
        self.validators = session.query(User).all()

    def add_validator(self, discordname, address, moniker, alarm_threshold):
        try:
            user = User(discordname=discordname,
                        address=address,
                        moniker=moniker,
                        alarm_threshold=alarm_threshold)
            session.add(user)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
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

    def check_nodes(self):
        """
        calls check method on all available nodes.
        """
        def worker(nodeobject):
            nodeobject.check()

        for node in self.nodes.values():
            t = Thread(target=worker, args=(node,))
            t.start()
            time.sleep(0.01)

        main_thread =threading.currentThread()
        for t in threading.enumerate():
            if t is not main_thread:
                t.join()

    def add_nodes_from_file(self, filename):
        for node in open(filename, "r").readlines():
            self.add_node(node.strip())

    def add_node(self, node_url):
        if node_url not in self.nodes.keys():
            newnode = Kujira(node_url)
            self.nodes[node_url] = newnode

    def get_missing_block_numbers(self):
        """
        check all kujira nodes and select the active ones.

        randomly select one of the active ones and ask for
        missing numbers for addresses in the database.
        """
        self.check_nodes()

        active_nodes = [node for node in self.nodes.values() if node.active == True]

        selected = random.choice(active_nodes)
        return selected.get_missing_block_numbers(self.validators.address_list())
