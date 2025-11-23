# Log Comparator

Aplikacja do porównywania logów z urządzeń sieciowych (Pre-Check vs Post-Check). Generuje czytelne raporty HTML/PDF z podświetlonymi różnicami.

## Wymagania

*   Python 3.8+
*   Zalecane utworzenie wirtualnego środowiska (venv)

## Instalacja

1.  Sklonuj repozytorium lub pobierz pliki.
2.  Zainstaluj wymagane biblioteki:

```bash
pip install -r requirements.txt
```

## Uruchomienie

### Tryb Graficzny (GUI)
To domyślny i zalecany tryb pracy.

```bash
python main.py --gui
```
lub po prostu (jeśli nie podasz argumentów):
```bash
python main.py
```

### Tryb Wiersza Poleceń (CLI)
Możesz wygenerować raport automatycznie, podając ścieżki do folderów.

```bash
python main.py [katalog_z_logami] [katalog_wyjsciowy]
```

Opcjonalne flagi:
*   `--format`: Format raportu (`html`, `pdf`, `json`). Domyślnie: `html`.
*   `--lang`: Język raportu (`pl`, `en`, `de`, etc.). Domyślnie: `pl`.

Przykład:
```bash
python main.py C:\logs\cisco C:\reports --format pdf --lang en
```

## Funkcje
*   **Porównywanie linia do linii**: Precyzyjne wykrywanie zmian, dodań i usunięć.
*   **Ignorowanie szumu**: (Planowane) Możliwość filtrowania dat i zmiennych wartości.
*   **Wielowątkowość**: Szybkie przetwarzanie wielu plików jednocześnie.
*   **Eksport**: Raporty w HTML (interaktywne), PDF (do druku) i JSON (do integracji).
