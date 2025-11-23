import re

# Reguły ignorowania (Ignore Rules)
# Linie pasujące do tych wzorców będą traktowane jako identyczne podczas porównywania,
# jeśli ich "znormalizowana" forma (po usunięciu zmiennych danych) jest taka sama.
IGNORE_PATTERNS = [
    r"last login\s*:.*",
    r"# Generated.*UTC",
    r"# Finished.*UTC",
    r"Up Time\s*:.*",
    r"Temperature\s*:.*",
    r"Memory Usage\s*:.*",
]

# Reguły kolorowania składni (Syntax Highlighting)
# Kolejność ma znaczenie (najpierw ogólne, potem szczegółowe lub odwrotnie, zależnie od strategii).
# Tutaj używamy prostego słownika: Nazwa klasy CSS -> Wzorzec Regex
SYNTAX_HIGHLIGHTING = {
    "syntax-ip": r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d+)?\b",  # IPv4 + optional CIDR
    "syntax-mac": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",  # MAC Address
    "syntax-string": r'"[^"]*"',  # Tekst w cudzysłowie
    "syntax-date": r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{2,4}\b|\b\d{2}:\d{2}:\d{2}\b",  # Daty i czasy
    "syntax-error": r"(?i)\b(error|fail|failed|failure|critical|major|down|shutdown)\b",  # Błędy i stany negatywne
    "syntax-success": r"(?i)\b(success|ok|up|connected|active)\b",  # Sukcesy i stany pozytywne
    "syntax-keyword": r"(?i)\b(description|interface|port|vlan|sap|lag|service|customer|create|exit|no)\b",  # Słowa kluczowe konfiguracji
}
