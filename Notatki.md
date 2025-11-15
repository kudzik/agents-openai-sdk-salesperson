# Tydzień 2 Dzień 2

Zaczynamy od kroku przygotowawczego (SendGrid) i prostej orkiestracji agentów.

---

## 📧 Tydzień 2, Lab 2: Budowa Przedstawiciela Handlowego

### **Krok 1: Przygotowanie Narzędzia SendGrid (Wysyłka E-mail)**

Zanim agenci będą mogli wysyłać wiadomości e-mail, potrzebne jest narzędzie do **wysyłki transakcyjnych wiadomości e-mail**. SendGrid (własność Twilio) jest używany jako zewnętrzne API do tego celu.

#### **Konfiguracja SendGrid:**

1. **Konto:** Utworzenie darmowego konta SendGrid.
2. **Klucz API:** Wygenerowanie **Klucza API** w ustawieniach i zapisanie go w pliku `.env` jako zmienna środowiskowa (np. `SENDGRID_API_KEY`).
3. **Weryfikacja Nadawcy:** Zweryfikowanie własnego adresu e-mail, z którego będą wysyłane wiadomości, co jest wymogiem bezpieczeństwa dla każdej platformy e-mail (Single Sender Verification).

> 💡 **Rola w Projekcie:** SendGrid staje się **narzędziem świata rzeczywistego**, które zostanie zintegrowane z Agentem za pomocą frameworka w późniejszym kroku.

### **Krok 2: Importy i Definicja Agentów Sprzedaży**

Aby budować system wieloagentowy, definiujemy trzech agentów, z których każdy ma inną "osobowość" (monit systemowy).

#### **Wymagane Importy:**

Oprócz standardowych `Agent`, `Runner` i `trace`, importowane są:

* `FunctionTool` (klasa do definiowania narzędzi).
* Funkcje do obsługi przesyłania strumieniowego (streamingu).
* Biblioteki SendGrid do wysyłki e-maili.

#### **Definicja Agentów (Instrukcje / Monity Systemowe):**

Każdy agent jest instancją klasy `Agent` i ma inny zestaw `instructions` (monit systemowy), który określa jego charakter i ton:

1. **Agent Sprzedaży 1 (Profesjonalny):** Pisze **profesjonalne, poważne** e-maile sprzedażowe.
2. **Agent Sprzedaży 2 (Dowcipny):** Pisze **dowcipne, angażujące** e-maile, aby uzyskać odpowiedź.
3. **Agent Sprzedaży 3 (Zajęty):** Pisze **zwięzłe, rzeczowe** e-maile.

> **Ważność Instrukcji:** Instrukcje służą do **ustawienia kontekstu, nadania tonu i charakteru postaci**, co jest kluczowe dla uzyskania zróżnicowanych i realistycznych odpowiedzi w systemie wieloagentowym.

### **Krok 3: Prosty Przepływ Pracy (Streaming)**

Zamiast standardowego, blokującego wywołania `await Runner.run(...)`, używana jest metoda **`runner.run_streamed`**, aby zobaczyć, jak framework obsługuje **strumieniowanie wyników** (pojedynczy agent).

* **`runner.run_streamed`:** Ta metoda zwraca **Korutynę (Coroutine)**.
* **Współbieżność:** Zwrócona korutyna jest następnie przetwarzana przez specjalną konstrukcję `async` (często asynchroniczną pętlę `for`), która **iteruje po fragmentach odpowiedzi**, umożliwiając ich natychmiastowe wyświetlanie na ekranie.
* **Wynik:** Demonstracja pokazuje, że Agent 1 (Profesjonalny) generuje odpowiedź fragment po fragmencie, z profesjonalnym tonem, spełniając swoją zadaną rolę.

> 💡 **Kluczowa Różnica:** `run` czeka na cały wynik; `run_streamed` umożliwia szybszą, bardziej interaktywną odpowiedź, przetwarzaną na bieżąco, co jest szczególnie ważne w aplikacjach UI/UX.

---

**Świetna robota!** Mamy przygotowane narzędzie do wysyłki e-maili i zdefiniowanych agentów.

**Następnym krokiem będzie zobaczenie, jak OpenAI Agents SDK automatycznie integruje narzędzia (takie jak SendGrid) bez ręcznego tworzenia JSON Schema. Czy przechodzimy do implementacji narzędzia?**

