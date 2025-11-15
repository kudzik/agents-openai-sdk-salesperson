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

---
