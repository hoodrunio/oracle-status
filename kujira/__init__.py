import requests
import json


ENDPOINT = "/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED" 

class Validator:
    """
    Class for Kujira Validator.

    Operations related to validators will be implemented under this class
    """
    pass


class Kujira:
    """
    Class for Kujira Node

    validators : dict of Validator objects with address as the key
    """
    def __init__(self, server):
        self.server = server
        self.validators = {}



    def get_validators(self):
        """
        Get details of all validators

        Return
        json response from node
        """
        response = requests.get(f"{self.server}{ENDPOINT}")
        return json.loads(response.text)