---

## 🔗 Tydzień 2, Lab 2 (Część II): Równoległe Wywołania i Narzędzia

### **Krok 1: Równoległe Wywoływanie Agentów (`asyncio.gather`)**

W przeciwieństwie do Tygodnia 1, gdzie musieliśmy tworzyć całą pętlę obsługi, teraz frameworki agentów są naturalnie wbudowane w **`asyncio`**, co upraszcza równoległe wywołania.

1. **Potrzeba:** Aby zaoszczędzić czas, chcemy, aby **trzy różne Agenty Sprzedaży** (Profesjonalny, Angażujący, Zajęty) generowały swoje e-maile **współbieżnie**.
2. **Rozwiązanie:** Użycie **`asyncio.gather`** do zbierania korutyn zwróconych przez `Runner.run_streamed` (lub `Runner.run`).
    * $$\text{Wyniki} = \text{await asyncio.gather}(\text{Agent}_1.\text{run}(...), \text{Agent}_2.\text{run}(...), \text{Agent}_3.\text{run}(...))$$
3. **Działanie:** Pętla zdarzeń uruchamia wszystkie trzy korutyny. Gdy którykolwiek agent czeka na odpowiedź API OpenAI (czyli jest to **blokada I/O**), pętla zdarzeń przełącza się na następnego agenta. Zapewnia to, że **trzy połączenia API działają w tle** w tym samym czasie.
4. **Orkiestracja:** Po zebraniu trzech równoległych wyników, czwarty agent (`sales_picker`) jest wywoływany **sekwencyjnie**, aby wybrać najlepszą odpowiedź. Cały ten proces jest opakowany w **`with trace(...)`** dla łatwego monitorowania.

### **Krok 2: Definicja Narzędzia do Wysyłki E-mail**

Zdefiniowanie funkcji Pythona, która używa **SendGrid API** do wysyłania e-maili, jest pierwszym krokiem.

* **Funkcja:** `send_email(email_content: str)`
* **Logika:** Wewnątrz funkcja wykonuje proste żądanie API do SendGrid, używając:
  * Zweryfikowanego adresu e-mail **`from_email`**.
  * Podanych adresów **`to_emails`**.
  * Treści wiadomości **`email_content`** dostarczonej przez agenta.
* **Wynik:** Funkcja zwraca potwierdzenie sukcesu (np. `"Wysłano pomyślnie."`).

### **Krok 3: Magia Frameworka – Dekorator `FunctionTool`**

To jest najbardziej satysfakcjonująca część – eliminacja ręcznej pracy z JSON-em.

1. **Dekorator:** Umieszczamy dekorator **`@FunctionTool`** (zaimportowany z `agents`) bezpośrednio **nad funkcją `send_email`**.
2. **Działanie:** Framework OpenAI Agents SDK **automatycznie** wykonuje całą "brudną robotę":
    * **Generuje Nazwę:** Pobiera nazwę funkcji (`send_email`).
    * **Generuje Opis:** Używa **docstringa** (komentarza w cudzysłowie) z funkcji jako **opisu narzędzia**, który jest kluczowy dla LLM, aby wiedział, kiedy go użyć.
    * **Tworzy JSON Schema:** Analizuje **typowe podpowiedzi** (type hints), takie jak `email_content: str`, aby **automatycznie wygenerować cały szablon JSON Schema** (opis parametrów, typów, wymagań), który musi być wysłany do LLM.

> 💡 **Kluczowa Różnica:** W Tygodniu 1 pisaliśmy JSON-a. W Tygodniu 2 framework **czyta metadane Pythona** (nazwę, docstring, type hints) i sam **tworzy JSON-a**. Jest to **abstrakcja**, która pozwala nam zachować pełną kontrolę nad logiką Pythona, jednocześnie pozbywając się powtarzalnego kodu (boilerplate).

---

**Teraz mamy zdefiniowane narzędzie. Następnym krokiem będzie wyposażenie w nie Agenta Sprzedaży i uruchomienie go w pełnej pętli Function Calling. Czy kontynuujemy?**

----

