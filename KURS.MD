# Kompletny Kurs: Budowa Przedstawiciela Handlowego z OpenAI Agents SDK

## Wprowadzenie

Witaj w kompleksowym kursie budowy systemu wieloagentowego z wykorzystaniem **OpenAI Agents SDK**! W tym artykule krok po kroku nauczysz się, jak stworzyć inteligentnego przedstawiciela handlowego, który potrafi generować i wysyłać wiadomości e-mail w różnych stylach komunikacji.

### Czego się nauczysz?

Po ukończeniu tego kursu będziesz potrafił:

- ✅ Tworzyć i konfigurować agentów AI z różnymi "osobowościami"
- ✅ Używać narzędzi (Tools) do integracji funkcji z agentami
- ✅ Implementować przekazywanie kontroli (Handoffs) między agentami
- ✅ Budować hierarchiczne systemy wieloagentowe
- ✅ Wykorzystywać asynchroniczne programowanie w Pythonie do równoległego uruchamiania agentów
- ✅ Integrować zewnętrzne API (SendGrid) z systemem agentowym

### Wymagania wstępne

- Podstawowa znajomość Pythona (funkcje, klasy, importy)
- Podstawowa znajomość programowania asynchronicznego (async/await) - wyjaśnimy to w trakcie kursu
- Konto OpenAI z dostępem do API
- Konto SendGrid (darmowe) do wysyłki e-maili

---

## Część 1: Przygotowanie środowiska

### Krok 1.1: Instalacja zależności

Zacznijmy od przygotowania środowiska. Utwórz nowy katalog projektu i zainstaluj wymagane pakiety:

```bash
pip install openai-agents python-dotenv sendgrid
```

Lub użyj pliku `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Krok 1.2: Konfiguracja SendGrid

SendGrid to platforma do wysyłki transakcyjnych wiadomości e-mail. Będziemy jej używać jako narzędzia świata rzeczywistego, które nasi agenci będą mogli wykorzystywać.

#### Krok 1.2.1: Utworzenie konta SendGrid

1. Odwiedź [https://sendgrid.com/](https://sendgrid.com/)
2. Utwórz darmowe konto
3. Po zalogowaniu przejdź do: **Settings** → **API Keys** → **Create API Key**
4. Skopiuj wygenerowany klucz API

#### Krok 1.2.2: Weryfikacja nadawcy

Aby SendGrid mógł wysyłać e-maile w Twoim imieniu, musisz zweryfikować adres nadawcy:

1. Przejdź do: **Settings** → **Sender Authentication** → **Verify a Single Sender**
2. Podaj swój adres e-mail i zweryfikuj go

#### Krok 1.2.3: Konfiguracja zmiennych środowiskowych

Utwórz plik `.env` w katalogu głównym projektu:

```env
SENDGRID_API_KEY=twój_klucz_api_tutaj
FROM_EMAIL=twój_zweryfikowany_email@example.com
TO_EMAIL=adres_odbiorcy@example.com
OPENAI_API_KEY=twój_klucz_openai_tutaj
```

**⚠️ Ważne:** Plik `.env` zawiera wrażliwe dane - nigdy nie commituj go do repozytorium Git!

### Krok 1.3: Test konfiguracji

Stwórzmy prostą funkcję testową, aby sprawdzić, czy wszystko działa:

```python
import os
import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Content, Email, Mail, To

load_dotenv()

def send_test_email():
    """Wysyła testowy e-mail, aby zweryfikować konfigurację SendGrid"""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(os.environ.get("FROM_EMAIL"))
    to_email = To(os.environ.get("TO_EMAIL"))
    content = Content("text/plain", "To jest ważny testowy e-mail")
    mail = Mail(from_email, to_email, "Test e-mail", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"Status odpowiedzi: {response.status_code}")
    if response.status_code == 202:
        print("✅ E-mail wysłany pomyślnie!")

send_test_email()
```

Jeśli otrzymasz status `202`, oznacza to, że konfiguracja działa poprawnie! Sprawdź swoją skrzynkę odbiorczą.

---

## Część 2: Podstawy OpenAI Agents SDK

### Czym jest OpenAI Agents SDK?

**OpenAI Agents SDK** to framework, który upraszcza tworzenie systemów wieloagentowych. Zamiast ręcznie pisać JSON Schema i obsługiwać wywołania funkcji, framework automatycznie:

- Generuje schematy JSON z metadanych Pythona
- Zarządza przepływem pracy między agentami
- Obsługuje asynchroniczne wywołania
- Umożliwia śledzenie (tracing) działań agentów

### Kluczowe komponenty

#### 1. Agent

`Agent` to podstawowa jednostka w systemie. Reprezentuje inteligentnego asystenta z określonymi instrukcjami i możliwościami.

```python
from agents import Agent

agent = Agent(
    name="Mój Agent",
    instructions="Jesteś pomocnym asystentem...",
    model="gpt-4o-mini"
)
```

**Parametry:**
- `name`: Nazwa agenta (używana w śledzeniu)
- `instructions`: Monit systemowy określający zachowanie agenta
- `model`: Model LLM do użycia (np. "gpt-4o-mini", "gpt-4o")

#### 2. Runner

`Runner` zarządza wykonywaniem agentów. Umożliwia uruchamianie agentów synchronicznie lub asynchronicznie.

```python
from agents import Runner

