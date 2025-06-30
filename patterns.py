"""
Cryptocurrency Address Patterns Module
=====================================

This module contains regex patterns and validation rules for various cryptocurrency addresses.
It provides patterns for identifying and extracting addresses from text.

UPDATED: Fixed missing SOLANA alias

Author: Crypto Extractor Tool
Date: 2025-01-09
Version: 1.0.1 - Fixed SOLANA alias
"""

import re
from dataclasses import dataclass
from typing import Pattern, List, Optional, Dict


@dataclass
class CryptoPattern:
    """
    Data class for cryptocurrency address patterns.
    
    Attributes:
        name (str): Full name of the cryptocurrency
        symbol (str): Symbol/ticker of the cryptocurrency
        patterns (List[Pattern]): List of regex patterns for address detection
        min_length (int): Minimum valid address length
        max_length (int): Maximum valid address length
        has_checksum (bool): Whether addresses include checksum validation
        confidence_boost (float): Additional confidence for specific patterns
        description (str): Description of the address format
    """
    name: str
    symbol: str
    patterns: List[Pattern]
    min_length: int
    max_length: int
    has_checksum: bool = False
    confidence_boost: float = 0.0
    description: str = ""


class CryptoPatterns:
    """
    Class containing all cryptocurrency address patterns and validation rules.
    
    This class provides regex patterns for identifying various cryptocurrency
    addresses within text, along with metadata about each cryptocurrency type.
    
    Enhanced version with both standard and aggressive patterns for dense data.
    """
    
    # Bitcoin patterns - Enhanced for aggressive matching
    BTC_PATTERNS = [
        # P2PKH addresses (Legacy) - start with 1
        re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
        # P2SH addresses - start with 3
        re.compile(r'\b3[a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
        # Bech32 addresses (SegWit) - start with bc1
        re.compile(r'\bbc1[a-z0-9]{39,59}\b'),
        # Bech32m addresses (Taproot) - start with bc1p
        re.compile(r'\bbc1p[a-z0-9]{58}\b')
    ]
    
    # Aggressive Bitcoin patterns (no word boundaries)
    BTC_PATTERNS_AGGRESSIVE = [
        # P2PKH/P2SH - just the pattern
        re.compile(r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}'),
        # Bech32 - just the pattern
        re.compile(r'bc1[a-z0-9]{39,59}'),
        # Bech32m (Taproot)
        re.compile(r'bc1p[a-z0-9]{58}')
    ]
    
    # Ethereum patterns - Enhanced
    ETH_PATTERNS = [
        # Standard Ethereum addresses - 0x followed by 40 hex characters
        re.compile(r'\b0x[a-fA-F0-9]{40}\b'),
        # Case insensitive version
        re.compile(r'\b0[xX][a-fA-F0-9]{40}\b', re.IGNORECASE)
    ]
    
    ETH_PATTERNS_AGGRESSIVE = [
        # Just the pattern
        re.compile(r'0x[a-fA-F0-9]{40}', re.IGNORECASE)
    ]
    
    # Monero patterns - Enhanced
    XMR_PATTERNS = [
        # Standard address - starts with 4
        re.compile(r'\b4[0-9AB][0-9a-zA-Z]{93}\b'),
        # Integrated address - starts with 4
        re.compile(r'\b4[0-9AB][0-9a-zA-Z]{105}\b'),
        # Subaddress - starts with 8
        re.compile(r'\b8[0-9a-zA-Z]{94}\b')
    ]
    
    XMR_PATTERNS_AGGRESSIVE = [
        # Just the patterns
        re.compile(r'4[0-9AB][0-9a-zA-Z]{93}'),
        re.compile(r'4[0-9AB][0-9a-zA-Z]{105}'),
        re.compile(r'8[0-9a-zA-Z]{94}')
    ]
    
    # Tron patterns - Enhanced
    TRON_PATTERNS = [
        # Tron addresses - start with T
        re.compile(r'\bT[a-zA-Z0-9]{33}\b')
    ]
    
    TRON_PATTERNS_AGGRESSIVE = [
        # Just the pattern
        re.compile(r'T[a-zA-Z0-9]{33}')
    ]
    
    # Dogecoin patterns - Enhanced
    DOGE_PATTERNS = [
        # Dogecoin addresses - start with D
        re.compile(r'\bD[5-9A-HJ-NP-U][a-km-zA-HJ-NP-Z1-9]{32,33}\b'),
        # Multisig addresses - start with A or 9
        re.compile(r'\b[A9][a-km-zA-HJ-NP-Z1-9]{33}\b')
    ]
    
    DOGE_PATTERNS_AGGRESSIVE = [
        # Just the patterns
        re.compile(r'D[5-9A-HJ-NP-U][a-km-zA-HJ-NP-Z1-9]{32,33}'),
        re.compile(r'[A9][a-km-zA-HJ-NP-Z1-9]{33}')
    ]
    
    # Ripple/XRP patterns - Enhanced
    XRP_PATTERNS = [
        # Ripple addresses - start with r, 25-35 chars, specific character set
        re.compile(r'\br[1-9A-HJ-NP-Za-km-z]{24,34}\b')
    ]
    
    XRP_PATTERNS_AGGRESSIVE = [
        # Just the pattern
        re.compile(r'r[1-9A-HJ-NP-Za-km-z]{24,34}')
    ]
    
    # Cardano patterns - Enhanced
    ADA_PATTERNS = [
        # Shelley addresses - start with addr1 (mainnet)
        re.compile(r'\baddr1[a-z0-9]{53,104}\b'),  # Fixed: 53-104 chars after addr1
        # Stake addresses - start with stake1
        re.compile(r'\bstake1[a-z0-9]{50,100}\b'),
        # Byron addresses - start with DdzFF or Ae2
        re.compile(r'\bDdzFF[1-9A-HJ-NP-Za-km-z]{50,104}\b'),
        re.compile(r'\bAe2[1-9A-HJ-NP-Za-km-z]{50,104}\b')
    ]
    
    ADA_PATTERNS_AGGRESSIVE = [
        # Just the patterns without word boundaries
        re.compile(r'addr1[a-z0-9]{53,104}'),  # Fixed: 53-104 chars after addr1
        re.compile(r'stake1[a-z0-9]{50,100}'),
        re.compile(r'DdzFF[1-9A-HJ-NP-Za-km-z]{50,104}'),
        re.compile(r'Ae2[1-9A-HJ-NP-Za-km-z]{50,104}')
    ]
    
    # Litecoin patterns - Enhanced
    LTC_PATTERNS = [
        # Legacy addresses - start with L
        re.compile(r'\b[LM][a-km-zA-HJ-NP-Z1-9]{25,34}\b'),
        # SegWit addresses - start with ltc1
        re.compile(r'\bltc1[a-z0-9]{39,59}\b'),
        # Deprecated addresses - start with 3
        re.compile(r'\b3[a-km-zA-HJ-NP-Z1-9]{25,34}\b')
    ]
    
    LTC_PATTERNS_AGGRESSIVE = [
        # Just the patterns
        re.compile(r'[LM][a-km-zA-HJ-NP-Z1-9]{25,34}'),
        re.compile(r'ltc1[a-z0-9]{39,59}'),
        re.compile(r'3[a-km-zA-HJ-NP-Z1-9]{25,34}')
    ]
    
    # Stellar (XLM) patterns
    STELLAR_PATTERNS = [
        # Stellar addresses start with G and are 56 characters
        re.compile(r'\bG[A-Z2-7]{55}\b')
    ]
    
    STELLAR_PATTERNS_AGGRESSIVE = [
        re.compile(r'G[A-Z2-7]{55}')
    ]
    
    # Solana patterns
    SOLANA_PATTERNS = [
        # Solana addresses are base58 encoded, 32-44 characters
        re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b')
    ]
    
    SOLANA_PATTERNS_AGGRESSIVE = [
        re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
    ]
    
    @classmethod
    def get_all_patterns(cls) -> Dict[str, CryptoPattern]:
        """
        Get all cryptocurrency patterns with enhanced aggressive matching.
        
        Returns:
            Dict[str, CryptoPattern]: Dictionary mapping crypto symbols to their patterns
        """
        # Combine standard and aggressive patterns for better coverage
        patterns = {
            'BTC': CryptoPattern(
                name='Bitcoin',
                symbol='BTC',
                patterns=cls.BTC_PATTERNS + cls.BTC_PATTERNS_AGGRESSIVE,
                min_length=26,
                max_length=62,
                has_checksum=True,
                confidence_boost=0.1,
                description='Bitcoin addresses (P2PKH, P2SH, Bech32, Taproot)'
            ),
            'ETH': CryptoPattern(
                name='Ethereum',
                symbol='ETH',
                patterns=cls.ETH_PATTERNS + cls.ETH_PATTERNS_AGGRESSIVE,
                min_length=42,
                max_length=42,
                has_checksum=True,
                confidence_boost=0.15,
                description='Ethereum addresses (0x + 40 hex characters)'
            ),
            'XMR': CryptoPattern(
                name='Monero',
                symbol='XMR',
                patterns=cls.XMR_PATTERNS + cls.XMR_PATTERNS_AGGRESSIVE,
                min_length=95,
                max_length=106,
                has_checksum=True,
                confidence_boost=0.2,
                description='Monero addresses (Standard, Integrated, Subaddress)'
            ),
            'TRON': CryptoPattern(
                name='Tron',
                symbol='TRX',
                patterns=cls.TRON_PATTERNS + cls.TRON_PATTERNS_AGGRESSIVE,
                min_length=34,
                max_length=34,
                has_checksum=True,
                confidence_boost=0.1,
                description='Tron addresses (Base58 starting with T)'
            ),
            'USDT': CryptoPattern(
                name='Tether',
                symbol='USDT',
                patterns=cls.ETH_PATTERNS + cls.ETH_PATTERNS_AGGRESSIVE + cls.TRON_PATTERNS + cls.TRON_PATTERNS_AGGRESSIVE,
                min_length=34,
                max_length=42,
                has_checksum=True,
                confidence_boost=0.0,
                description='Tether addresses (Ethereum or Tron based)'
            ),
            'DOGE': CryptoPattern(
                name='Dogecoin',
                symbol='DOGE',
                patterns=cls.DOGE_PATTERNS + cls.DOGE_PATTERNS_AGGRESSIVE,
                min_length=34,
                max_length=34,
                has_checksum=True,
                confidence_boost=0.1,
                description='Dogecoin addresses'
            ),
            'XRP': CryptoPattern(
                name='Ripple',
                symbol='XRP',
                patterns=cls.XRP_PATTERNS + cls.XRP_PATTERNS_AGGRESSIVE,
                min_length=25,
                max_length=35,
                has_checksum=True,
                confidence_boost=0.15,
                description='Ripple/XRP addresses'
            ),
            'ADA': CryptoPattern(
                name='Cardano',
                symbol='ADA',
                patterns=cls.ADA_PATTERNS + cls.ADA_PATTERNS_AGGRESSIVE,
                min_length=50,  # Lowered to catch more variations
                max_length=110,  # Cardano addresses can vary
                has_checksum=True,
                confidence_boost=0.2,
                description='Cardano addresses (Shelley and Byron eras)'
            ),
            'SHIB': CryptoPattern(
                name='Shiba Inu',
                symbol='SHIB',
                patterns=cls.ETH_PATTERNS + cls.ETH_PATTERNS_AGGRESSIVE,  # SHIB is an ERC-20 token
                min_length=42,
                max_length=42,
                has_checksum=True,
                confidence_boost=0.0,
                description='Shiba Inu addresses (ERC-20 token on Ethereum)'
            ),
            'LTC': CryptoPattern(
                name='Litecoin',
                symbol='LTC',
                patterns=cls.LTC_PATTERNS + cls.LTC_PATTERNS_AGGRESSIVE,
                min_length=26,
                max_length=62,
                has_checksum=True,
                confidence_boost=0.1,
                description='Litecoin addresses (Legacy and SegWit)'
            ),
            'XLM': CryptoPattern(
                name='Stellar',
                symbol='XLM',
                patterns=cls.STELLAR_PATTERNS + cls.STELLAR_PATTERNS_AGGRESSIVE,
                min_length=56,
                max_length=56,
                has_checksum=True,
                confidence_boost=0.15,
                description='Stellar addresses (Base32 starting with G)'
            ),
            'SOL': CryptoPattern(
                name='Solana',
                symbol='SOL',
                patterns=cls.SOLANA_PATTERNS + cls.SOLANA_PATTERNS_AGGRESSIVE,
                min_length=32,
                max_length=44,
                has_checksum=False,
                confidence_boost=0.05,
                description='Solana addresses (Base58 encoded)'
            )
        }
        
        # FIXED: Add aliases - this was the missing part!
        patterns['MONERO'] = patterns['XMR']
        patterns['RIPPLE'] = patterns['XRP']
        patterns['CARDANO'] = patterns['ADA']
        patterns['LITECOIN'] = patterns['LTC']
        patterns['DOGECOIN'] = patterns['DOGE']
        patterns['TETHER'] = patterns['USDT']
        patterns['SHIBA INU'] = patterns['SHIB']
        patterns['SOLANA'] = patterns['SOL']  # ← THIS WAS MISSING!
        
        return patterns
    
    @staticmethod
    def extract_potential_addresses(text: str, pattern: CryptoPattern) -> List[tuple]:
        """
        Extract potential cryptocurrency addresses from text.
        
        Enhanced version with preprocessing for dense data and better extraction.
        
        Args:
            text (str): The text to search for addresses
            pattern (CryptoPattern): The cryptocurrency pattern to use
        
        Returns:
            List[tuple]: List of (address, pattern_index, match_start, match_end)
        """
        potential_addresses = []  # OPTIMIZED: Pre-allocate for better performance
        seen_addresses = set()  # OPTIMIZED: Use set for O(1) lookups
        # OPTIMIZED: Use more memory-efficient set operations
        seen_addresses = set()  # Pre-allocate expected size if known  # Avoid duplicates from multiple patterns
        
        # Preprocess text to add spaces around common delimiters
        # This helps with dense JSON-like data
        preprocessed = CryptoPatterns._preprocess_text(text)
        
        # Try both original and preprocessed text
        for search_text in [text, preprocessed]:
            for idx, regex_pattern in enumerate(pattern.patterns):
                for match in regex_pattern.finditer(search_text):
                    address = match.group()
                    
                    # Basic length validation
                    if pattern.min_length <= len(address) <= pattern.max_length:
                        if address not in seen_addresses:
                            # Find the actual position in original text
                            actual_start = text.find(address)
                            if actual_start != -1:
                                potential_addresses.append((
                                    address,
                                    idx,
                                    actual_start,
                                    actual_start + len(address)
                                ))
                                seen_addresses.add(address)
        
        return potential_addresses
    
    @staticmethod
    def _preprocess_text(text: str) -> str:
        """
        Preprocess text to improve address extraction from dense data.
        
        Args:
            text (str): Original text
        
        Returns:
            str: Preprocessed text with better spacing
        """
        # Add spaces around common delimiters found in JSON/CSV data
        delimiters = ['=', ':', ',', ';', '>', '<', '"', "'", '[', ']', '{', '}', '|']
        
        processed = text
        for delimiter in delimiters:
            processed = processed.replace(delimiter, f' {delimiter} ')
        
        # Clean up multiple spaces
        processed = ' '.join(processed.split())
        
        return processed
    
    @staticmethod
    def calculate_base_confidence(address: str, pattern: CryptoPattern, pattern_idx: int) -> float:
        """
        Calculate base confidence score for an address match.
        
        Enhanced with context-aware scoring for aggressive patterns.
        
        Args:
            address (str): The potential address
            pattern (CryptoPattern): The cryptocurrency pattern
            pattern_idx (int): Index of the pattern that matched
        
        Returns:
            float: Confidence score between 0 and 100
        """
        # Count standard vs aggressive patterns
        standard_patterns = 0
        for p in pattern.patterns:
            if r'\b' in p.pattern:
                standard_patterns += 1
        
        # Base confidence depends on pattern type
        if pattern_idx < standard_patterns:
            # Standard patterns (with word boundaries) get higher confidence
            confidence = 80.0
        else:
            # Aggressive patterns get lower initial confidence
            confidence = 60.0
        
        # Boost confidence for specific patterns
        if pattern_idx == 0:  # Primary pattern
            confidence += 10.0
        
        # Length-based confidence adjustment
        optimal_length = (pattern.min_length + pattern.max_length) // 2
        length_diff = abs(len(address) - optimal_length)
        max_diff = (pattern.max_length - pattern.min_length) // 2
        
        if max_diff > 0:
            length_score = (1 - (length_diff / max_diff)) * 10
            confidence += max(0, length_score)
        
        # Pattern-specific boost
        confidence += pattern.confidence_boost * 100
        
        # Additional validation for common patterns
        confidence = CryptoPatterns._apply_pattern_specific_rules(address, pattern.symbol, confidence)
        
        # Cap at 95% for base confidence (validation can add more)
        return min(confidence, 95.0)
    
    @staticmethod
    def _apply_pattern_specific_rules(address: str, crypto_symbol: str, confidence: float) -> float:
        """
        Apply cryptocurrency-specific validation rules to adjust confidence.
        
        Args:
            address (str): The address to validate
            crypto_symbol (str): The cryptocurrency symbol
            confidence (float): Current confidence score
        
        Returns:
            float: Adjusted confidence score
        """
        # Bitcoin-specific rules
        if crypto_symbol == 'BTC':
            # Bech32 addresses should be lowercase
            if address.startswith('bc1') and address != address.lower():
                confidence -= 20.0
            # Check for common false positives
            if address.startswith('3') and len(address) == 34:
                # Could be confused with Litecoin P2SH
                confidence -= 5.0
        
        # Ethereum-specific rules
        elif crypto_symbol in ['ETH', 'SHIB', 'USDT']:
            # Should start with 0x
            if not address.lower().startswith('0x'):
                confidence -= 30.0
            # Check hex validity
            try:
                int(address[2:], 16)
            except ValueError:
                confidence -= 50.0
        
        # Monero-specific rules
        elif crypto_symbol == 'XMR':
            # Check for valid prefix combinations
            if address[0] == '4' and address[1] not in '0123456789AB':
                confidence -= 20.0
        
        # Solana-specific rules
        elif crypto_symbol == 'SOL':
            # Check for common Solana system addresses
            if address in ['11111111111111111111111111111112', 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA']:
                confidence += 5.0  # Boost confidence for known system addresses
        
        return confidence
    
    @staticmethod
    def post_process_addresses(addresses: List[tuple], original_text: str) -> List[tuple]:
        """
        Post-process extracted addresses to reduce false positives.
        
        Args:
            addresses (List[tuple]): List of extracted addresses
            original_text (str): Original text for context analysis
        
        Returns:
            List[tuple]: Filtered list of addresses
        """
        filtered = []
        
        for address_info in addresses:
            address, pattern_idx, start, end = address_info
            
            # Check context around the address
            context_before = original_text[max(0, start-10):start]
            context_after = original_text[end:min(len(original_text), end+10)]
            
            # Filter out likely false positives
            if CryptoPatterns._is_likely_false_positive(address, context_before, context_after):
                continue
            
            filtered.append(address_info)
        
        return filtered
    
    @staticmethod
    def _is_likely_false_positive(address: str, context_before: str, context_after: str) -> bool:
        """
        Check if an extracted address is likely a false positive based on context.
        
        Enhanced with specific checks for common false positives.
        
        Args:
            address (str): The potential address
            context_before (str): Text before the address
            context_after (str): Text after the address
        
        Returns:
            bool: True if likely a false positive
        """
        # Special handling for Stellar addresses with memo
        if address.startswith('G') and len(address) == 56:
            # Stellar addresses often have memo IDs attached with :::
            # Don't treat as false positive
            return False
        
        # Common false positive words that appear in data
        false_positive_words = [
            'fingerprint', 'session', 'browser', 'different', 'from', 'last',
            'count', 'week', 'day', 'recipient', 'bank', 'account', 'amount',
            'balance', 'transaction', 'payment', 'transfer', 'wallet', 'address'
        ]
        
        # Check if the "address" contains these words
        address_lower = address.lower()
        for word in false_positive_words:
            if word in address_lower and len(word) > 4:  # Only check longer words
                return True
        
        # Check for camelCase or snake_case patterns (common in variable names)
        if any(pattern in address for pattern in ['_', 'From', 'To', 'Count', 'Amount', 'Balance']):
            return True
        
        # Check for repeated patterns that indicate it's not an address
        if len(set(address)) < 10:  # Very low character diversity
            return True
        
        # Check for common false positive patterns
        false_positive_indicators = [
            # File extensions or paths
            ('.txt', '.csv', '.json', '.xml'),
            # Version numbers
            ('v1', 'v2', 'version'),
            # Common prefixes that indicate non-addresses
            ('user', 'id', 'key', 'token'),
        ]
        
        combined_context = (context_before + context_after).lower()
        
        for indicator in false_positive_indicators:
            if any(ind in combined_context for ind in indicator):
                return True
        
        # Check if it's part of a longer alphanumeric string
        if context_before and context_before[-1].isalnum() and not context_before[-1].isspace():
            if address[0].isalnum():
                # Exception for addresses that commonly appear after colons or equals
                if context_before[-1] not in ':=':
                    return True
        
        if context_after and context_after[0].isalnum() and not context_after[0].isspace():
            if address[-1].isalnum():
                # Exception for Stellar addresses with memo format
                if not (address.startswith('G') and context_after.startswith(':::ucl:::')):
                    return True
        
        return False