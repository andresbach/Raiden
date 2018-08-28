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

#fondosEth = 0.1
#minteoTokens = 100
def fondeoBC(fondosEth, minteoTokens):
	for i in range(1,len(acc)):
		if(minteoTokens > 0):
			RTT.functions.mintFor(minteoTokens, acc[i]).transact({"from": acc[0], "gasPrice": web3.toWei(5, 'Gwei'), "gas": 1000000})
		if(fondosEth > 0):
			web3.eth.sendTransaction({"to": acc[i], "from": acc[0], "gasPrice": web3.toWei(5, 'Gwei'), "gas": 1000000, "value": web3.toWei(fondosEth, 'ether')})

def balances():
	for i in range(1,len(acc)):
		print(i, ',', RTT.functions.balanceOf(acc[i]).call(), ',', web3.eth.getBalance(acc[i]), 'wei.')

def comando(paraAcc):
	print("./Downloads/Raiden/raiden-0.5.0-linux --keystore-path ~/.ethereum/testnet/keystore/ --api-address '127.0.0.1:500"+str(paraAcc)+"' --listen-address '0.0.0.0:4000"+str(paraAcc)+"' --eth-rpc-endpoint 'http://10.10.0.83:8545' --log-config='raiden:DEBUG' --address '"+acc[paraAcc]+"' --password-file pass --gas-price 5000000000")

# para abrir los procesos, vi que funciona haciendo
#output = subprocess.Popen(["stress","-c","1"], stdout=subprocess.PIPE)
# y luego con
#output.kill()
# lo "mata" dentro del proceso de ipython. En stress lo mata cuando le doy ctl + c despues de haber hecho
#output.communicate()
#el PID me lo da con
#output.pid
# igual no me conviene abrirlo de fondo porque asi puedo ver que es lo que esta ocurriendo con el cliente del usuario.

tiempo = None

def canales(emisor):
	cha = requests.get('http://localhost:500'+str(emisor)+'/api/1/channels')
	return cha.json()

def tokens(emisor):
	tok = requests.get('http://localhost:500'+str(emisor)+'/api/1/tokens')
	return tok.json()

def eventos(emisor, bloque):# deberia agregarle el token que tambien usaria
	even = requests.get('http://localhost:500'+str(emisor)+'/api/1/events/tokens/0x0f114A1E9Db192502E7856309cc899952b3db1ED?from_block=3809000')
	return even.json()

def conexiones(emisor):
	conn = requests.get('http://localhost:500'+str(emisor)+'/api/1/connections')
	return conn.json()

def abrir(emisor, deposito, receptor, settletime):# deberia agregarle el token que tambien usaria
	global tiempo, apertura
	start = time.perf_counter()
	apertura = requests.put('http://localhost:500'+str(emisor)+'/api/1/channels', headers={'Content-Type': 'application/json'}, json={'balance': deposito, 'partner_address': acc[receptor], 'settle_timeout': settletime, 'token_address': '0x0f114A1E9Db192502E7856309cc899952b3db1ED'})
	tiempo = time.perf_counter() - start
	return apertura.json()

def fondeoCh(emisor, receptor, deposito):# el fondeo lo hace sobre el total. Si ya puse antes, tiene que ser un monto mayor al que tenia antes, sino me lo devuelve como OK
	global tiempo, funds
	start = time.perf_counter()
	funds = requests.patch('http://localhost:500'+str(emisor)+'/api/1/channels/0x0f114A1E9Db192502E7856309cc899952b3db1ED/'+acc[receptor], headers={'Content-Type': 'application/json'}, json={'total_deposit': deposito})
	tiempo = time.perf_counter() - start
	return funds.json()

def transferir(emisor, receptor, cantidad, ref):# deberia agregarle el token que tambien usaria
	global tiempo, tran
	start = time.perf_counter()
	tran = requests.post('http://localhost:500'+str(emisor)+'/api/1/payments/0x0f114A1E9Db192502E7856309cc899952b3db1ED/'+acc[receptor], headers={'Content-Type': 'application/json'}, json={'amount': cantidad, 'identifier': ref})
	tiempo = time.perf_counter() - start
	return tran.json()

def cerrar(emisor, receptor):# el fondeo lo hace sobre el total. Si ya puse antes, tiene que ser un monto mayor al que tenia antes, sino me lo devuelve como OK
	global tiempo, close
	start = time.perf_counter()
	close = requests.patch('http://localhost:500'+str(emisor)+'/api/1/channels/0x0f114A1E9Db192502E7856309cc899952b3db1ED/'+acc[receptor], headers={'Content-Type': 'application/json'}, json={'state': 'closed'})
	tiempo = time.perf_counter() - start
	return close.json()