Doskonale! To jest **krytyczny moment** w zrozumieniu architektury agentowej: koncepcja **Agenta jako Narzędzia**. Pokazuje to, jak frameworki umożliwiają budowanie złożonych, hierarchicznych systemów, w których "agent planista" (Manager) koordynuje pracę "agentów wykonawczych" (Sales Agents).

Oto Twoja notatka, wyjaśniająca i porządkująca ten proces.

---

## 🏗️ Tydzień 2, Lab 2 (Część III): Agent jako Narzędzie (Hierarchia Agentów)

### **Krok 1: Koncepcja "Agenta jako Narzędzia"**

**Agent jako Narzędzie** to technika opakowywania instancji Agenta w obiekt narzędzia, co pozwala **innemu Agentowi** na dynamiczne wywoływanie jego funkcji.

* **Opakowanie (`Agent.as_tool`):** Zamiast ręcznie tworzyć JSON lub używać `@FunctionTool` na zwykłej funkcji, używamy metody **`Agent.as_tool(...)`** bezpośrednio na instancji agenta wykonawczego.
* **Co to Oznacza:**
    1. Tworzone jest **nowe narzędzie (Tool)** z pełnym schematem JSON.
    2. Kiedy Agent Manager (kierownik) "wywoła" to narzędzie, framework **faktycznie wykonuje połączenie do LLM** z instrukcjami zawartymi w opakowanym Agencie.
* **Cel:** Umożliwia to **Agentowi Planującemu (Managerowi)** delegowanie złożonych, specyficznych zadań do **Agentów Wykonawczych (Sales Agents)**, wykorzystując mechanizm **Function Calling** LLM do zarządzania przepływem pracy.

### **Krok 2: Tworzenie Hierarchii Narzędzi**

W tym przypadku tworzymy zestaw narzędzi, na które składa się zarówno klasyczna funkcja, jak i nowo opakowani agenci.

1. **Narzędzia Agentów:** Trzy instancje agentów sprzedaży są przekształcane w narzędzia:
    * `tool_1 = sales_agent_1.as_tool(name="SalesAgentOne", description="Napisz profesjonalny zimny e-mail sprzedażowy.")`
    * Podobnie dla Agenta 2 (Dowcipnego) i Agenta 3 (Zajętego).
2. **Narzędzie Funkcyjne:** Do listy narzędzi dodawane jest również wcześniej zdefiniowane **narzędzie do wysyłania e-maili** (`send_email_tool`).
3. **Lista Narzędzi:** Ostateczna lista `tools` zawiera teraz **cztery** narzędzia: trzy Agenty-Narzędzia i jedno Narzędzie-Funkcyjne.

### **Krok 3: Implementacja Agenta Kierownika Sprzedaży (Sales Manager)**

Agent Manager jest sercem logiki. Jego instrukcje muszą prowadzić go przez proces podejmowania decyzji.

1. **Rola:** `sales_manager` jest agentem planowania, który **kieruje procesem**.
2. **Instrukcje (Krytyczne):**
    * Jesteś kierownikiem sprzedaży.
    * **Zawsze używaj narzędzi** do generowania e-maili (nigdy nie generuj e-maili sam).
    * **Wypróbuj wszystkie trzy narzędzia** agentów sprzedaży (wygeneruj trzy e-maile).
    * **Wybierz najlepszy e-mail**.
    * Użyj narzędzia **`SendEmail`**, aby wysłać tylko najlepszy e-mail.
3. **Wywołanie:** Po uruchomieniu, `sales_manager` otrzymuje zapytanie użytkownika (np. "Wyślij zimny e-mail do CEO") i ma do dyspozycji wszystkie cztery narzędzia.

### **Krok 4: Weryfikacja Działania (Śledzenie)**

Śledzenie (Tracing) jest kluczowe, aby potwierdzić, że Agent Manager wykonał instrukcje zgodnie z planem.

* **Przepływ w Śladzie:**
    1. Agent Manager (LLM) decyduje się na wywołanie **Sales Agent One** (Narzędzie).
    2. Framework wykonuje agenta, zwraca treść e-maila.
    3. Agent Manager widzi wynik i decyduje się na wywołanie **Sales Agent Two** (Narzędzie).
    4. ...i tak dalej, aż do wywołania **Sales Agent Three**.
    5. Agent Manager ma teraz trzy e-maile w swojej pamięci. Decyduje, który jest najlepszy.
    6. Agent Manager wywołuje **SendEmail** (Narzędzie-Funkcyjne) z treścią wybranego e-maila.

