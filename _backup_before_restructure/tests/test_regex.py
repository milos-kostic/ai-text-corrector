import re

# Tvoj pattern
compound_fixes = {
    'i and i was': 'i and i were',
    'he and i was': 'he and i were',
}

pattern = re.compile(
    r'\b(' + '|'.join(map(re.escape, compound_fixes.keys())) + r')\b',
    re.IGNORECASE
)

# Test cases
tests = [
    "I and I was there",
    "He and I was late",
    "i and i was there",
]

for test in tests:
    matches = pattern.findall(test)
    print(f"Text: '{test}'")
    print(f"Matches: {matches}")
    print()