# Synchroniczne uruchomienie
result = await Runner.run(agent, "Twoja wiadomość")

# Strumieniowe uruchomienie (dla UI)
result = Runner.run_streamed(agent, input="Twoja wiadomość")
```

#### 3. Trace

`trace` to kontekstowy menedżer do śledzenia działań agentów. Wszystkie operacje wewnątrz bloku `with trace(...)` są automatycznie logowane na platformie OpenAI.

```python
from agents import trace

with trace("Nazwa operacji"):
    result = await Runner.run(agent, "Wiadomość")
```

---

## Część 3: Tworzenie pierwszych agentów

### Krok 3.1: Definicja agentów sprzedaży

Zacznijmy od stworzenia trzech agentów sprzedaży, z których każdy ma inną "osobowość":

```python
from agents import Agent

# Instrukcje dla agenta profesjonalnego
instructions_professional = (
    "Jesteś agentem sprzedaży pracującym dla ComplAI, "
    "firmy oferującej narzędzie SaaS do zapewnienia zgodności SOC2 i przygotowania do audytów, "
    "napędzane przez AI. Piszesz profesjonalne, poważne e-maile sprzedażowe."
)

# Instrukcje dla agenta angażującego
instructions_engaging = (
    "Jesteś dowcipnym, angażującym agentem sprzedaży pracującym dla ComplAI, "
    "firmy oferującej narzędzie SaaS do zapewnienia zgodności SOC2 i przygotowania do audytów, "
    "napędzane przez AI. Piszesz dowcipne, angażujące e-maile sprzedażowe, które prawdopodobnie otrzymają odpowiedź."
)

# Instrukcje dla agenta zwięzłego
instructions_concise = (
    "Jesteś zajętym agentem sprzedaży pracującym dla ComplAI, "
    "firmy oferującej narzędzie SaaS do zapewnienia zgodności SOC2 i przygotowania do audytów, "
    "napędzane przez AI. Piszesz zwięzłe, rzeczowe e-maile sprzedażowe."
)

# Tworzenie agentów
sales_agent1 = Agent(
    name="Profesjonalny Agent Sprzedaży",
    instructions=instructions_professional,
    model="gpt-4o-mini"
)

sales_agent2 = Agent(
    name="Angażujący Agent Sprzedaży",
    instructions=instructions_engaging,
    model="gpt-4o-mini"
)

sales_agent3 = Agent(
    name="Zajęty Agent Sprzedaży",
    instructions=instructions_concise,
    model="gpt-4o-mini"
)
```

### Dlaczego instrukcje są ważne?

**Instrukcje (monity systemowe)** to kluczowy element definiujący zachowanie agenta. Określają one:

- **Kontekst**: W jakiej sytuacji agent działa
- **Ton**: Jak agent komunikuje się
- **Zachowanie**: Co agent powinien robić

Różne instrukcje prowadzą do różnych stylów odpowiedzi, co jest kluczowe w systemach wieloagentowych, gdzie chcemy mieć różnorodność.

### Krok 3.2: Testowanie pojedynczego agenta

Przetestujmy jednego z agentów:

```python
from agents import Runner

message = "Napisz zimny e-mail sprzedażowy"
result = await Runner.run(sales_agent1, message)
print(result.final_output)
```

### Krok 3.3: Strumieniowanie odpowiedzi (Streaming)

Dla lepszego doświadczenia użytkownika możemy wyświetlać odpowiedź fragment po fragmencie:

```python
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

result = Runner.run_streamed(sales_agent1, input="Napisz zimny e-mail sprzedażowy")

async for event in result.stream_events():
    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
        print(event.data.delta, end="", flush=True)
```

**Różnica między `run` a `run_streamed`:**
- `run`: Czeka na całą odpowiedź, zwraca wynik po zakończeniu
- `run_streamed`: Wyświetla odpowiedź na bieżąco, fragment po fragmencie (idealne dla UI)

---

## Część 4: Programowanie asynchroniczne i równoległe wywołania

### Wprowadzenie do asyncio

**Asyncio** to biblioteka Pythona do programowania asynchronicznego. Pozwala na wykonywanie wielu operacji jednocześnie, co jest szczególnie przydatne, gdy operacje czekają na odpowiedzi z sieci (np. wywołania API).

### Kluczowe koncepcje

#### 1. Funkcje asynchroniczne (async def)

Funkcja oznaczona jako `async def` może być wstrzymana (suspended) i wznowiona później:

```python
async def moja_funkcja():
    # Ta funkcja może czekać na operacje I/O bez blokowania całego programu
    await jakas_operacja()
```

#### 2. Await

Słowo kluczowe `await` wstrzymuje wykonanie funkcji do czasu zakończenia operacji:

```python
result = await Runner.run(agent, "Wiadomość")
# Kod poniżej wykona się dopiero po zakończeniu Runner.run
```

#### 3. asyncio.gather

`asyncio.gather` pozwala uruchomić wiele operacji asynchronicznych równolegle:

```python
import asyncio

