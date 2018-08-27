import requests, os, time

# Creo cuentas

# nAcc = 0
def nuevasCuentas(nAcc):
	with open("./pass") as password_file:
		password = password_file.read()
		password = password[:len(password)-1] # EOF cuenta como 1 char
	for i in range(nAcc):
		web3.personal.newAccount(password)
	del password
	global acc
	acc = web3.eth.accounts

contract_address = '0x0f114A1E9Db192502E7856309cc899952b3db1ED'
with open("RTT.abi") as contract_abi_file:
	contract_abi = json.load(contract_abi_file)
RTT = web3.eth.contract(address = contract_address, abi = contract_abi)
