from kujira import Kujira, KujiraPool

from config import *

pool = KujiraPool()

for node_url in SERVERS:
    pool.add_node(node_url)

print(pool.selected.server)
pool.get_missing_block_numbers()


pool.selected.list_missing()
print(pool.selected.server)
