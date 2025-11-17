"""
Projekt: Budowa Przedstawiciela Handlowego z OpenAI Agents SDK

Ten moduł demonstruje budowę wieloagentowej architektury sprzedażowej,
która generuje i wysyła wiadomości e-mail w różnych stylach komunikacji.

Główne koncepcje:
1. Agent workflow - podstawowy przepływ pracy agentów
2. Narzędzia (Tools) - integracja funkcji z agentami
3. Handoffs - przekazywanie kontroli między agentami
"""

import asyncio
import os
from typing import Dict

import sendgrid
from agents import Agent, Runner, function_tool, trace
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from sendgrid.helpers.mail import Content, Email, Mail, To

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv(override=True)

# ============================================================================
# KONFIGURACJA
# ============================================================================

# Pobieranie konfiguracji z zmiennych środowiskowych
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get(
    "FROM_EMAIL", "example@example.com"
)  # Zmień na swój zweryfikowany adres
TO_EMAIL = os.environ.get("TO_EMAIL", "example@example.com")  # Zmień na adres odbiorcy

# Weryfikacja wymaganych zmiennych środowiskowych
if not SENDGRID_API_KEY:
    raise ValueError(
        "SENDGRID_API_KEY nie jest ustawiony. Dodaj go do pliku .env: SENDGRID_API_KEY=xxxx"
    )

# ============================================================================
# CZĘŚĆ 1: PRZYGOTOWANIE I TEST WYSYŁKI E-MAIL
# ============================================================================


def send_test_email() -> None:
    """
    Funkcja testowa do weryfikacji konfiguracji SendGrid.

    Wysyła prostą wiadomość testową, aby upewnić się, że:
    - Klucz API jest poprawny
    - Adres nadawcy jest zweryfikowany w SendGrid
    - Konfiguracja działa poprawnie

    Oczekiwany status odpowiedzi: 202 (Accepted)
    """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL)
    to_email = To(TO_EMAIL)
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"Status odpowiedzi SendGrid: {response.status_code}")
    if response.status_code == 202:
        print("✅ Test e-mail wysłany pomyślnie! Sprawdź skrzynkę odbiorczą.")
    else:
        print(f"⚠️ Otrzymano nieoczekiwany status: {response.status_code}")


# ============================================================================
# CZĘŚĆ 2: DEFINICJA AGENTÓW SPRZEDAŻY
# ============================================================================

# Instrukcje (monity systemowe) dla trzech różnych agentów sprzedaży
# Każdy agent ma inną "osobowość", co wpływa na styl generowanych e-maili

INSTRUCTIONS_PROFESSIONAL = (
    "You are a sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write professional, serious cold emails."
)

INSTRUCTIONS_ENGAGING = (
    "You are a humorous, engaging sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write witty, engaging cold emails that are likely to get a response."
)

INSTRUCTIONS_CONCISE = (
    "You are a busy sales agent working for ComplAI, "
    "a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. "
    "You write concise, to the point cold emails."
)


def create_sales_agents() -> tuple[Agent, Agent, Agent]:
    """
    Tworzy trzy agentów sprzedaży z różnymi stylami komunikacji.

    Returns:
        tuple: Trzech agentów (profesjonalny, angażujący, zwięzły)
    """
    sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=INSTRUCTIONS_PROFESSIONAL,
        model="gpt-4o-mini",
    )

    sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=INSTRUCTIONS_ENGAGING,
        model="gpt-4o-mini",
    )

    sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=INSTRUCTIONS_CONCISE,
        model="gpt-4o-mini",
    )

    return sales_agent1, sales_agent2, sales_agent3


# ============================================================================
# CZĘŚĆ 3: DEMONSTRACJA STRUMIENIOWANIA (STREAMING)
# ============================================================================


async def demonstrate_streaming(agent: Agent, message: str) -> None:
    """
    Demonstruje strumieniowe generowanie odpowiedzi przez agenta.

    Zamiast czekać na całą odpowiedź, wyświetlamy ją fragment po fragmencie,
    co jest szczególnie przydatne w aplikacjach UI/UX.

    Args:
        agent: Agent do uruchomienia
        message: Wiadomość wejściowa dla agenta
    """
    print("🔄 Generowanie odpowiedzi (streaming)...\n")
    result = Runner.run_streamed(agent, input=message)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)
    print("\n")


# ============================================================================
# CZĘŚĆ 4: RÓWNOLEGŁE WYWOŁYWANIE AGENTÓW
# ============================================================================