# Wszystkie trzy operacje uruchomią się jednocześnie
results = await asyncio.gather(
    Runner.run(agent1, message),
    Runner.run(agent2, message),
    Runner.run(agent3, message)
)
```

### Krok 4.1: Równoległe generowanie e-maili

Zamiast czekać na każdy e-mail osobno, możemy wygenerować wszystkie trzy jednocześnie:

```python
import asyncio
from agents import Runner, trace

async def generate_parallel_emails(agent1, agent2, agent3, message):
    """Generuje trzy różne e-maile równolegle"""
    with trace("Równoległe e-maile sprzedażowe"):
        results = await asyncio.gather(
            Runner.run(agent1, message),
            Runner.run(agent2, message),
            Runner.run(agent3, message),
        )
    
    outputs = [result.final_output for result in results]
    return outputs

# Użycie
message = "Napisz zimny e-mail sprzedażowy"
emails = await generate_parallel_emails(sales_agent1, sales_agent2, sales_agent3, message)

for i, email in enumerate(emails, 1):
    print(f"\n--- E-mail {i} ---\n{email}\n")
```

**Korzyści:**
- **Oszczędność czasu**: Zamiast 3 × czas_pojedynczego_wywołania, otrzymujemy maksymalny czas z trzech wywołań
- **Lepsze wykorzystanie zasobów**: Gdy jeden agent czeka na odpowiedź API, pętla zdarzeń przełącza się na innego

### Krok 4.2: Wybór najlepszego e-maila

Stwórzmy agenta, który wybierze najlepszy e-mail z trzech wygenerowanych:

```python
from agents import Agent, Runner, trace

# Agent wybierający
sales_picker = Agent(
    name="Wybór e-maila",
    instructions=(
        "Wybierasz najlepszy zimny e-mail sprzedażowy z podanych opcji. "
        "Wyobraź sobie, że jesteś klientem i wybierz ten, na który najprawdopodobniej odpowiesz. "
        "Nie podawaj wyjaśnienia; odpowiedz tylko wybranym e-mailem."
    ),
    model="gpt-4o-mini",
)

async def select_best_email(agent1, agent2, agent3, picker_agent, message):
    """Generuje trzy warianty i wybiera najlepszy"""
    with trace("Wybór z agentów sprzedaży"):
        # Krok 1: Generowanie trzech wariantów równolegle
        results = await asyncio.gather(
            Runner.run(agent1, message),
            Runner.run(agent2, message),
            Runner.run(agent3, message),
        )
        outputs = [result.final_output for result in results]
        
        # Krok 2: Przygotowanie wiadomości dla agenta wybierającego
        emails = "Zimne e-maile sprzedażowe:\n\n" + "\n\nE-mail:\n\n".join(outputs)
        
        # Krok 3: Wybór najlepszego e-maila
        best = await Runner.run(picker_agent, emails)
        
        return best.final_output

# Użycie
best_email = await select_best_email(
    sales_agent1, sales_agent2, sales_agent3, sales_picker, 
    "Napisz zimny e-mail sprzedażowy"
)
print(f"Najlepszy e-mail:\n{best_email}")
```

---

## Część 5: Narzędzia (Tools) - Integracja funkcji z agentami

### Czym są narzędzia?

**Narzędzia (Tools)** to funkcje, które agenci mogą wywoływać podczas swojej pracy. Pozwalają one agentom na interakcję ze światem zewnętrznym - wysyłanie e-maili, pobieranie danych, wykonywanie obliczeń itp.

### Problem: Ręczne tworzenie JSON Schema

W tradycyjnym podejściu musielibyśmy ręcznie tworzyć JSON Schema dla każdej funkcji:

```python
# Tradycyjne podejście (nie używamy tego w OpenAI Agents SDK)
tool_schema = {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Wysyła e-mail z podaną treścią",
        "parameters": {
            "type": "object",
            "properties": {
                "body": {
                    "type": "string",
                    "description": "Treść wiadomości e-mail"
                }
            },
            "required": ["body"]
        }
    }
}
```

To jest żmudne i podatne na błędy!

### Rozwiązanie: Dekorator @function_tool

OpenAI Agents SDK automatycznie generuje JSON Schema z metadanych Pythona:

```python
from agents import function_tool

@function_tool
def send_email(body: str) -> dict:
    """
    Wysyła e-mail z podaną treścią do wszystkich potencjalnych klientów.
    
    Args:
        body: Treść wiadomości e-mail do wysłania
    
    Returns:
        Słownik ze statusem operacji
    """
    # Implementacja funkcji
    return {"status": "success"}
```

**Co framework robi automatycznie:**
1. **Generuje nazwę narzędzia** z nazwy funkcji (`send_email`)
2. **Tworzy opis** z docstringa (komentarz w potrójnych cudzysłowach)
3. **Generuje JSON Schema** z type hints (`body: str` → parametr typu string)

### Krok 5.1: Implementacja narzędzia do wysyłki e-maili

```python
import os
import sendgrid
from agents import function_tool
from sendgrid.helpers.mail import Content, Email, Mail, To