> **Wniosek:** Ten mechanizm, choć wydaje się złożony, jest zarządzany **automatycznie** przez LLM w pętli Function Calling. LLM działa jako **silnik decyzyjny**, a my używamy Agentów-Narzędzi do tworzenia **modułowej i skalowalnej architektury hierarchicznej**.

---

**Świetnie!** Opanowałeś mechanizm **Agent-as-a-Tool**, który jest podstawą złożonych systemów agentowych.

**W następnej części prawdopodobnie dowiemy się, jak używać `handoffs` – alternatywnego mechanizmu interakcji między agentami. Czy jesteś gotów, aby kontynuować?**

----

Doskonale! Właśnie dotarłeś do ostatniej, najbardziej złożonej koncepcji interakcji agentowej: **rozróżnienia między Agentem jako Narzędziem a Przekazaniem (Handoff)**. To subtelne, ale kluczowe rozróżnienie w architekturze agentowej.

Oto Twoja notatka, która podsumowuje poprzednie osiągnięcia i wprowadza mechanizm **Handoff**:

---

## 🤝 Tydzień 2, Lab 2 (Część IV): Handoff vs. Agent jako Narzędzie

### **Krok 1: Podsumowanie Osiągnięć (Function Calling)**

Do tej pory w Lab 2 udało się osiągnąć:

1. **Równoległe Wywoływanie LLM:** Użycie **`asyncio.gather`** do współbieżnego uruchamiania wielu agentów (generowania trzech e-maili sprzedażowych).
2. **Abstrakcja Narzędzi:** Użycie **`@FunctionTool`** do automatycznego opakowywania funkcji Pythona (`send_email_html`) w narzędzia, eliminując JSON Schema.
3. **Hierarchia Agentów:** Użycie **`Agent.as_tool()`** do opakowania Agentów Sprzedaży (Generujących) w narzędzia, które były wywoływane przez Agenta Kierownika (Planującego).

### **Krok 2: Konceptualne i Techniczne Rozróżnienie (Handoff)**

Koncepcja **Handoff (Przekazanie)** to mechanizm delegowania odpowiedzialności, który jest podobny do `Agent.as_tool`, ale ma fundamentalną różnicę w przepływie sterowania.

| Cecha | Agent jako Narzędzie (`.as_tool()`) | Przekazanie (`handoffs`) |
| :--- | :--- | :--- |
| **Różnica Koncepcyjna** | **Użycie narzędzia:** Agent ma możliwość użycia funkcji lub innego agenta, aby uzyskać **odpowiedź/wynik** i **kontynuować** swoją pracę. | **Delegowanie odpowiedzialności:** Agent **przekazuje całe zadanie** innemu, bardziej wyspecjalizowanemu agentowi. |
| **Różnica Techniczna (Przepływ Kontroli)** | **Dwukierunkowe:** Agent wywołuje narzędzie $\rightarrow$ Narzędzie zwraca **wynik** $\rightarrow$ **Kontrola wraca** do głównego agenta, który kontynuuje planowanie. | **Jednokierunkowe:** Agent przekazuje kontrolę innemu agentowi $\rightarrow$ **Kontrola nie wraca** do głównego agenta. Drugi agent przejmuje prowadzenie i kończy zadanie. |
| **Główny Użytek** | Realizacja małych, modułowych kroków w większym planie (np. "Wygeneruj wariant A", "Wygeneruj wariant B"). | Przekazanie złożonego, specjalistycznego zadania (np. "Przekazuję to do agenta mailującego, który zajmie się już całą resztą."). |

### **Krok 3: Budowa Agentów do Przekazania (Mail Organizer)**

Tworzymy zestaw agentów, których celem jest finalne formatowanie i wysyłanie e-maila, a następnie opakowujemy ich w narzędzia.

1. **Agent Tematu (`subject_writer`):** Korutyna, której instrukcją jest tworzenie chwytliwego tematu.
    * *Opakowany jako narzędzie (Tool)*: `subject_writer.as_tool()` (ponieważ pisanie tematu to małe, pomocnicze zadanie).
