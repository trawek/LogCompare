# Log Comparison Tool - Deployment Guide

## Sposoby uruchamiania aplikacji lokalnie

### 1. 🚀 Uruchamianie w trybie deweloperskim (Zalecane)

#### Wymagania:
- Node.js (wersja 18 lub nowsza)
- npm lub yarn

#### Kroki:
```bash
# 1. Sklonuj lub pobierz projekt
cd log-comparison-tool

# 2. Zainstaluj zależności
npm install

# 3. Uruchom aplikację
npm run dev

# 4. Otwórz przeglądarkę i przejdź do:
http://localhost:3000
```

### 2. 📦 Budowanie statycznej wersji HTML

#### Konfiguracja dla statycznego eksportu:
```bash
# 1. Zbuduj aplikację
npm run build

# 2. Eksportuj do statycznych plików
npm run export

# 3. Pliki HTML będą w folderze 'out/'
# Otwórz plik out/index.html w przeglądarce
```

### 3. 🖥️ Tworzenie aplikacji desktopowej (Electron)

#### Instalacja Electron:
```bash
# Zainstaluj Electron
npm install --save-dev electron electron-builder

# Uruchom jako aplikacja desktopowa
npm run electron

# Zbuduj plik .exe
npm run build:electron
```

### 4. 🌐 Uruchamianie na serwerze lokalnym

#### Opcja A - Używając Python:
```bash
# W folderze 'out/' po eksporcie
python -m http.server 8000
# Otwórz: http://localhost:8000
```

#### Opcja B - Używając Node.js:
```bash
npx serve out/
# Otwórz podany adres
```

### 5. 📱 Portable HTML (Pojedynczy plik)

Dla maksymalnej przenośności, można utworzyć pojedynczy plik HTML ze wszystkimi zasobami:

```bash
npm run build:portable
```

## Instrukcje szczegółowe

### Dla użytkowników bez doświadczenia technicznego:

1. **Pobierz Node.js** z https://nodejs.org
2. **Pobierz projekt** jako ZIP i rozpakuj
3. **Otwórz terminal/wiersz poleceń** w folderze projektu
4. **Wpisz komendy** jedna po drugiej:
   ```
   npm install
   npm run dev
   ```
5. **Otwórz przeglądarkę** i wejdź na http://localhost:3000

### Rozwiązywanie problemów:

- **Błąd "npm not found"**: Zainstaluj Node.js
- **Port zajęty**: Zmień port w package.json lub użyj `npm run dev -- --port 3001`
- **Błędy zależności**: Usuń folder `node_modules` i uruchom `npm install` ponownie

## Funkcje aplikacji:

✅ **Tryb pojedynczego pliku** - porównanie dwóch plików log
✅ **Tryb wsadowy** - porównanie całego katalogu z plikami
✅ **Wykresy i wizualizacje** - analiza graficzna różnic
✅ **Eksport wyników** - możliwość zapisania porównań
✅ **Responsywny design** - działa na wszystkich urządzeniach

## Wsparcie techniczne:

W przypadku problemów z uruchomieniem, sprawdź:
1. Czy Node.js jest zainstalowany (`node --version`)
2. Czy wszystkie zależności są zainstalowane (`npm list`)
3. Czy port 3000 nie jest zajęty przez inną aplikację
