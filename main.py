from kujira import Kujira, KujiraPool, session, User, Missing, initialize
from config import *

import time

#initialize()
pool = KujiraPool()

for node_url in SERVERS:
    pool.add_node(node_url)

pool.update_selected()

while 1:
    pool.get_missing_block_numbers()
    time.sleep(5)
#pool.update_selected()
#pool.add_validator("discord1", "kujiravaloper1qvq39e9mjaqner30swwrq6vf59huyxetrqagjy", 10)

"""

#initialize()

k = Kujira("https://lcd.kaiyo.kujira.setten.io")
k.check()
validators = Validators()

validators.add_validator("ilkermanap#7075", "denemeaddres", "denememoniker", 20)
"""