async def generate_parallel_emails(
    agent1: Agent, agent2: Agent, agent3: Agent, message: str
) -> list[str]:
    """
    Generuje trzy różne e-maile sprzedażowe równolegle używając asyncio.gather.

    Korzyści:
    - Oszczędność czasu - trzy wywołania API działają jednocześnie
    - Lepsze wykorzystanie zasobów - gdy jeden agent czeka na odpowiedź API,
      pętla zdarzeń przełącza się na innego agenta

    Args:
        agent1: Pierwszy agent (profesjonalny)
        agent2: Drugi agent (angażujący)
        agent3: Trzeci agent (zwięzły)
        message: Wiadomość wejściowa

    Returns:
        Lista trzech wygenerowanych e-maili
    """
    with trace("Parallel cold emails"):
        results = await asyncio.gather(
            Runner.run(agent1, message),
            Runner.run(agent2, message),
            Runner.run(agent3, message),
        )

    outputs = [result.final_output for result in results]
    return outputs


async def select_best_email(
    agent1: Agent, agent2: Agent, agent3: Agent, picker_agent: Agent, message: str
) -> str:
    """
    Generuje trzy warianty e-maili, a następnie wybiera najlepszy.

    Proces:
    1. Trzy agenty generują równolegle różne warianty e-maili
    2. Agent wybierający (picker) ocenia wszystkie warianty i wybiera najlepszy

    Args:
        agent1: Pierwszy agent sprzedaży
        agent2: Drugi agent sprzedaży
        agent3: Trzeci agent sprzedaży
        picker_agent: Agent odpowiedzialny za wybór najlepszego e-maila
        message: Wiadomość wejściowa

    Returns:
        Najlepszy wybrany e-mail
    """
    with trace("Selection from sales people"):
        # Krok 1: Generowanie trzech wariantów równolegle
        results = await asyncio.gather(
            Runner.run(agent1, message),
            Runner.run(agent2, message),
            Runner.run(agent3, message),
        )
        outputs = [result.final_output for result in results]

        # Krok 2: Przygotowanie wiadomości dla agenta wybierającego
        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

        # Krok 3: Wybór najlepszego e-maila
        best = await Runner.run(picker_agent, emails)

        return best.final_output


# ============================================================================
# CZĘŚĆ 5: NARZĘDZIA (TOOLS) - INTEGRACJA FUNKCJI Z AGENTAMI
# ============================================================================


@function_tool
def send_email(body: str) -> Dict[str, str]:
    """
    Wysyła e-mail z podaną treścią do wszystkich potencjalnych klientów.

    Ta funkcja jest automatycznie konwertowana na narzędzie (tool) przez
    dekorator @function_tool. Framework OpenAI Agents SDK automatycznie:
    - Generuje nazwę narzędzia z nazwy funkcji
    - Tworzy opis z docstringa
    - Generuje JSON Schema z type hints

    Args:
        body: Treść wiadomości e-mail do wysłania

    Returns:
        Słownik ze statusem operacji
    """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL)
    to_email = To(TO_EMAIL)
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}


