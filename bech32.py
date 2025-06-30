"""
Bech32 Implementation for Bitcoin SegWit Address Validation
===========================================================

A pure Python implementation of Bech32 address encoding/decoding.
Based on BIP 173 specification.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.0
"""

from typing import Optional, Tuple, List


class Bech32:
    """Bech32 address encoding/decoding implementation."""
    
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    
    @staticmethod
    def bech32_polymod(values: List[int]) -> int:
        """Compute the Bech32 checksum polymod."""
        generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for value in values:
            top = chk >> 25
            chk = (chk & 0x1ffffff) << 5 ^ value
            for i in range(5):
                chk ^= generator[i] if ((top >> i) & 1) else 0
        return chk
    
    @staticmethod
    def bech32_hrp_expand(hrp: str) -> List[int]:
        """Expand the HRP into values for checksum computation."""
        return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]
    
    @staticmethod
    def bech32_verify_checksum(hrp: str, data: List[int]) -> bool:
        """Verify a checksum given HRP and converted data characters."""
        return Bech32.bech32_polymod(Bech32.bech32_hrp_expand(hrp) + data) == 1
    
    @staticmethod
    def bech32_decode(bech: str) -> Tuple[Optional[str], Optional[List[int]]]:
        """
        Decode a Bech32 string.
        
        Returns: (hrp, data) or (None, None) if invalid
        """
        if len(bech) > 90:
            return (None, None)
        if not all(33 <= ord(x) <= 126 for x in bech):
            return (None, None)
        bech = bech.lower()
        pos = bech.rfind('1')
        if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
            return (None, None)
        if not all(x in Bech32.CHARSET for x in bech[pos+1:]):
            return (None, None)
        hrp = bech[:pos]
        data = [Bech32.CHARSET.find(x) for x in bech[pos+1:]]
        if not Bech32.bech32_verify_checksum(hrp, data):
            return (None, None)
        return (hrp, data[:-6])
    
    @staticmethod
    def convertbits(data: List[int], frombits: int, tobits: int, pad: bool = True) -> Optional[List[int]]:
        """Convert between bit groups."""
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        max_acc = (1 << (frombits + tobits - 1)) - 1
        for value in data:
            if value < 0 or (value >> frombits):
                return None
            acc = ((acc << frombits) | value) & max_acc
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if pad:
            if bits:
                ret.append((acc << (tobits - bits)) & maxv)
        elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
            return None
        return ret
    
    @staticmethod
    def decode_segwit_address(hrp: str, addr: str) -> Tuple[Optional[int], Optional[List[int]]]:
        """
        Decode a segwit address.
        
        Returns: (witness_version, witness_program) or (None, None) if invalid
        """
        hrpgot, data = Bech32.bech32_decode(addr)
        if hrpgot != hrp:
            return (None, None)
        if not data or len(data) < 1:
            return (None, None)
        decoded = Bech32.convertbits(data[1:], 5, 8, False)
        if decoded is None or len(decoded) < 2 or len(decoded) > 40:
            return (None, None)
        if data[0] > 16:
            return (None, None)
        if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
            return (None, None)
        return (data[0], decoded)


def validate_bitcoin_bech32(address: str) -> Tuple[bool, str]:
    """
    Validate a Bitcoin Bech32 (SegWit) address.
    
    Args:
        address: The Bitcoin address to validate
        
    Returns:
        (is_valid, address_type)
    """
    if not address.startswith('bc1'):
        return False, "Not Bech32"
    
    try:
        witness_version, witness_program = Bech32.decode_segwit_address("bc", address)
        
        if witness_version is None:
            return False, "Invalid Bech32"
        
        if witness_version == 0:
            if len(witness_program) == 20:
                return True, "P2WPKH (SegWit v0 pubkey hash)"
            elif len(witness_program) == 32:
                return True, "P2WSH (SegWit v0 script hash)"
        elif witness_version == 1 and len(witness_program) == 32:
            return True, "P2TR (Taproot)"
        else:
            return True, f"SegWit v{witness_version}"
            
    except Exception:
        return False, "Invalid Bech32"
    
    return False, "Unknown SegWit format"


def validate_litecoin_bech32(address: str) -> Tuple[bool, str]:
    """Validate a Litecoin Bech32 address."""
    if not address.startswith('ltc1'):
        return False, "Not Litecoin Bech32"
    
    try:
        witness_version, witness_program = Bech32.decode_segwit_address("ltc", address)
        
        if witness_version is None:
            return False, "Invalid Bech32"
        
        if witness_version == 0 and len(witness_program) in [20, 32]:
            return True, "Litecoin SegWit"
        
        return False, "Invalid Litecoin SegWit"
        
    except Exception:
        return False, "Invalid Bech32"