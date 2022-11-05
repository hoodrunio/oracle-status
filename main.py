from kujira import Kujira, KujiraPool, session, User, Missing, initialize

from config import *


pool = KujiraPool()

for node_url in SERVERS:
    pool.add_node(node_url)

pool.get_missing_block_numbers()




"""

#initialize()

k = Kujira("https://lcd.kaiyo.kujira.setten.io")
k.check()
validators = Validators()

validators.add_validator("ilkermanap#7075", "denemeaddres", "denememoniker", 20)
"""