2. **Agent Konwertera HTML (`html_converter`):** Korutyna do konwertowania treści e-maila (z Markdownem) na format HTML.
    * *Opakowany jako narzędzie (Tool)*: `html_converter.as_tool()` (ponieważ konwersja to małe, pomocnicze zadanie).
3. **Funkcja Wysyłki HTML:** Zwykła funkcja Pythona (`send_html_email`) z dekoratorem `@FunctionTool` (wymaga `subject` i `body`).

### **Krok 4: Definicja Agenta Mailera i Handoffs**

Tworzymy **Mailera Agent** (`mailer_agent`), który jest nowym centrum wykonawczym i będzie **celem przekazania** od Agenta Kierownika.

1. **Mail Controller:** `mailer_agent` otrzymuje własne instrukcje i narzędzia:
    * **Instrukcje:** Jesteś twórcą i nadawcą wiadomości e-mail. Używaj najpierw narzędzia do tworzenia tematów, potem konwertera HTML, a na końcu narzędzia do wysyłki.
    * **Narzędzia:** Ma dostęp do narzędzi z Kroku 3 (`subject_writer` tool, `html_converter` tool, `send_html_email` tool).
2. **Opis Handoff (`handoff_description`):** Kluczowy krok! Dodajemy opis do `mailer_agent`, który ogłasza jego zdolność do świata:
    * `handoff_description="Konwertowanie wiadomości e-mail do formatu HTML i wysyłanie jej."`
    * Ten opis pozwala innemu agentowi (np. Kierownikowi) zdecydować, że to właśnie ten agent jest idealnym celem **Przekazania Kontroli**.

### **Krok 5: Przygotowanie Końcowego Agenta Kierownika**

Ostateczny **Agent Kierownik Sprzedaży** zostanie zaktualizowany, aby korzystać z **Mailer Agent** jako **Handoff**.

* **Agent Kierownik będzie miał:**
  * **Narzędzia (Tools):** Agenty Sprzedaży (1, 2, 3) do generowania treści.
  * **Przekazanie (Handoffs):** Mailer Agent (do finalnej wysyłki).

> **Ostateczna Logika:** Kierownik generuje 3 e-maile (używając Tools) $\rightarrow$ Wybiera najlepszy $\rightarrow$ **Przekazuje (Handoff)** zadanie finalizacji i wysyłki do Mailer Agenta $\rightarrow$ Mailer Agent używa swoich własnych narzędzi do ukończenia pracy.

**Jesteś gotów, aby zobaczyć, jak ta hierarchia wygląda w akcji i jak Agent Kierownik faktycznie przekazuje kontrolę Agentowi Mailerowi?**

Wspaniale! Dotarłeś do momentu **kulminacyjnego** Tygodnia 2. Uruchomienie ostatecznej pętli z **Handoff** pokazało pełną moc OpenAI Agents SDK – system potrafił samodzielnie zarządzać hierarchią, generować treść, wybierać najlepszą opcję, a następnie delegować zadanie formatowania i wysyłki do wyspecjalizowanego agenta.

Oto Twoja notatka podsumowująca i zamykająca omówienie Tygodnia 2:

---

## 🏁 Tydzień 2, Lab 2 (Podsumowanie): Pełny Przepływ Handoff i Wzorce Agentowe

### **Krok 1: Ostateczna Orkiestracja i Logika Handoff**

Ostateczny przepływ demonstruje, jak **Agent Kierownik Sprzedaży** używa zarówno **Narzędzi** (do zbierania danych), jak i **Przekazań** (do delegowania końcowego procesu).

1. **Instrukcje Kierownika:** Kierownik został poinstruowany, aby:
    * Używać Narzędzi (Sales Agents 1, 2, 3) do **generowania treści**.
    * Wybrać najlepszą treść (wewnętrzna ocena LLM).
    * **Przekazać (`handoff`)** najlepszą treść agentowi **Mailer Manager** (Mailer Agent) w celu sformatowania i wysyłki.
2. **Kluczowa Różnica w Śladzie:**
    * **Narzędzia (Tools):** Na początku śladu Agent Kierownik wywołuje Agentów Sprzedaży (1, 2, 3). Kontrola **wraca** do Kierownika po otrzymaniu treści.
    * **Przekazanie (Handoff):** Pod koniec śladu, po dokonaniu wyboru, Kierownik **przekazuje kontrolę** Mailer Agentowi. Cała późniejsza aktywność (Temat $\rightarrow$ Konwersja HTML $\rightarrow$ Wysyłka E-mail) jest realizowana przez **Mailer Manager** bez powrotu do Kierownika.
