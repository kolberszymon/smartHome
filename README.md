# Doorime - z nami nie zapomnisz o otwartych drzwiach.

Doorime jest projektem studenckim, mającym na celu stworzenie inteligentego urządzenia.

Projekt został podzielony na mniejsze grupy w celach organizacyjnych.

### 1. Hardware
### 2. Server Side
### 3. Mobile



## Podstawowy flow aplikacji - czyli jak to w ogóle ma działać?

### Flow ze strony Aplikacji
Otwieramy aplikację → Zestawiamy tunel ssh → Logujemy się za pomocą loginu i hasła otrzymując przy tym token → Dodajemy token do requesta zapewniając bezpieczną komunikację

### Flow ze strony Urządzenia
Drzwi są otwarte → Użytkownik rozłącza się z domowym WiFi → Urządzenie stwierdza, że opuścił mieszkanie → ESP informuje o tym Raspberry → Raspberry łączy się z bazą danych postgresa na VM → Baza danych z API → API przez tunel ssh wysyła push notyfikację → Push notyfikacja przypomina użytkownikowi o otwartych drzwiach


# Postęp poszczególnych części

# Hardware
- [x] Wybór i zakup niezbędnych urządzeń
- [x] Implementacja automatycznego łączenia się ESP z siecią Wi-Fi 
- [x] Stworzenie Publishera na ESP wysyłającego informacje do Raspberry PI
- [x] Połączenie kontaktronu i implementacja jego obsługi przez ESP
- [x] Ustalenie formatu przesyłanych danych 
- [x] Napisanie testowego programu wysyłającego wiadomości na podstawie tych otrzymanych z kontaktronów
- [x] Wysyłanie do Raspberry PI konkretnych danych otrzymanych z kontaktronów 
- [x] Przetestowanie i usprawnienie funkcjonalności

# Server Side
- [x] Wybór protokołu komunikacyjnego (ESP --> Raspberry)
- [x] Przygotowanie OS na Virtual Machine i Raspberry PI 
- [x] Połączenie między Raspberry a ESP za pomocą WIFI 
- [x] Zestawienie tuneli ssh pomiędzy VM a rasp, za pośrednictwem plutona
- [x] Stworzenie bazy danych na VM z wykorzystaniem dockera
- [x] Opracowanie komunikacji pomiędzy androidem a api na VM, z wykorzystaniem tunelu ssh
- [x] Konfiguracyjny DockerFile
- [x] Stworzenie RESTful API w oparciu o Flask'a
- [x] Uwierzytelnianie do bazy danych na maszynie wirtualnej z wykorzystaniem tokenów
- [x] Połączenie API z bazą danych postgresa
- [x] Opracowanie skryptu wstawiające dane z ESP do bazy danych, bezpośrednio z raspberry pi

# Mobile 
- [x] Plan aplikacji mobilnej
- [x] Wykrycie opuszczenia domu przez użytkownika 
- [x] Implementacja notyfikiacji push z informacją o otwartch drzwiach/oknach
- [x] Implementacja tunelu na androidzie
- [x] Generowanie zapytań http do komunikacji z api
- [x] Pobranie danych użytkownika z serwera
- [x] Przetwarzanie i prezentacja danych


# Dokumentacja

Ogólna
https://github.com/kolberszymon/smartHome/blob/master/Dokumentacja%20Doorime.pdf

Api
https://github.com/kolberszymon/smartHome/blob/master/api/api_v3-dokumentacja.pdf
