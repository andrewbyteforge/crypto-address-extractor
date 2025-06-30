"""
Debug script to test Cardano address detection
"""

import re

# Test address
test_address = "addr1vy6mgq7gs3cmv2ryk26h5qr8tckvvqjwmspvrude98csyxgms6ktr"
print(f"Testing address: {test_address}")
print(f"Length: {len(test_address)}")

# Test patterns
patterns = [
    re.compile(r'\baddr1[a-z0-9]{58,104}\b'),
    re.compile(r'addr1[a-z0-9]{58,104}'),
    re.compile(r'\baddr1[a-z0-9]+\b'),
    re.compile(r'addr1[a-z0-9]+'),
]

# Test each pattern
for i, pattern in enumerate(patterns):
    match = pattern.search(test_address)
    if match:
        print(f"Pattern {i+1} MATCHED: {match.group()}")
    else:
        print(f"Pattern {i+1} did not match")

# Test with sample text
sample_texts = [
    test_address,
    f" {test_address} ",
    f"address:{test_address}",
    f"wallet={test_address}",
    f"The address is {test_address} in the data"
]

print("\nTesting in different contexts:")
for text in sample_texts:
    for i, pattern in enumerate(patterns):
        if pattern.search(text):
            print(f"Pattern {i+1} found in: {text[:30]}...")
            break
    else:
        print(f"NO MATCH in: {text[:30]}...")

# Check character set
print(f"\nCharacters in address:")
chars = set(test_address[5:])  # Skip 'addr1'
print(f"Unique chars: {sorted(chars)}")
print(f"All lowercase letters/numbers? {all(c in 'abcdefghijklmnopqrstuvwxyz0123456789' for c in test_address[5:])}")