@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Wysyła e-mail z podanym tematem i treścią HTML do wszystkich potencjalnych klientów.

    Args:
        subject: Temat wiadomości e-mail
        html_body: Treść wiadomości w formacie HTML

    Returns:
        Słownik ze statusem operacji
    """
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(FROM_EMAIL)
    to_email = To(TO_EMAIL)
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}


# ============================================================================
# CZĘŚĆ 6: AGENT JAKO NARZĘDZIE (AGENT AS A TOOL)
# ============================================================================


def create_sales_agent_tools(agent1: Agent, agent2: Agent, agent3: Agent) -> list:
    """
    Konwertuje agentów sprzedaży na narzędzia, które mogą być używane przez innych agentów.

    Koncepcja "Agent jako Narzędzie" pozwala agentowi planującemu (Manager)
    na dynamiczne wywoływanie innych agentów wykonawczych.

    Args:
        agent1: Pierwszy agent sprzedaży
        agent2: Drugi agent sprzedaży
        agent3: Trzeci agent sprzedaży

    Returns:
        Lista narzędzi utworzonych z agentów
    """
    description = "Write a cold sales email"

    tool1 = agent1.as_tool(tool_name="sales_agent1", tool_description=description)
    tool2 = agent2.as_tool(tool_name="sales_agent2", tool_description=description)
    tool3 = agent3.as_tool(tool_name="sales_agent3", tool_description=description)

    return [tool1, tool2, tool3]


# ============================================================================
# CZĘŚĆ 7: AGENT KIEROWNIK SPRZEDAŻY Z NARZĘDZIAMI
# ============================================================================


def create_sales_manager_with_tools(sales_tools: list) -> Agent:
    """
    Tworzy agenta kierownika sprzedaży, który używa narzędzi do generowania i wysyłania e-maili.

    Instrukcje kierownika prowadzą go przez proces:
    1. Generowanie trzech wariantów e-maili używając narzędzi agentów
    2. Wybór najlepszego e-maila
    3. Wysłanie najlepszego e-maila używając narzędzia send_email

    Args:
        sales_tools: Lista narzędzi (agenty sprzedaży + send_email)

    Returns:
        Agent kierownika sprzedaży
    """
    instructions = """
    You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
     
    Follow these steps carefully:
    1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
     
    2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
     
    3. Use the send_email tool to send the best email (and only the best email) to the user.
     
    Crucial Rules:
    - You must use the sales agent tools to generate the drafts — do not write them yourself.
    - You must send ONE email using the send_email tool — never more than one.
    """

    return Agent(
        name="Sales Manager",
        instructions=instructions,
        tools=sales_tools,
        model="gpt-4o-mini",
    )


# ============================================================================
# CZĘŚĆ 8: HANDOFFS - PRZEKAZYWANIE KONTROLI MIĘDZY AGENTAMI
# ============================================================================


def create_email_formatting_agents() -> tuple[Agent, Agent]:
    """
    Tworzy agentów odpowiedzialnych za formatowanie e-maili.

    Returns:
        Tuple zawierający:
        - Agent do pisania tematów e-maili
        - Agent do konwersji treści na HTML
    """
    subject_instructions = (
        "You can write a subject for a cold sales email. "
        "You are given a message and you need to write a subject for an email that is likely to get a response."
    )

    html_instructions = (
        "You can convert a text email body to an HTML email body. "
        "You are given a text email body which might have some markdown "
        "and you need to convert it to an HTML email body with simple, clear, compelling layout and design."
    )

    subject_writer = Agent(
        name="Email subject writer",
        instructions=subject_instructions,
        model="gpt-4o-mini",
    )

    html_converter = Agent(
        name="HTML email body converter",
        instructions=html_instructions,
        model="gpt-4o-mini",
    )

    return subject_writer, html_converter


def create_email_manager_agent() -> Agent:
    """
    Tworzy agenta zarządzającego formatowaniem i wysyłką e-maili.

    Ten agent będzie używany jako "handoff" - agent kierownik przekazuje
    mu kontrolę nad finalizacją i wysyłką e-maila.

    Returns:
        Agent zarządzający e-mailami
    """
    subject_writer, html_converter = create_email_formatting_agents()

    # Konwersja agentów na narzędzia
    subject_tool = subject_writer.as_tool(
        tool_name="subject_writer",
        tool_description="Write a subject for a cold sales email",
    )

    html_tool = html_converter.as_tool(
        tool_name="html_converter",
        tool_description="Convert a text email body to an HTML email body",
    )

    # Lista narzędzi dla agenta zarządzającego
    tools = [subject_tool, html_tool, send_html_email]

    instructions = (
        "You are an email formatter and sender. You receive the body of an email to be sent. "
        "You first use the subject_writer tool to write a subject for the email, "
        "then use the html_converter tool to convert the body to HTML. "
        "Finally, you use the send_html_email tool to send the email with the subject and HTML body."
    )

    return Agent(
        name="Email Manager",
        instructions=instructions,
        tools=tools,
        model="gpt-4o-mini",
        handoff_description="Convert an email to HTML and send it",
    )


def create_sales_manager_with_handoff(sales_tools: list, email_manager: Agent) -> Agent:
    """
    Tworzy agenta kierownika sprzedaży z możliwością przekazania kontroli (handoff).

    Różnica między Tools a Handoffs:
    - Tools: Agent wywołuje narzędzie, otrzymuje wynik, kontynuuje pracę
    - Handoffs: Agent przekazuje całe zadanie innemu agentowi, kontrola nie wraca

    Args:
        sales_tools: Lista narzędzi do generowania e-maili
        email_manager: Agent zarządzający formatowaniem i wysyłką

    Returns:
        Agent kierownika z możliwością handoff
    """
    instructions = """
    You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
     
    Follow these steps carefully:
    1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
     
    2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
    You can use the tools multiple times if you're not satisfied with the results from the first try.
     
    3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
     
    Crucial Rules:
    - You must use the sales agent tools to generate the drafts — do not write them yourself.
    - You must hand off exactly ONE email to the Email Manager — never more than one.
    """

    return Agent(
        name="Sales Manager",
        instructions=instructions,
        tools=sales_tools,
        handoffs=[email_manager],
        model="gpt-4o-mini",
    )


# ============================================================================
# CZĘŚĆ 9: GŁÓWNE FUNKCJE DEMONSTRACYJNE
# ============================================================================


async def demo_basic_workflow() -> None:
    """Demonstracja podstawowego przepływu pracy z agentami."""
    print("=" * 60)
    print("DEMONSTRACJA 1: Podstawowy przepływ pracy")
    print("=" * 60)

    agent1, agent2, agent3 = create_sales_agents()

    # Demonstracja streaming
    print("\n1. Streaming odpowiedzi:")
    await demonstrate_streaming(agent1, "Write a cold sales email")

    # Równoległe generowanie e-maili
    print("\n2. Równoległe generowanie trzech e-maili:")
    outputs = await generate_parallel_emails(
        agent1, agent2, agent3, "Write a cold sales email"
    )
    for i, output in enumerate(outputs, 1):
        print(f"\n--- E-mail {i} ---\n{output}\n")

    # Wybór najlepszego e-maila
    print("\n3. Wybór najlepszego e-maila:")
    picker_agent = Agent(
        name="sales_picker",
        instructions=(
            "You pick the best cold sales email from the given options. "
            "Imagine you are a customer and pick the one you are most likely to respond to. "
            "Do not give an explanation; reply with the selected email only."
        ),
        model="gpt-4o-mini",
    )
    best_email = await select_best_email(
        agent1, agent2, agent3, picker_agent, "Write a cold sales email"
    )
    print(f"\nNajlepszy e-mail:\n{best_email}\n")


async def demo_sales_manager_with_tools() -> None:
    """Demonstracja agenta kierownika używającego narzędzi."""
    print("=" * 60)
    print("DEMONSTRACJA 2: Agent kierownik z narzędziami")
    print("=" * 60)

    agent1, agent2, agent3 = create_sales_agents()

    # Tworzenie narzędzi
    sales_tools = create_sales_agent_tools(agent1, agent2, agent3)
    sales_tools.append(send_email)  # Dodanie narzędzia do wysyłki

    # Tworzenie agenta kierownika
    sales_manager = create_sales_manager_with_tools(sales_tools)

    # Uruchomienie agenta kierownika
    message = "Send a cold sales email addressed to 'Dear CEO'"
    print(f"\nWiadomość: {message}\n")

    with trace("Sales manager"):
        result = await Runner.run(sales_manager, message)

    print(f"\nWynik: {result.final_output}\n")


async def demo_sales_manager_with_handoff() -> None:
    """Demonstracja agenta kierownika z przekazaniem kontroli (handoff)."""
    print("=" * 60)
    print("DEMONSTRACJA 3: Agent kierownik z handoff")
    print("=" * 60)

    agent1, agent2, agent3 = create_sales_agents()

    # Tworzenie narzędzi dla agentów sprzedaży
    sales_tools = create_sales_agent_tools(agent1, agent2, agent3)

    # Tworzenie agenta zarządzającego e-mailami
    email_manager = create_email_manager_agent()

    # Tworzenie agenta kierownika z handoff
    sales_manager = create_sales_manager_with_handoff(sales_tools, email_manager)

    # Uruchomienie agenta kierownika
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    print(f"\nWiadomość: {message}\n")

    with trace("Automated SDR"):
        result = await Runner.run(sales_manager, message)

    print(f"\nWynik: {result.final_output}\n")
    print("✅ Sprawdź swoją skrzynkę e-mail!")


# ============================================================================
# CZĘŚĆ 10: GŁÓWNA FUNKCJA
# ============================================================================


async def main() -> None:
    """
    Główna funkcja uruchamiająca wszystkie demonstracje.

    Uwaga: Przed uruchomieniem upewnij się, że:
    1. Masz skonfigurowany plik .env z SENDGRID_API_KEY
    2. Masz zweryfikowany adres e-mail w SendGrid
    3. Masz ustawiony OPENAI_API_KEY w zmiennych środowiskowych
    """
    print("\n" + "=" * 60)
    print("PROJEKT: Budowa Przedstawiciela Handlowego")
    print("OpenAI Agents SDK - Demonstracja")
    print("=" * 60 + "\n")

    # Test konfiguracji SendGrid
    print("🔧 Testowanie konfiguracji SendGrid...")
    try:
        send_test_email()
    except Exception as e:
        print(f"❌ Błąd podczas testu SendGrid: {e}")
        print("⚠️  Kontynuowanie bez wysyłki e-maili...\n")

    # Uruchomienie demonstracji
    try:
        # Demonstracja 1: Podstawowy przepływ
        await demo_basic_workflow()

        # Demonstracja 2: Agent z narzędziami
        # await demo_sales_manager_with_tools()  # Odkomentuj, aby uruchomić

        # Demonstracja 3: Agent z handoff
        # await demo_sales_manager_with_handoff()  # Odkomentuj, aby uruchomić

        print("\n" + "=" * 60)
        print("✅ Wszystkie demonstracje zakończone!")
        print("📊 Sprawdź ślady (traces) na: https://platform.openai.com/traces")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Błąd podczas uruchamiania demonstracji: {e}")
        raise


if __name__ == "__main__":
    # Uruchomienie głównej funkcji asynchronicznej
    asyncio.run(main())
