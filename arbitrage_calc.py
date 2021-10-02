import os
import sys
import json
import time 
import urllib3
import sqlite3
from itertools import combinations

db = sqlite3.connect("arbitrage.db")
cr = db.cursor()
http_manager = urllib3.PoolManager()


class ConsoleColor:
	OKBLUE = '\033[94m'
	ENDC = '\033[0m'


def getinput(msg):
	try:
		inp = input(msg)
		return inp
	except KeyboardInterrupt:
		sys.exit()


def is_number(a):
	try:
		b = float(a)
		return True
	except:
		return False


def split_price(price):
	p = str(price)
	i = 3
	while(i < len(p)):
		p = p[:-i] + ',' + p[-i:]
		i += 4
	return p


def interest_rates(buy, sell):
	return abs(round(float((int(buy) - int(sell)) / int(sell) * 100.0), 2))


def check_tbls():
	"this function checks if required tables exist, if not create them"
	global db
	global cr

	# the value column is intentionally considered as TEXT for futher adding settings
	create_settings_qry = """
		BEGIN TRANSACTION;

		CREATE TABLE IF NOT EXISTS settings (
		   id INTEGER PRIMARY KEY,
		   keyname TEXT NOT NULL,
		   value TEXT NULL,
		   UNIQUE(keyname)
		);

		INSERT OR IGNORE INTO settings (keyname, value) VALUES
			("INTERVAL", "5"),
			("INTEREST", "0.1");

		COMMIT;
	"""

	cr.executescript(create_settings_qry)


def get_key(keyname):
	global cr
	cr.execute("SELECT * FROM settings WHERE keyname='{0}'".format(keyname))
	return cr.fetchone()[2]


def set_key(keyname, value):
	global db
	global cr
	cr.execute("UPDATE settings SET value='{0}' WHERE keyname='{1}'".format(value, keyname))
	db.commit()


def get_crypto_data():
	"this fetches data from our server"
	response = http_manager.request('GET', 'https://fullnode.ir/fee')
	if(response.status == 200):
		return json.loads(response.data)


def show_arbitrage(crypto_name, exchange_a, exchange_b):
	print(""" 
	Crypto Name: {10}{0}{11}
	Buy From {10}{1}{11} with price {10}{2}{11}
	Sell To {10}{3}{11}  with price {10}{4}{11}
	Interest %: {10}{5}{11}
	Interest Amount: {10}{6}{11}
	Buy Vol.  : {10}{7}{11}
	Sell Vol. : {10}{8}{11}
	Arbitrage Vol. : {10}{9}{11} 
			""".format(
					crypto_name, 
					exchange_a["exchange_lable"],
					split_price(exchange_a["buy"]["price"]),
					exchange_b["exchange_lable"],
					split_price(exchange_b["sell"]["price"]),
					interest_rates(exchange_a["buy"]["price"], exchange_b["sell"]["price"]),
					split_price(abs(exchange_b["sell"]["price"] - exchange_a["buy"]["price"])),
					exchange_a["buy"]["vol"],
					exchange_b["sell"]["vol"],
					min(exchange_b["sell"]["vol"], exchange_a["buy"]["vol"]),
					ConsoleColor.OKBLUE, ConsoleColor.ENDC
				))


def compare_data(exchange_a, exchange_b, crypto_name, interest):
	if((exchange_a["buy"]["price"] < exchange_b["sell"]["price"]) and 
		interest_rates(exchange_a["buy"]["price"], exchange_b["sell"]["price"]) >= float(interest)):
		show_arbitrage(crypto_name, exchange_a, exchange_b)
	elif((exchange_b["buy"]["price"] < exchange_a["sell"]["price"]) and 
		interest_rates(exchange_b["buy"]["price"], exchange_a["sell"]["price"]) >= float(interest)):
		show_arbitrage(crypto_name, exchange_b, exchange_a)


def set_settings():
	"Setting the settings of program"
	os.system("clear")
	INTERVAL = get_key("INTERVAL")
	INTEREST = get_key("INTEREST")
	print("""
=====================
> SETTINGS
=====================
1) Check Interval: {0} s
2) Amount of Interest: {1} %
3) Main Menu  
		""".format(INTERVAL, INTEREST))
	
	_setting_id = getinput("To SET each one, select their number:")

	if (_setting_id == "3"):
		show_menu()

	# check if the choice is in valid range
	if(_setting_id not in ["1","2"]):
		print("wrong choise!")
		time.sleep(1)
		set_settings()

	_value = getinput("OK now the new value:")

	if(not is_number(_value)):
		print("wrong value!")
		time.sleep(1)
		set_settings()
	
	if(_setting_id == "1"):
		set_key("INTERVAL", _value)
	elif (_setting_id == "2"):
		set_key("INTEREST", _value)

	print("Setting has been set :)")
	time.sleep(1)
	set_settings()


def run_arbitrage():
	os.system("clear")
	ShowEnLables = True
	INTERVAL = get_key("INTERVAL")
	INTEREST = get_key("INTEREST")
	print("""
=====================
> Arbitrage BOT
=====================
1) Check Interval: {0} s
2) Amount of Interest: {1} %
To Stop press Ctrl + C
		""".format(INTERVAL, INTEREST))
	
	try:
		while True:
			crypto_data = get_crypto_data()

			COINS_LIST = ["BTC"]  # crypto_data["coins"].keys()
			
			for crypto in COINS_LIST:
				
				CRYPTO_DATA = crypto_data["coins"][crypto]
				
				for ex_a, ex_b in combinations(CRYPTO_DATA.keys(), 2):
				
					if(ShowEnLables):
						CRYPTO_DATA[ex_a]["exchange_lable"] = ex_a
						CRYPTO_DATA[ex_b]["exchange_lable"] = ex_b
				
					compare_data(CRYPTO_DATA[ex_a], CRYPTO_DATA[ex_b], crypto, INTEREST)			
			time.sleep(int(INTERVAL))
	except KeyboardInterrupt:
		print("Arbitrage Stopped")
		show_menu()


def show_menu():
	"this function shows main menu of program"

	os.system("clear")
	print(r"""

░█████╗░██████╗░██████╗░██╗████████╗██████╗░░█████╗░░██████╗░███████╗
██╔══██╗██╔══██╗██╔══██╗██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝░██╔════╝
███████║██████╔╝██████╦╝██║░░░██║░░░██████╔╝███████║██║░░██╗░█████╗░░
██╔══██║██╔══██╗██╔══██╗██║░░░██║░░░██╔══██╗██╔══██║██║░░╚██╗██╔══╝░░
██║░░██║██║░░██║██████╦╝██║░░░██║░░░██║░░██║██║░░██║╚██████╔╝███████╗
╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚═════╝░╚══════╝


BY ᙢ ᗴ ᖺ ᖇ ᖙ ᗩ ᕍ  ᐯ ᗴ ᔕ ᗩ ᒪ
""")

	print("""
# Please select one the following numbers:
① Settings
② Run the Arbitrage bot
③ Exit
		""")
	choice = getinput("enter the number: ")


	if choice == '1':
		set_settings()
	elif choice == '2':
		run_arbitrage()
	elif choice == '3':
		print("Good Bye")
		sys.exit()
	else:
		print("wrong choise!")
		time.sleep(1)
		show_menu()


if __name__ == "__main__":
	check_tbls()
	show_menu()