@function_tool
def send_email(body: str) -> dict:
    """
    Wysyła e-mail z podaną treścią do wszystkich potencjalnych klientów.
    """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(os.environ.get("FROM_EMAIL"))
    to_email = To(os.environ.get("TO_EMAIL"))
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "E-mail sprzedażowy", content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}
```

**Kluczowe elementy:**
- `@function_tool`: Dekorator konwertujący funkcję na narzędzie
- `body: str`: Type hint określający typ parametru
- Docstring: Opis funkcji używany jako opis narzędzia dla LLM

### Krok 5.2: Użycie narzędzia przez agenta

Aby agent mógł używać narzędzia, musimy przekazać je podczas tworzenia agenta:

```python
from agents import Agent, Runner, trace

# Tworzenie agenta z narzędziem
sales_manager = Agent(
    name="Kierownik Sprzedaży",
    instructions="""
    Jesteś Kierownikiem Sprzedaży w ComplAI. Twoim celem jest znalezienie najlepszego 
    zimnego e-maila sprzedażowego używając narzędzi agentów sprzedaży.
    
    Postępuj zgodnie z tymi krokami:
    1. Generowanie wersji: Użyj wszystkich trzech narzędzi agentów sprzedaży, 
       aby wygenerować trzy różne wersje e-maili. Nie przechodź dalej, 
       dopóki wszystkie trzy wersje nie będą gotowe.
    
    2. Ocena i wybór: Przejrzyj wersje i wybierz najlepszy e-mail używając 
       swojej oceny, który jest najbardziej skuteczny.
    
    3. Użyj narzędzia send_email, aby wysłać najlepszy e-mail (i tylko najlepszy).
    
    Kluczowe zasady:
    - Musisz używać narzędzi agentów sprzedaży do generowania wersji — nie pisz ich sam.
    - Musisz wysłać JEDEN e-mail używając narzędzia send_email — nigdy więcej niż jeden.
    """,
    tools=[send_email],  # Przekazanie narzędzia
    model="gpt-4o-mini",
)

# Uruchomienie agenta
message = "Wyślij zimny e-mail sprzedażowy adresowany do 'Drogi CEO'"

with trace("Kierownik sprzedaży"):
    result = await Runner.run(sales_manager, message)
```

**Co się dzieje:**
1. Agent otrzymuje wiadomość
2. Agent decyduje, że potrzebuje wygenerować e-mail
3. Agent wywołuje narzędzie `send_email` z wygenerowaną treścią
4. Framework wykonuje funkcję `send_email`
5. Agent otrzymuje wynik i kontynuuje pracę

---

## Część 6: Agent jako Narzędzie (Agent as a Tool)

### Koncepcja "Agent jako Narzędzie"

**Agent jako Narzędzie** to technika opakowywania agenta w narzędzie, które może być używane przez innego agenta. Pozwala to na budowanie hierarchicznych systemów, gdzie "agent planista" (Manager) koordynuje pracę "agentów wykonawczych" (Sales Agents).

### Różnica między zwykłym narzędziem a agentem jako narzędziem

| Typ | Opis | Kiedy używać |
|-----|------|--------------|
| **Zwykłe narzędzie** | Funkcja Pythona z `@function_tool` | Proste operacje (wysyłka e-maila, obliczenia) |
| **Agent jako narzędzie** | Agent opakowany w narzędzie | Złożone zadania wymagające rozumowania LLM |

### Krok 6.1: Konwersja agenta na narzędzie

```python
from agents import Agent

# Tworzenie agentów sprzedaży
sales_agent1 = Agent(
    name="Profesjonalny Agent Sprzedaży",
    instructions=instructions_professional,
    model="gpt-4o-mini"
)

# Konwersja agenta na narzędzie
tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1",
    tool_description="Napisz profesjonalny zimny e-mail sprzedażowy"
)

# Teraz tool1 może być użyte przez innego agenta!
```

**Co się dzieje:**
1. Metoda `as_tool()` tworzy narzędzie z agenta
2. Gdy narzędzie jest wywoływane, framework faktycznie uruchamia agenta z jego instrukcjami
3. Wynik działania agenta jest zwracany jako wynik narzędzia

### Krok 6.2: Tworzenie hierarchii narzędzi

Stwórzmy zestaw narzędzi składający się z agentów i funkcji:

```python
def create_sales_agent_tools(agent1, agent2, agent3):
    """Konwertuje agentów sprzedaży na narzędzia"""
    description = "Napisz zimny e-mail sprzedażowy"
    
    tool1 = agent1.as_tool(tool_name="sales_agent1", tool_description=description)
    tool2 = agent2.as_tool(tool_name="sales_agent2", tool_description=description)
    tool3 = agent3.as_tool(tool_name="sales_agent3", tool_description=description)
    
    return [tool1, tool2, tool3]

# Tworzenie narzędzi
sales_tools = create_sales_agent_tools(sales_agent1, sales_agent2, sales_agent3)
sales_tools.append(send_email)  # Dodanie narzędzia do wysyłki

# Teraz mamy 4 narzędzia: 3 agenty + 1 funkcja
```

### Krok 6.3: Agent kierownik z narzędziami

Stwórzmy agenta kierownika, który używa wszystkich narzędzi:

```python
from agents import Agent, Runner, trace