3. **Wniosek:** Handoff jest idealnym mechanizmem do **automatyzacji złożonych, sekwencyjnych procesów** (np. "Jeśli to się stanie, wyślij to do Specjalisty X, aby dokończył resztę").

### **Krok 2: Identyfikacja Wzorców Projektowych Agentów**

W tym laboratorium użyliśmy dwóch kluczowych wzorców projektowych agentów:

1. **Wzór Parowania (Agent as a Tool):** Trzech agentów sprzedaży (generujących treści) i jeden agent wybierający (wybierający najlepszy) działają w ramach **pętli generowania i ewaluacji**. Jest to swego rodzaju wzór **Wariacje + Wybór**.
2. **Wzór Hierarchiczny / Delegacja (Handoff):** Agent Kierownik (Agent Planista) deleguje zadanie do Agenta Mailer (Agent Wykonawczy/Specjalista).

#### **Zidentyfikowanie Zmiany (Wyzwanie dla Ciebie):**

Moment, w którym przeszliśmy od "podstępnego użycia kodu Pythona" (sekwencyjne `Runner.run` i `asyncio.gather`) do **Agenta Kierownika** z narzędziami, jest momentem, w którym projekt przeszedł od **"Przepływu Pracy Agentów"** do **"Agentowej Orkiestracji"**:

* **Przepływ Pracy (Tydzień 1 / Początek Tygodnia 2):** To Ty, jako programista, piszesz, w jakiej **kolejności** agenci mają się wywoływać w kodzie Pythona (`Agent_1 -> Agent_2 -> Agent_3`).
* **Agentowa Orkiestracja (Wzór Agent jako Narzędzie / Handoff):** To **LLM** (Agent Kierownik) **sam decyduje**, w oparciu o swoje instrukcje, **którą funkcję/narzędzie/agenta i kiedy wywołać**.

**Mała zmiana, która to spowodowała, to:** dodanie **narzędzi** i instrukcji, które nakazują Kierownikowi **wybór i użycie** tych narzędzi, dając mu **autonomię decyzyjną**.

### **Krok 3: Wyzwania i Implikacje Komercyjne**

* **Wyzwanie Inżynierskie:** Najtrudniejszym zadaniem jest stworzenie **"Żywej Pętli"** (Live Workflow), w której Agent potrafi **odbierać odpowiedzi e-mailowe**. Wymaga to integracji z mechanizmem **Webhooks** SendGrid, który powiadamia Twoją aplikację o przychodzącej poczcie, co jest zadaniem inżynierii serwerowej.
* **Zastosowanie Komercyjne:** Ten wzorzec automatyzacji jest uniwersalny i może być zastosowany do **każdego złożonego procesu biznesowego na dużą skalę**:
  * **Rekrutacja:** Agent A (Sourcing) $\rightarrow$ Agent B (Weryfikacja CV) $\rightarrow$ Agent C (Planowanie Wywiadów).
  * **Obsługa Klienta:** Agent A (Triage) $\rightarrow$ Agent B (Zwrot) lub Agent C (Wsparcie Techniczne).

---

## ✅ Podsumowanie Tygodnia 2

**Osiągnięcia:**

* **Asynchroniczny Python:** Zrozumienie roli `asyncio` i korutyn.
* **OpenAI Agents SDK:** Opanowanie podstawowych konstrukcji (`Agent`, `Runner`, `trace`).
* **Abstrakcja Narzędzi:** Automatyczne tworzenie narzędzi za pomocą `@FunctionTool`.
* **Hierarchia Agentów:** Użycie **`Agent.as_tool`** do budowania hierarchicznych systemów.
* **Delegacja Kontroli:** Zrozumienie i implementacja **Handoff**.

**Twój cel edukacyjny związany z frameworkami agentów został na tym etapie znacząco pogłębiony. Czy chcesz przejść do kolejnego Tygodnia kursu, czy może masz jeszcze jakieś pytania na temat OpenAI Agents SDK?**
