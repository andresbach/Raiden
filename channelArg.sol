pragma solidity ^0.4.0;

contract Channel {

	address public Alicia;
	address public Benancio;
	uint public startDate;
	uint public channelTimeout;
	mapping (bytes32 => address) signatures;

	function Channel(address to, uint timeout) payable {
		Benancio = to;
		Alicia = msg.sender;
		startDate = now;
		channelTimeout = timeout;
	}

	// estos son partes del mensaje firmado, se divide r son ultimos 32bytes por ejemplo
	function CloseChannel(bytes32 h, uint8 v, bytes32 r, bytes32 s, uint value){

		address signer;
		bytes32 proof;

		// get signer from signature
		signer = ecrecover(h, v, r, s);

		// signature is invalid, throw
		if (signer != Alicia && signer != Benancio) throw;

		proof = sha3(this, value);

		// signature is valid but doesn't match the data provided
		if (proof != h) throw;

		if (signatures[proof] == 0)
			signatures[proof] = signer;
		else if (signatures[proof] != signer){
			// channel completed, both signatures provided
			if (!Benancio.send(value)) throw;
			selfdestruct(Alicia);
		}

	}

	function ChannelTimeout(){
		if (startDate + channelTimeout > now)
			throw;

		selfdestruct(Alicia);
	}

}
