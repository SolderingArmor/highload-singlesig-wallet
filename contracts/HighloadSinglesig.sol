pragma ton-solidity >=0.47.0;
pragma AbiHeader time;
pragma AbiHeader pubkey;
pragma AbiHeader expire;

//================================================================================
//
import "../interfaces/IHighloadSinglesig.sol";

//================================================================================
/// @title Highload Single Signature Wallet
/// @author SuperArmor (https://t.me/SuperArmor)
//
contract HighloadSinglesig is IHighloadSinglesig
{
    //========================================
    // Constants
    address constant addressZero = address.makeAddrStd(0, 0);
    
    //========================================
    // Variables
    mapping(uint256 => uint64) _messages;
    uint32                     _messageCount;

    //========================================
    // Error codes
    uint constant ERROR_MESSAGE_PUBKEY_IS_INCORRECT    = 100;
    uint constant ERROR_MESSAGE_SENDER_IS_NOT_MY_OWNER = 101;
    uint constant ERROR_MESSAGE_SENDER_IS_NOT_EXTERNAL = 102;
    uint constant ERROR_MESSAGE_ALREADY_SENT           = 103;

    //========================================
    // Modifiers
    modifier onlyOwner 
    {
        require(msg.pubkey() == tvm.pubkey(), ERROR_MESSAGE_SENDER_IS_NOT_MY_OWNER);
        require(msg.isExternal,               ERROR_MESSAGE_SENDER_IS_NOT_EXTERNAL);
        tvm.accept();
        _;
    }
    
    //========================================
    //
    constructor() public 
    {
        require(msg.pubkey() == tvm.pubkey(), ERROR_MESSAGE_PUBKEY_IS_INCORRECT);
        tvm.accept();
    }

    //========================================
    //
    function sendTransaction(address dest, uint128 value, bool bounce, uint16 flags, TvmCell payload) external override onlyOwner
    {
        dest.transfer(value, bounce, flags, payload);
        gc();
    }

    //========================================
    // Highload implementation
    function afterSignatureCheck(TvmSlice body, TvmCell message) private inline returns (TvmSlice) 
    {
        (, uint64 expireAt) = body.decode(uint64, uint32);
        require(expireAt > now, 57);

        uint256 msgHash = tvm.hash(message);
        require(!_messages.exists(msgHash), ERROR_MESSAGE_ALREADY_SENT);
        
        tvm.accept();
        _messages[msgHash] = expireAt;
        _messageCount += 1;

        return body;
    }

    //========================================
    // Garbage collection to delete expired messages.
    // We can't go through all messages every time, it's slow, expensive and we can hit the limit of execution
    // (1'000'000 gas) and contract will become unusable. We will go in batches of 50 instead, it will give us
    // low fees (on messages when the list is below 50) and gc 50 messages at once for about 350'000 gas total.
    function gc() private inline 
    {
        if(_messageCount < 50){  return;  }

        uint count = 0;        
        for((uint256 msgHash, uint64 expireAt) : _messages) 
        {
            count += 1;
            if(expireAt <= now) {  delete _messages[msgHash];  _messageCount -= 1;  }
            if(count > 50){  return;  }
        }
    }

    //========================================
    //
    function getMessages() public view override returns (Message[] messages) 
    {
        for ((uint256 msgHash, uint64 expireAt) : _messages) 
        {
            messages.push(Message(msgHash, expireAt));
        }
    }
}

//================================================================================
//
