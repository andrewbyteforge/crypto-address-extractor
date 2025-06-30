"""
Cryptocurrency Address Validators Module
=======================================

This module provides validation classes for various cryptocurrency addresses.
It includes checksum validation and format verification for supported cryptocurrencies.

Enhanced version with full cryptographic validation where possible.

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.0
"""

import re
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple

# Try to import enhanced validation
try:
    from enhanced_validators import EnhancedValidators
    ENHANCED_VALIDATION = True
except ImportError:
    ENHANCED_VALIDATION = False
    logging.warning("Enhanced validators not available. Using basic validation.")


class AddressValidator(ABC):
    """
    Abstract base class for cryptocurrency address validators.
    
    Each cryptocurrency should implement its own validator that inherits
    from this base class and implements the validate method.
    """
    
    def __init__(self):
        """Initialize the validator with a logger."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def validate(self, address: str) -> Tuple[bool, float]:
        """
        Validate a cryptocurrency address.
        
        Args:
            address (str): The address to validate
        
        Returns:
            Tuple[bool, float]: (is_valid, confidence_adjustment)
                - is_valid: Whether the address passes validation
                - confidence_adjustment: Amount to add to confidence (0-100)
        """
        pass
    
    def validate_with_logging(self, address: str, crypto_type: str) -> Tuple[bool, float]:
        """
        Validate an address with logging.
        
        Args:
            address (str): The address to validate
            crypto_type (str): The cryptocurrency type
        
        Returns:
            Tuple[bool, float]: (is_valid, confidence_adjustment)
        """
        try:
            is_valid, confidence_adj = self.validate(address)
            
            if is_valid:
                self.logger.debug(f"Valid {crypto_type} address: {address}")
            else:
                self.logger.debug(f"Invalid {crypto_type} address: {address}")
            
            return is_valid, confidence_adj
            
        except Exception as e:
            self.logger.error(f"Error validating {crypto_type} address {address}: {str(e)}")
            return False, 0.0


class BitcoinValidator(AddressValidator):
    """Validator for Bitcoin addresses."""
    
    # Base58 alphabet (excludes 0, O, I, l)
    BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """
        Validate a Bitcoin address.
        
        Supports:
        - P2PKH (starts with 1)
        - P2SH (starts with 3)
        - Bech32 (starts with bc1)
        """
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_bitcoin(address)
                if is_valid:
                    self.logger.debug(f"Valid Bitcoin {addr_type}: {address}")
                return is_valid, confidence
            except Exception as e:
                self.logger.warning(f"Enhanced validation failed, falling back: {e}")
        
        # Fallback to basic validation
        if address.startswith('bc1'):
            return self._validate_bech32(address)
        elif address[0] in '13':
            return self._validate_base58_check(address)
        
        return False, 0.0
    
    def _validate_base58_check(self, address: str) -> Tuple[bool, float]:
        """Validate Base58Check encoded addresses."""
        try:
            # Decode Base58
            decoded = self._base58_decode(address)
            if len(decoded) != 25:
                return False, 0.0
            
            # Verify checksum
            checksum = decoded[-4:]
            payload = decoded[:-4]
            
            hash_result = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
            
            if hash_result[:4] == checksum:
                return True, 20.0  # High confidence boost for valid checksum
            
            return False, 0.0
            
        except Exception:
            return False, 0.0
    
    def _base58_decode(self, address: str) -> bytes:
        """Decode a Base58 string to bytes."""
        decoded = 0
        for char in address:
            decoded = decoded * 58 + self.BASE58_ALPHABET.index(char)
        
        return decoded.to_bytes(25, byteorder='big')
    
    def _validate_bech32(self, address: str) -> Tuple[bool, float]:
        """Validate Bech32 addresses (simplified)."""
        # Basic validation - full Bech32 validation is complex
        if not re.match(r'^bc1[a-z0-9]{39,59}$', address):
            return False, 0.0
        
        # Simplified validation
        return True, 15.0


class EthereumValidator(AddressValidator):
    """Validator for Ethereum addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """
        Validate an Ethereum address.
        
        Checks format and EIP-55 checksum if applicable.
        """
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, checksum_status = EnhancedValidators.validate_ethereum(address)
                if is_valid:
                    self.logger.debug(f"Ethereum address {checksum_status}: {address}")
                return is_valid, confidence
            except Exception as e:
                self.logger.warning(f"Enhanced validation failed, falling back: {e}")
        
        # Fallback to basic validation
        # Remove 0x prefix for validation
        if not address.startswith('0x') or len(address) != 42:
            return False, 0.0
        
        address_no_prefix = address[2:]
        
        # Check if it's all valid hex
        try:
            int(address_no_prefix, 16)
        except ValueError:
            return False, 0.0
        
        # If address has mixed case, validate EIP-55 checksum
        if address_no_prefix != address_no_prefix.lower() and address_no_prefix != address_no_prefix.upper():
            return self._validate_checksum(address)
        
        # All lowercase or uppercase addresses are valid but get lower confidence
        return True, 10.0
    
    def _validate_checksum(self, address: str) -> Tuple[bool, float]:
        """Validate EIP-55 checksum."""
        address_no_prefix = address[2:]
        
        # Hash the lowercase address
        address_hash = hashlib.sha256(address_no_prefix.lower().encode()).hexdigest()
        
        # Check each character
        for i in range(len(address_no_prefix)):
            char = address_no_prefix[i]
            if char in '0123456789':
                continue
            
            # Check if uppercase/lowercase matches hash
            hash_char = address_hash[i]
            if (int(hash_char, 16) >= 8 and char.upper() != char) or \
               (int(hash_char, 16) < 8 and char.lower() != char):
                return False, 0.0
        
        return True, 25.0  # High confidence for valid checksum