def create_sales_manager_with_tools(sales_tools):
    """Tworzy agenta kierownika sprzedaży z narzędziami"""
    instructions = """
    Jesteś Kierownikiem Sprzedaży w ComplAI. Twoim celem jest znalezienie 
    najlepszego zimnego e-maila sprzedażowego używając narzędzi agentów sprzedaży.
    
    Postępuj zgodnie z tymi krokami:
    1. Generowanie wersji: Użyj wszystkich trzech narzędzi agentów sprzedaży, 
       aby wygenerować trzy różne wersje e-maili. Nie przechodź dalej, 
       dopóki wszystkie trzy wersje nie będą gotowe.
    
    2. Ocena i wybór: Przejrzyj wersje i wybierz najlepszy e-mail używając 
       swojej oceny, który jest najbardziej skuteczny.
    
    3. Użyj narzędzia send_email, aby wysłać najlepszy e-mail (i tylko najlepszy).
    
    Kluczowe zasady:
    - Musisz używać narzędzi agentów sprzedaży do generowania wersji — nie pisz ich sam.
    - Musisz wysłać JEDEN e-mail używając narzędzia send_email — nigdy więcej niż jeden.
    """
    
    return Agent(
        name="Kierownik Sprzedaży",
        instructions=instructions,
        tools=sales_tools,  # Wszystkie narzędzia
        model="gpt-4o-mini",
    )

# Użycie
sales_manager = create_sales_manager_with_tools(sales_tools)

message = "Wyślij zimny e-mail sprzedażowy adresowany do 'Drogi CEO'"

with trace("Kierownik sprzedaży"):
    result = await Runner.run(sales_manager, message)
```

**Przepływ działania:**
1. Agent kierownik otrzymuje wiadomość
2. Agent kierownik wywołuje `sales_agent1` (narzędzie) → otrzymuje e-mail 1
3. Agent kierownik wywołuje `sales_agent2` (narzędzie) → otrzymuje e-mail 2
4. Agent kierownik wywołuje `sales_agent3` (narzędzie) → otrzymuje e-mail 3
5. Agent kierownik ocenia wszystkie trzy i wybiera najlepszy
6. Agent kierownik wywołuje `send_email` (narzędzie) z najlepszym e-mailem

**Kluczowa różnica:** W tym przypadku to **LLM (agent kierownik) sam decyduje**, które narzędzie i kiedy wywołać. To przejście od "przepływu pracy" (gdzie programista określa kolejność) do "orkiestracji agentowej" (gdzie agent sam zarządza procesem).

---

## Część 7: Handoffs - Przekazywanie kontroli między agentami

### Czym są Handoffs?

**Handoffs (Przekazania)** to mechanizm delegowania odpowiedzialności, gdzie agent przekazuje całe zadanie innemu, bardziej wyspecjalizowanemu agentowi. W przeciwieństwie do narzędzi, gdzie kontrola wraca do głównego agenta, w handoff kontrolę przejmuje drugi agent i kończy zadanie.

### Porównanie: Tools vs Handoffs

| Cecha | Narzędzia (Tools) | Przekazania (Handoffs) |
|------|-------------------|------------------------|
| **Przepływ kontroli** | Dwukierunkowy: Agent → Narzędzie → Agent | Jednokierunkowy: Agent → Agent (kontrola nie wraca) |
| **Użycie** | Małe, modułowe kroki w większym planie | Przekazanie złożonego, specjalistycznego zadania |
| **Przykład** | "Wygeneruj wariant A", "Wygeneruj wariant B" | "Przekazuję to do agenta mailującego, który zajmie się resztą" |

### Krok 7.1: Tworzenie agentów do formatowania e-maili

Stwórzmy agentów odpowiedzialnych za formatowanie i wysyłkę e-maili:

```python
from agents import Agent, function_tool

# Agent do pisania tematów
subject_writer = Agent(
    name="Pisarz tematów e-maili",
    instructions=(
        "Potrafisz napisać temat dla zimnego e-maila sprzedażowego. "
        "Otrzymujesz wiadomość i musisz napisać temat e-maila, który prawdopodobnie otrzyma odpowiedź."
    ),
    model="gpt-4o-mini",
)

# Agent do konwersji na HTML
html_converter = Agent(
    name="Konwerter treści e-maila na HTML",
    instructions=(
        "Potrafisz przekonwertować treść e-maila tekstowego na treść HTML. "
        "Otrzymujesz treść tekstową, która może zawierać markdown, "
        "i musisz przekonwertować ją na treść HTML z prostym, przejrzystym, przekonującym układem i designem."
    ),
    model="gpt-4o-mini",
)

# Konwersja agentów na narzędzia
subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Napisz temat dla zimnego e-maila sprzedażowego",
)

html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Przekonwertuj treść e-maila tekstowego na treść HTML",
)

# Narzędzie do wysyłki HTML
@function_tool
def send_html_email(subject: str, html_body: str) -> dict:
    """Wysyła e-mail z podanym tematem i treścią HTML"""
    # Implementacja wysyłki HTML (podobna do send_email)
    return {"status": "success"}
```

### Krok 7.2: Tworzenie agenta zarządzającego e-mailami

Stwórzmy agenta, który będzie celem przekazania (handoff):

```python
from agents import Agent

