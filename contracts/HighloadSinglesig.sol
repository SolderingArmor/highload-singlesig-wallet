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

        return body;
    }

    //========================================
    // Garbage collection to delete expired messages
    function gc() private inline 
    {
        optional(uint256, uint64) elm = _messages.min();
        
        while(elm.hasValue())
        {
            (uint256 msgHash, uint64 expireAt) = elm.get();
            if (expireAt <= now) 
            {
                delete _messages[msgHash];
            }
            elm = _messages.next(msgHash);
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
