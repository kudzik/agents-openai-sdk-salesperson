# README

## 📌 Opis Projektu: Budowa Przedstawiciela Handlowego z OpenAI Agents SDK

Projekt polega na stworzeniu wieloagentowej architektury sprzedażowej z wykorzystaniem **OpenAI Agents SDK**. Celem jest zbudowanie **Przedstawiciela Handlowego**, który potrafi generować i wysyłać wiadomości e-mail w różnych stylach komunikacji, a także współpracować z innymi agentami.

### 🎯 Główne elementy projektu

- **Integracja z narzędziem SendGrid** – umożliwia wysyłkę transakcyjnych wiadomości e-mail poprzez zewnętrzne API.
- **Definicja agentów sprzedaży** – każdy agent posiada odmienną osobowość i ton komunikacji:
  - Profesjonalny i poważny,
  - Dowcipny i angażujący,
  - Zwięzły i rzeczowy.
- **Prosty przepływ pracy (Streaming)** – zastosowanie metody `runner.run_streamed`, która pozwala na strumieniowe generowanie odpowiedzi i ich natychmiastowe wyświetlanie.
- **Eksploracja trzech warstw architektury agentowej**:
  1. Prosty przepływ agentów,  
  2. Agenci z narzędziami (Tools),  
  3. Współpraca agentów (handoffs).

### 🌟 Rezultat

Powstaje fundament systemu wieloagentowego, w którym agenci mogą:

- generować różnorodne wiadomości sprzedażowe,
- korzystać z narzędzi świata rzeczywistego (np. SendGrid),
- współpracować ze sobą w ramach orkiestracji i przekazywania zadań.

Popraw pliki  @main.py  aby był zgodny z @Notatki.md  dodaj komentarze i zrefaktoryzuj kod. napisz wymagane testy i sprawdź działanie, następnie na podstawie @main.py  i @Notatki.md Stwórz plik KURS.MD z profesjonalnym kursem krok po kroku zawierającym wyjaśnienia wraz z przykładami zamieszczonego kodu. Kurs ma być po polsku, uzupełnij brakujące koncepcje, sprawdź czy nie ma błędów składniowych i logicznych. Jeśli uznasz za konieczne uzupełnij brakujące koncepcje i wytłumacz je w przystępny sposób.Kurs kierowany dla początkujących w formie artykułu na bloga. pomiń informacje o dniach ma być ciągły i spójny dokumentacja @openai-agents-python.   Jeśli masz pytania to je zadaj.
