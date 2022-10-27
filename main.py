from kujira import Kujira
from pprint import pprint

SERVER = "https://lcd.kaiyo.kujira.setten.io"

mykujira = Kujira(SERVER)

#mykujira.list_validators()
mykujira.get_missing_block_numbers()
mykujira.list_missing()