def create_email_manager_agent():
    """Tworzy agenta zarządzającego formatowaniem i wysyłką e-maili"""
    # Lista narzędzi dla agenta zarządzającego
    tools = [subject_tool, html_tool, send_html_email]
    
    instructions = (
        "Jesteś formatowaczem i nadawcą e-maili. Otrzymujesz treść e-maila do wysłania. "
        "Najpierw użyj narzędzia subject_writer, aby napisać temat e-maila, "
        "następnie użyj narzędzia html_converter, aby przekonwertować treść na HTML. "
        "Na końcu użyj narzędzia send_html_email, aby wysłać e-mail z tematem i treścią HTML."
    )
    
    return Agent(
        name="Menedżer E-maili",
        instructions=instructions,
        tools=tools,
        model="gpt-4o-mini",
        handoff_description="Przekonwertuj e-mail na HTML i wyślij go",  # Kluczowe!
    )

email_manager = create_email_manager_agent()
```

**Kluczowy element:** `handoff_description` - opis, który pozwala innemu agentowi zdecydować, że ten agent jest idealnym celem przekazania kontroli.

### Krok 7.3: Agent kierownik z handoff

Teraz stwórzmy agenta kierownika, który używa handoff:

```python
from agents import Agent, Runner, trace

def create_sales_manager_with_handoff(sales_tools, email_manager):
    """Tworzy agenta kierownika z możliwością przekazania kontroli"""
    instructions = """
    Jesteś Kierownikiem Sprzedaży w ComplAI. Twoim celem jest znalezienie 
    najlepszego zimnego e-maila sprzedażowego używając narzędzi agentów sprzedaży.
    
    Postępuj zgodnie z tymi krokami:
    1. Generowanie wersji: Użyj wszystkich trzech narzędzi agentów sprzedaży, 
       aby wygenerować trzy różne wersje e-maili. Nie przechodź dalej, 
       dopóki wszystkie trzy wersje nie będą gotowe.
    
    2. Ocena i wybór: Przejrzyj wersje i wybierz najlepszy e-mail używając 
       swojej oceny, który jest najbardziej skuteczny. Możesz używać narzędzi 
       wielokrotnie, jeśli nie jesteś zadowolony z wyników z pierwszego podejścia.
    
    3. Przekazanie do wysyłki: Przekaż TYLKO zwycięską wersję e-maila agentowi 
       'Menedżer E-maili'. Menedżer E-maili zajmie się formatowaniem i wysyłką.
    
    Kluczowe zasady:
    - Musisz używać narzędzi agentów sprzedaży do generowania wersji — nie pisz ich sam.
    - Musisz przekazać dokładnie JEDEN e-mail Menedżerowi E-maili — nigdy więcej niż jeden.
    """
    
    return Agent(
        name="Kierownik Sprzedaży",
        instructions=instructions,
        tools=sales_tools,  # Narzędzia do generowania
        handoffs=[email_manager],  # Przekazanie do formatowania i wysyłki
        model="gpt-4o-mini",
    )

# Użycie
sales_manager = create_sales_manager_with_handoff(sales_tools, email_manager)

message = "Wyślij zimny e-mail sprzedażowy adresowany do Drogi CEO od Alicji"

with trace("Zautomatyzowany SDR"):
    result = await Runner.run(sales_manager, message)
```

**Przepływ działania z handoff:**
1. Agent kierownik generuje 3 e-maile (używając Tools) → kontrola wraca
2. Agent kierownik wybiera najlepszy
3. Agent kierownik **przekazuje kontrolę** (Handoff) agentowi Menedżer E-maili
4. **Kontrola NIE WRACA** do kierownika
5. Menedżer E-maili używa swoich narzędzi: Temat → Konwersja HTML → Wysyłka

**Różnica w śledzeniu (trace):**
- **Narzędzia**: Na początku śladu kierownik wywołuje agentów sprzedaży, kontrola wraca
- **Przekazanie**: Pod koniec śladu kierownik przekazuje kontrolę, cała późniejsza aktywność jest realizowana przez Menedżera E-maili

---

## Część 8: Wzorce projektowe agentów

### Wzorzec 1: Wariacje + Wybór

W tym wzorcu generujemy wiele wariantów, a następnie wybieramy najlepszy:

```python
# Generowanie wariantów
variants = await asyncio.gather(
    generate_variant_1(),
    generate_variant_2(),
    generate_variant_3(),
)

# Wybór najlepszego
best = await select_best(variants)
```

**Zastosowanie:** Generowanie treści, optymalizacja, A/B testing

### Wzorzec 2: Hierarchiczna delegacja

W tym wzorcu agent planista deleguje zadania do agentów wykonawczych:

```python
# Agent planista
manager = Agent(
    tools=[agent1_tool, agent2_tool, agent3_tool],
    handoffs=[specialist_agent]
)

# Agent specjalista
specialist = Agent(
    tools=[specialized_tools],
    handoff_description="Specjalistyczne zadanie"
)
```

**Zastosowanie:** Złożone procesy biznesowe, automatyzacja workflow

### Wzorzec 3: Pipeline z handoff

W tym wzorcu zadanie przechodzi przez sekwencję agentów:

```python
# Agent A → Agent B → Agent C
agent_a = Agent(handoffs=[agent_b])
agent_b = Agent(handoffs=[agent_c])
agent_c = Agent(tools=[final_tools])
```

**Zastosowanie:** Przetwarzanie dokumentów, analiza danych, raportowanie

---

## Część 9: Śledzenie i debugowanie

### Platforma OpenAI Traces

Wszystkie operacje wewnątrz bloku `with trace(...)` są automatycznie logowane na platformie OpenAI:

```python
with trace("Nazwa operacji"):
    result = await Runner.run(agent, message)
