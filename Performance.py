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
