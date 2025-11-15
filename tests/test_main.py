"""
Testy jednostkowe dla modułu main.py

Testy sprawdzają:
- Konfigurację i walidację zmiennych środowiskowych
- Tworzenie agentów
- Funkcje pomocnicze
- Integrację z SendGrid (mock)
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict

# Dodanie ścieżki do modułu głównego
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mockowanie sendgrid przed importem main
with patch.dict('sys.modules', {'sendgrid': MagicMock()}):
    from main import (
        send_test_email,
        create_sales_agents,
        create_sales_agent_tools,
        create_sales_manager_with_tools,
        create_email_manager_agent,
        create_sales_manager_with_handoff,
        send_email,
        send_html_email,
    )


class TestConfiguration:
    """Testy konfiguracji i zmiennych środowiskowych"""

    def test_sendgrid_api_key_required(self):
        """Test sprawdzający, czy brak SENDGRID_API_KEY powoduje błąd"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SENDGRID_API_KEY"):
                # Reimport modułu, aby sprawdzić walidację
                import importlib
                import main
                importlib.reload(main)


class TestSalesAgents:
    """Testy tworzenia agentów sprzedaży"""

    def test_create_sales_agents(self):
        """Test tworzenia trzech agentów sprzedaży"""
        agent1, agent2, agent3 = create_sales_agents()

        assert agent1 is not None
        assert agent2 is not None
        assert agent3 is not None

        assert agent1.name == "Professional Sales Agent"
        assert agent2.name == "Engaging Sales Agent"
        assert agent3.name == "Busy Sales Agent"

    def test_agents_have_different_instructions(self):
        """Test sprawdzający, czy agenci mają różne instrukcje"""
        agent1, agent2, agent3 = create_sales_agents()

        assert agent1.instructions != agent2.instructions
        assert agent2.instructions != agent3.instructions
        assert agent1.instructions != agent3.instructions


class TestTools:
    """Testy narzędzi (tools)"""

    def test_create_sales_agent_tools(self):
        """Test konwersji agentów na narzędzia"""
        agent1, agent2, agent3 = create_sales_agents()
        tools = create_sales_agent_tools(agent1, agent2, agent3)

        assert len(tools) == 3
        assert all(tool is not None for tool in tools)

    def test_send_email_function_tool(self):
        """Test funkcji send_email jako narzędzia"""
        # Sprawdzenie, czy funkcja ma dekorator @function_tool
        assert hasattr(send_email, '__name__')
        assert send_email.__name__ == 'send_email'

    def test_send_html_email_function_tool(self):
        """Test funkcji send_html_email jako narzędzia"""
        assert hasattr(send_html_email, '__name__')
        assert send_html_email.__name__ == 'send_html_email'

    @patch('main.sendgrid.SendGridAPIClient')
    @patch.dict(os.environ, {
        'SENDGRID_API_KEY': 'test_key',
        'FROM_EMAIL': 'test@example.com',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_send_email_mock(self, mock_sendgrid_client):
        """Test wysyłki e-maila z mockiem SendGrid"""
        # Konfiguracja mocka
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client.client.mail.send.post.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client

        # Wywołanie funkcji
        result = send_email("Test email body")

        # Weryfikacja
        assert result == {"status": "success"}
        mock_client.client.mail.send.post.assert_called_once()

    @patch('main.sendgrid.SendGridAPIClient')
    @patch.dict(os.environ, {
        'SENDGRID_API_KEY': 'test_key',
        'FROM_EMAIL': 'test@example.com',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_send_html_email_mock(self, mock_sendgrid_client):
        """Test wysyłki e-maila HTML z mockiem SendGrid"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client.client.mail.send.post.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client

        result = send_html_email("Test Subject", "<html>Test body</html>")

        assert result == {"status": "success"}
        mock_client.client.mail.send.post.assert_called_once()


class TestManagers:
    """Testy agentów zarządzających"""

    def test_create_sales_manager_with_tools(self):
        """Test tworzenia agenta kierownika z narzędziami"""
        agent1, agent2, agent3 = create_sales_agents()
        sales_tools = create_sales_agent_tools(agent1, agent2, agent3)
        sales_tools.append(send_email)

        manager = create_sales_manager_with_tools(sales_tools)

        assert manager is not None
        assert manager.name == "Sales Manager"
        assert len(manager.tools) == 4  # 3 agenty + send_email

    def test_create_email_manager_agent(self):
        """Test tworzenia agenta zarządzającego e-mailami"""
        email_manager = create_email_manager_agent()

        assert email_manager is not None
        assert email_manager.name == "Email Manager"
        assert email_manager.handoff_description is not None
        assert len(email_manager.tools) == 3  # subject_tool, html_tool, send_html_email

    def test_create_sales_manager_with_handoff(self):
        """Test tworzenia agenta kierownika z handoff"""
        agent1, agent2, agent3 = create_sales_agents()
        sales_tools = create_sales_agent_tools(agent1, agent2, agent3)
        email_manager = create_email_manager_agent()

        manager = create_sales_manager_with_handoff(sales_tools, email_manager)

        assert manager is not None
        assert manager.name == "Sales Manager"
        assert len(manager.tools) == 3
        assert len(manager.handoffs) == 1
        assert manager.handoffs[0] == email_manager


class TestSendGridIntegration:
    """Testy integracji z SendGrid"""

    @patch('main.sendgrid.SendGridAPIClient')
    @patch.dict(os.environ, {
        'SENDGRID_API_KEY': 'test_key',
        'FROM_EMAIL': 'test@example.com',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_send_test_email_success(self, mock_sendgrid_client, capsys):
        """Test pomyślnej wysyłki testowego e-maila"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client.client.mail.send.post.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client

        send_test_email()

        captured = capsys.readouterr()
        assert "202" in captured.out or "Status odpowiedzi SendGrid: 202" in captured.out
        mock_client.client.mail.send.post.assert_called_once()

    @patch('main.sendgrid.SendGridAPIClient')
    @patch.dict(os.environ, {
        'SENDGRID_API_KEY': 'test_key',
        'FROM_EMAIL': 'test@example.com',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_send_test_email_failure(self, mock_sendgrid_client, capsys):
        """Test obsługi błędu podczas wysyłki e-maila"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_client.client.mail.send.post.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client

        send_test_email()

        captured = capsys.readouterr()
        assert "400" in captured.out


class TestHelperFunctions:
    """Testy funkcji pomocniczych"""

    def test_send_email_returns_dict(self):
        """Test sprawdzający typ zwracany przez send_email"""
        with patch('main.sendgrid.SendGridAPIClient') as mock_sendgrid:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 202
            mock_client.client.mail.send.post.return_value = mock_response
            mock_sendgrid.return_value = mock_client

            with patch.dict(os.environ, {
                'SENDGRID_API_KEY': 'test_key',
                'FROM_EMAIL': 'test@example.com',
                'TO_EMAIL': 'recipient@example.com'
            }):
                result = send_email("Test")
                assert isinstance(result, dict)
                assert "status" in result

    def test_send_html_email_returns_dict(self):
        """Test sprawdzający typ zwracany przez send_html_email"""
        with patch('main.sendgrid.SendGridAPIClient') as mock_sendgrid:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 202
            mock_client.client.mail.send.post.return_value = mock_response
            mock_sendgrid.return_value = mock_client

            with patch.dict(os.environ, {
                'SENDGRID_API_KEY': 'test_key',
                'FROM_EMAIL': 'test@example.com',
                'TO_EMAIL': 'recipient@example.com'
            }):
                result = send_html_email("Subject", "<html>Body</html>")
                assert isinstance(result, dict)
                assert "status" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