def irse(emisor):# el fondeo lo hace sobre el total. Si ya puse antes, tiene que ser un monto mayor al que tenia antes, sino me lo devuelve como OK
	global tiempo, leave
	start = time.perf_counter()
	leave = requests.delete('http://localhost:500'+str(emisor)+'/api/1/connections/0x0f114A1E9Db192502E7856309cc899952b3db1ED', headers={'Content-Type': 'application/json'})
	tiempo = time.perf_counter() - start
	return leave.json()

# este crea canales entre una cuenta y su consecutiva. Fondea la primera
def creador(peers):
	global tiempo, tiempoProm, mediciones
	mediciones = []
	start = time.perf_counter()
	for i in range(1, peers):
		startintern = time.perf_counter()
		print('Abro entre cuenta', i, 'y', i+1, 'por 10 tokens')
		abrir(i, 10, i+1, 500)
		mediciones.append([i,time.perf_counter()-startintern])
	tiempo = time.perf_counter() - start
	tiempoProm = tiempo/peers
	return tiempo

# este fondea desde una cuenta a su anterior para canales ya abiertos
def fondeador(peers):
	global tiempo, tiempoProm, mediciones
	mediciones = []
	start = time.perf_counter()
	for i in range(1, peers):
		startintern = time.perf_counter()
		print('Fondeo entre cuenta', i+1, 'y', i, 'por 10 tokens')
		fondeoCh(i+1, i, 10)
		mediciones.append([i,time.perf_counter()-startintern])
	tiempo = time.perf_counter() - start
	tiempoProm = tiempo/peers
	return tiempo


# a partir de ahora hago los tests
tiempoProm = None
mediciones = []

# este es para hacer ciclos de ida y vuelta de los tokens simetricos (en caso par) para las dos primeras cuentas
def test1(ciclos):
	global tiempo, tiempoProm, mediciones
	mediciones = []
	start = time.perf_counter()
	vaA = True
	for i in range(ciclos):
		startintern = time.perf_counter()
		if (vaA):
			print(i, 'Transfiero de 1 a 2')
			transferir(1,2,1,i)
			vaA = False
		else:
			print(i, 'Transfiero de 2 a 1')
			transferir(2,1,1,i)
			vaA = True
		mediciones.append([i,time.perf_counter()-startintern])
	tiempo = time.perf_counter() - start
	tiempoProm = tiempo/ciclos
	return tiempo

# este es para enviar cierta cantidad de transacciones entre la primera y segunda cuenta
def test2(idas, emisor):
	global tiempo, tiempoProm, mediciones
	mediciones = []
	start = time.perf_counter()
	for i in range(idas):
		startintern = time.perf_counter()
		if (emisor == 1):
			print(i, 'Transfiero de 1 a 2')
			transferir(1,2,1,i)
		else:
			print(i, 'Transfiero de 2 a 1')
			transferir(2,1,1,i)
		mediciones.append([i,time.perf_counter()-startintern])
	tiempo = time.perf_counter() - start
	tiempoProm = tiempo/idas
	return tiempo

# cicla transacciones de ida y vuelta entre un emisor y receptor dados
def test3(ciclos, emisor, receptor):
	global tiempo, tiempoProm, mediciones
	mediciones = []
	start = time.perf_counter()
	vaA = True
	for i in range(ciclos):
		startintern = time.perf_counter()
		if (vaA):
			print(i, 'Transfiero de ', emisor, 'a', receptor)
			transferir(emisor,receptor,1,i)
			vaA = False
		else:
			print(i, 'Transfiero de ', receptor, 'a', emisor)
			transferir(receptor,emisor,1,i)
			vaA = True
		mediciones.append([i,time.perf_counter()-startintern])
	tiempo = time.perf_counter() - start
	tiempoProm = tiempo/ciclos
	return tiempo

# envia ciertas idas de transacciones en un sentido entre un emisor y receptor dados
def test4(idas, emisor, receptor):
	global tiempo, tiempoProm, mediciones
	mediciones = []
	start = time.perf_counter()
	for i in range(idas):
		print(i, 'Transfiero de ', emisor, 'a', receptor)
		startintern = time.perf_counter()
		transferir(emisor,receptor,1,i)
		mediciones.append([i,time.perf_counter()-startintern])
	tiempo = time.perf_counter() - start
	tiempoProm = tiempo/idas
	return tiempo