```

**Jak sprawdzić ślady:**
1. Odwiedź [https://platform.openai.com/traces](https://platform.openai.com/traces)
2. Zaloguj się na swoje konto OpenAI
3. Zobacz szczegółowe ślady wszystkich operacji agentów

**Co możesz zobaczyć:**
- Które narzędzia zostały wywołane
- Jakie były odpowiedzi agentów
- Przepływ kontroli między agentami
- Czas wykonania każdej operacji

### Debugowanie problemów

#### Problem: Agent nie wywołuje narzędzia

**Rozwiązanie:**
- Sprawdź, czy narzędzie jest dodane do listy `tools`
- Upewnij się, że opis narzędzia (docstring) jest jasny
- Sprawdź instrukcje agenta - czy są wystarczająco precyzyjne?

#### Problem: Błędy SSL przy wysyłce e-maili

**Rozwiązanie:**
```bash
pip install --upgrade certifi
```

```python
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
```

#### Problem: E-maile nie docierają

**Sprawdź:**
1. Folder spam w skrzynce odbiorczej
2. Status odpowiedzi SendGrid (powinien być 202)
3. Weryfikację nadawcy w SendGrid
4. Logi w SendGrid Dashboard

---

## Część 10: Zaawansowane techniki

### Dynamiczne tworzenie agentów

Możesz tworzyć agentów dynamicznie na podstawie danych:

```python
def create_agent_for_industry(industry: str) -> Agent:
    """Tworzy agenta specjalizującego się w danej branży"""
    instructions = f"""
    Jesteś agentem sprzedaży specjalizującym się w branży {industry}.
    Piszesz e-maile sprzedażowe dostosowane do specyfiki tej branży.
    """
    return Agent(
        name=f"Agent dla {industry}",
        instructions=instructions,
        model="gpt-4o-mini"
    )

# Użycie
tech_agent = create_agent_for_industry("technologia")
finance_agent = create_agent_for_industry("finanse")
```

### Warunkowe przekazania

Możesz używać logiki warunkowej do decydowania o przekazaniach:

```python
def create_smart_router() -> Agent:
    """Agent routujący, który decyduje, do którego specjalisty przekazać zadanie"""
    return Agent(
        name="Router",
        instructions="""
        Analizujesz zapytanie i decydujesz, do którego specjalisty je przekazać:
        - Jeśli dotyczy technologii → przekaż do Tech Specialist
        - Jeśli dotyczy finansów → przekaż do Finance Specialist
        - W przeciwnym razie → obsłuż sam
        """,
        handoffs=[tech_specialist, finance_specialist],
        model="gpt-4o-mini"
    )
```

### Równoległe przekazania

Możesz przekazać zadanie do wielu agentów jednocześnie:

```python
# Agent, który może przekazać do wielu specjalistów
coordinator = Agent(
    name="Koordynator",
    instructions="Przekazuj zadania do odpowiednich specjalistów",
    handoffs=[specialist1, specialist2, specialist3],
    model="gpt-4o-mini"
)
```

---

## Część 11: Najlepsze praktyki

### 1. Pisanie dobrych instrukcji

**Dobre instrukcje:**
- ✅ Są konkretne i precyzyjne
- ✅ Zawierają przykłady, gdy to możliwe
- ✅ Określają jasne kroki do wykonania
- ✅ Zawierają kluczowe zasady i ograniczenia

**Złe instrukcje:**
- ❌ Są zbyt ogólne ("Bądź pomocny")
- ❌ Są niejasne ("Zrób to dobrze")
- ❌ Brakuje kontekstu

### 2. Projektowanie narzędzi

**Dobre narzędzie:**
- ✅ Ma jasny, opisowy docstring
- ✅ Używa type hints dla parametrów
- ✅ Zwraca strukturyzowane dane (dict, list)
- ✅ Obsługuje błędy gracefully

**Przykład:**
```python
@function_tool
def get_weather(city: str) -> dict:
    """
    Pobiera aktualną pogodę dla podanego miasta.
    
    Args:
        city: Nazwa miasta (np. "Warszawa", "Kraków")
    
    Returns:
        Słownik z danymi pogodowymi: {"temperature": 20, "condition": "sunny"}
    """
    # Implementacja
    return {"temperature": 20, "condition": "sunny"}
```

### 3. Zarządzanie kosztami

**Optymalizacja kosztów:**
- Używaj `gpt-4o-mini` dla prostych zadań
- Używaj `gpt-4o` tylko dla złożonych zadań wymagających głębszego rozumowania
- Ograniczaj długość instrukcji (ale nie kosztem jakości)
- Używaj równoległych wywołań, aby skrócić czas wykonania

### 4. Obsługa błędów

Zawsze obsługuj błędy w narzędziach:

```python
@function_tool
def safe_api_call(param: str) -> dict:
    """Bezpieczne wywołanie API z obsługą błędów"""
    try:
        result = external_api.call(param)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

