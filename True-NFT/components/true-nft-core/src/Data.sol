pragma ton-solidity >=0.43.0;

pragma AbiHeader expire;
pragma AbiHeader time;
pragma AbiHeader pubkey;

import './resolvers/IndexResolver.sol';

import './interfaces/IData.sol';

import './libraries/Constants.sol';
struct AuthorityMsg {
    string amsg;
    uint256 pubkey;
}
enum msgStatus {
    notExist,
    Exist

}

contract Data is IData, IndexResolver {
    address _addrRoot;
    address _addrAuthor;

    mapping(uint256 => msgStatus) public _authority_signs;
    AuthorityMsg[] _messages;
    bytes static _name;

    constructor(TvmCell codeIndex, uint256[] authority_signs) public {
        optional(TvmCell) optSalt = tvm.codeSalt(tvm.code());
        require(optSalt.hasValue(), 101);
        (address addrRoot) = optSalt.get().toSlice().decode(address);
        require(msg.sender == addrRoot);
        require(msg.value >= Constants.MIN_FOR_DEPLOY);
        tvm.accept();
        _addrRoot = addrRoot;
        _codeIndex = codeIndex;
        for (uint i = 0; i < authority_signs.length ; i++) {
            _authority_signs[authority_signs[i]] = msgStatus.Exist;
        }

    }



    function getInfo() public view returns (
        address addrRoot,
        address addrData,
        bytes nameRoot,
        AuthorityMsg[] messages
    ) {
        addrRoot = _addrRoot;
        addrData = address(this);
        nameRoot = _name;
        messages = _messages;
    }

    function addMessage(string amsg) public externalMsg {
        require(_authority_signs.exists(msg.pubkey()),201, "Invalid sign");
        tvm.accept();
        AuthorityMsg obj;
        obj.amsg = amsg;
        obj.pubkey = msg.pubkey();
        _messages.push(obj);
    }

}