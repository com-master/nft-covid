pragma ton-solidity >=0.43.0;

pragma AbiHeader expire;
pragma AbiHeader time;
pragma AbiHeader pubkey;

import './resolvers/IndexResolver.sol';
import './resolvers/DataResolver.sol';

import './IndexBasis.sol';

import './interfaces/IData.sol';
import './interfaces/IIndexBasis.sol';

contract NftRoot is DataResolver, IndexResolver {

    address static _addrOwner;
    uint256[] static _signs;
    uint256 public _totalMinted;
    address _addrBasis;

    constructor(TvmCell codeIndex, TvmCell codeData) public {
        tvm.accept();
        _codeIndex = codeIndex;
        _codeData = codeData;
    }

    function mintNft(bytes metadata) public {
        //tvm.rawReserve(0 ton, 4);
        tvm.accept();
        TvmCell codeData = _buildDataCode(address(this));
        TvmCell stateData = _buildDataState(codeData,metadata);
        new Data{stateInit: stateData, value: 1.3 ton}( _codeIndex,_signs);

        _totalMinted++;
    }

    function deployBasis(TvmCell codeIndexBasis) public {
        tvm.rawReserve(0 ton, 4);
        uint256 codeHasData = resolveCodeHashData();
        TvmCell state = tvm.buildStateInit({
            contr: IndexBasis,
            varInit: {
                _codeHashData: codeHasData,
                _addrRoot: address(this)
            },
            code: codeIndexBasis
        });
        _addrBasis = new IndexBasis{stateInit: state, value: 0.4 ton}();
    }

    function destructBasis() public view {
        IIndexBasis(_addrBasis).destruct();
    }
}