## Część 12: Przykłady zastosowań

### Przykład 1: Automatyzacja obsługi klienta

```python
# Agent triage - klasyfikuje zapytania
triage_agent = Agent(
    name="Triage",
    instructions="Klasyfikujesz zapytania klientów do odpowiednich kategorii",
    handoffs=[support_agent, sales_agent, technical_agent],
    model="gpt-4o-mini"
)

# Specjaliści
support_agent = Agent(
    name="Wsparcie",
    tools=[knowledge_base_tool, ticket_system_tool],
    model="gpt-4o-mini"
)
```

### Przykład 2: Automatyzacja rekrutacji

```python
# Pipeline rekrutacyjny
sourcing_agent = Agent(
    name="Sourcing",
    tools=[linkedin_tool, job_boards_tool],
    handoffs=[cv_reviewer],
    model="gpt-4o-mini"
)

cv_reviewer = Agent(
    name="Recenzent CV",
    tools=[cv_parser_tool, skills_matcher_tool],
    handoffs=[interview_scheduler],
    model="gpt-4o-mini"
)

interview_scheduler = Agent(
    name="Planista wywiadów",
    tools=[calendar_tool, email_tool],
    model="gpt-4o-mini"
)
```

### Przykład 3: Analiza i raportowanie

```python
# System analityczny
data_collector = Agent(
    name="Zbieracz danych",
    tools=[database_tool, api_tool],
    handoffs=[data_analyzer],
    model="gpt-4o-mini"
)

data_analyzer = Agent(
    name="Analityk",
    tools=[statistics_tool, visualization_tool],
    handoffs=[report_generator],
    model="gpt-4o-mini"
)

report_generator = Agent(
    name="Generator raportów",
    tools=[template_tool, pdf_generator_tool],
    model="gpt-4o-mini"
)
```

---

## Podsumowanie

### Kluczowe koncepcje

1. **Agent**: Inteligentny asystent z określonymi instrukcjami
2. **Narzędzia (Tools)**: Funkcje, które agenci mogą wywoływać
3. **Agent jako Narzędzie**: Opakowanie agenta w narzędzie dla innego agenta
4. **Przekazania (Handoffs)**: Delegowanie całego zadania innemu agentowi
5. **Asynchroniczność**: Równoległe wykonywanie operacji dla lepszej wydajności

### Różnica między przepływem pracy a orkiestracją agentową

| Przepływ pracy | Orkiestracja agentowa |
|----------------|----------------------|
| Programista określa kolejność | Agent sam decyduje o kolejności |
| `agent1 → agent2 → agent3` | Agent wybiera, które narzędzie użyć |
| Statyczny, przewidywalny | Dynamiczny, adaptacyjny |

**Przejście następuje, gdy:**
- Dodajemy narzędzia do agenta
- Dajemy agentowi instrukcje, aby sam decydował o użyciu narzędzi
- Agent otrzymuje autonomię decyzyjną

### Następne kroki

1. **Eksperymentuj**: Spróbuj różnych instrukcji i konfiguracji
2. **Rozszerzaj**: Dodaj więcej narzędzi i agentów
3. **Integruj**: Połącz z innymi systemami (CRM, bazy danych, API)
4. **Monitoruj**: Używaj śledzenia do optymalizacji
5. **Ucz się**: Analizuj ślady, aby zrozumieć, jak agenci podejmują decyzje

### Przydatne linki

- [Dokumentacja OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Platforma OpenAI Traces](https://platform.openai.com/traces)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

---

## FAQ

### P: Czy mogę używać innych modeli niż GPT-4o-mini?

**O:** Tak! Możesz używać dowolnego modelu obsługiwanego przez OpenAI API, np. `gpt-4o`, `gpt-4-turbo`. Pamiętaj jednak o różnicach w kosztach i wydajności.

### P: Jak obsłużyć błędy w narzędziach?

**O:** Zawsze używaj try-except w narzędziach i zwracaj strukturyzowane odpowiedzi z informacją o błędzie. Agent może następnie zdecydować, jak zareagować na błąd.

### P: Czy mogę mieć zagnieżdżone handoffs?

**O:** Tak! Agent A może przekazać kontrolę agentowi B, który z kolei może przekazać kontrolę agentowi C. To umożliwia budowanie złożonych pipeline'ów.

### P: Jak ograniczyć koszty?

**O:** 
- Używaj `gpt-4o-mini` dla prostych zadań
- Ograniczaj długość instrukcji
- Używaj równoległych wywołań, aby skrócić czas
- Monitoruj użycie przez śledzenie

### P: Czy mogę używać lokalnych modeli LLM?

**O:** OpenAI Agents SDK jest zaprojektowany dla modeli OpenAI. Dla lokalnych modeli możesz potrzebować innego frameworka lub własnej implementacji.

---

**Gratulacje!** Ukończyłeś kompleksowy kurs budowy systemu wieloagentowego z OpenAI Agents SDK. Masz teraz wiedzę i narzędzia, aby tworzyć zaawansowane aplikacje wykorzystujące AI.

Powodzenia w budowaniu własnych systemów agentowych! 🚀