class MoneroValidator(AddressValidator):
    """Validator for Monero addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Monero address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_monero(address)
                return is_valid, confidence
            except Exception:
                pass
        
        # Basic length validation
        if len(address) not in [95, 106]:  # Standard or integrated address
            return False, 0.0
        
        # Check prefix
        if not (address.startswith('4') or address.startswith('8')):
            return False, 0.0
        
        # Monero uses base58 similar to Bitcoin but with different alphabet
        # Simplified validation here
        valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        if not all(c in valid_chars for c in address):
            return False, 0.0
        
        return True, 15.0


class TronValidator(AddressValidator):
    """Validator for Tron addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Tron address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_tron(address)
                return is_valid, confidence
            except Exception:
                pass
        
        if len(address) != 34 or not address.startswith('T'):
            return False, 0.0
        
        # Tron uses Base58Check similar to Bitcoin
        valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        if not all(c in valid_chars for c in address):
            return False, 0.0
        
        # Simplified validation - full Base58Check validation would be similar to Bitcoin
        return True, 15.0


class DogecoinValidator(AddressValidator):
    """Validator for Dogecoin addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Dogecoin address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_dogecoin(address)
                return is_valid, confidence
            except Exception:
                pass
        
        if len(address) not in [34]:
            return False, 0.0
        
        # Check prefix
        if not (address.startswith('D') or address.startswith('A') or address.startswith('9')):
            return False, 0.0
        
        # Dogecoin uses Base58Check like Bitcoin
        valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        if not all(c in valid_chars for c in address):
            return False, 0.0
        
        return True, 15.0


class RippleValidator(AddressValidator):
    """Validator for Ripple/XRP addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Ripple address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_ripple(address)
                return is_valid, confidence
            except Exception:
                pass
        
        if not address.startswith('r') or len(address) not in range(25, 36):
            return False, 0.0
        
        # Ripple uses its own Base58 variant
        valid_chars = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
        if not all(c in valid_chars for c in address):
            return False, 0.0
        
        return True, 15.0


class CardanoValidator(AddressValidator):
    """Validator for Cardano addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Cardano address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_cardano(address)
                return is_valid, confidence
            except Exception:
                pass
        
        # Shelley addresses
        if address.startswith('addr1'):
            if len(address) < 58:
                return False, 0.0
            # Bech32 format validation would go here
            return True, 20.0
        
        # Byron addresses
        elif address.startswith(('DdzFF', 'Ae2')):
            if len(address) < 50:
                return False, 0.0
            return True, 15.0
        
        return False, 0.0


class LitecoinValidator(AddressValidator):
    """Validator for Litecoin addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Litecoin address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_litecoin(address)
                return is_valid, confidence
            except Exception:
                pass
        
        # Legacy addresses
        if address[0] in 'LM3':
            if len(address) not in range(26, 35):
                return False, 0.0
            # Base58Check validation similar to Bitcoin
            return True, 15.0
        
        # SegWit addresses
        elif address.startswith('ltc1'):
            if not re.match(r'^ltc1[a-z0-9]{39,59}$', address):
                return False, 0.0
            return True, 15.0
        
        return False, 0.0


class StellarValidator(AddressValidator):
    """Validator for Stellar addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Stellar address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_stellar(address)
                return is_valid, confidence
            except Exception:
                pass
        
        if len(address) != 56 or not address.startswith('G'):
            return False, 0.0
        
        # Check if it's valid base32 (Stellar uses base32)
        valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
        if not all(c in valid_chars for c in address):
            return False, 0.0
        
        # Note: Full Stellar validation would include CRC16 checksum
        return True, 20.0


class SolanaValidator(AddressValidator):
    """Validator for Solana addresses."""
    
    def validate(self, address: str) -> Tuple[bool, float]:
        """Validate a Solana address."""
        # Use enhanced validation if available
        if ENHANCED_VALIDATION:
            try:
                is_valid, confidence, addr_type = EnhancedValidators.validate_solana(address)
                return is_valid, confidence
            except Exception:
                pass
        
        if len(address) not in range(32, 45):
            return False, 0.0
        
        # Solana uses base58 like Bitcoin but different format
        valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        if not all(c in valid_chars for c in address):
            return False, 0.0
        
        # Solana addresses don't have a consistent prefix pattern
        # This makes them harder to distinguish from random base58 strings
        return True, 10.0


class ValidatorFactory:
    """Factory class for creating appropriate validators."""
    
    _validators = {
        'BTC': BitcoinValidator,
        'ETH': EthereumValidator,
        'XMR': MoneroValidator,
        'MONERO': MoneroValidator,
        'TRON': TronValidator,
        'TRX': TronValidator,
        'USDT': EthereumValidator,  # Can be multiple chains
        'TETHER': EthereumValidator,
        'DOGE': DogecoinValidator,
        'DOGECOIN': DogecoinValidator,
        'XRP': RippleValidator,
        'RIPPLE': RippleValidator,
        'ADA': CardanoValidator,
        'CARDANO': CardanoValidator,
        'SHIB': EthereumValidator,  # ERC-20 token
        'SHIBA INU': EthereumValidator,
        'LTC': LitecoinValidator,
        'LITECOIN': LitecoinValidator,
        'XLM': StellarValidator,
        'STELLAR': StellarValidator,
        'SOL': SolanaValidator,
        'SOLANA': SolanaValidator
    }
    
    @classmethod
    def get_validator(cls, crypto_type: str) -> Optional[AddressValidator]:
        """
        Get the appropriate validator for a cryptocurrency type.
        
        Args:
            crypto_type (str): The cryptocurrency type
        
        Returns:
            Optional[AddressValidator]: The validator instance or None
        """
        validator_class = cls._validators.get(crypto_type.upper())
        if validator_class:
            return validator_class()
        return None