from kujira import Kujira

SERVER = "https://lcd.kaiyo.kujira.setten.io"

mykujira = Kujira(SERVER)

mykujira.get_missing_block_numbers()
mykujira.list_missing()
