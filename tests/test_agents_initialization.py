"""
Tests to validate that all agents can be started and initialized correctly.
This ensures that new changes will not break the current behavior.
"""

import pytest
from unittest.mock import patch, MagicMock
import os


@pytest.fixture
def mock_env_vars():
    """Mock environment variables needed for agents."""
    with patch.dict(os.environ, {
        'AZURE_DEVOPS_ORGANIZATION': 'test-org',
        'AZURE_DEVOPS_PROJECT': 'test-project',
        'AZURE_DEVOPS_PAT': 'test-pat',
        'AZURE_DEVOPS_USER_EMAIL': 'test@example.com',
        'AGENT_BASE_URL': 'http://localhost:8008',
        'MODEL_NAME': 'openai/gpt-4o'
    }):
        yield


@pytest.fixture
def mock_load_context():
    """Mock the load_context function to avoid Azure DevOps API calls."""
    with patch('buildgentic.tools.tools_azureDevOps.load_context') as mock:
        mock.return_value = {
            'name': 'Test Agent',
            'description': 'Test agent description',
            'instruction': 'Test agent instructions'
        }
        yield mock


@pytest.fixture
def mock_agent():
    """Mock Agent class to avoid actual agent creation."""
    with patch('buildgentic.manager.agent.Agent') as mock_manager_agent, \
         patch('buildgentic.architect.agent.Agent') as mock_architect_agent, \
         patch('buildgentic.developer.agent.Agent') as mock_developer_agent, \
         patch('buildgentic.qa.agent.Agent') as mock_qa_agent, \
         patch('buildgentic.compliance.agent.Agent') as mock_compliance_agent:
        
        # Configure each mock to return a mock agent with the correct name
        def create_mock_agent(name):
            mock = MagicMock()
            mock.name = name
            return mock
        
        mock_manager_agent.return_value = create_mock_agent('manager')
        mock_architect_agent.return_value = create_mock_agent('architect')
        mock_developer_agent.return_value = create_mock_agent('developer')
        mock_qa_agent.return_value = create_mock_agent('qa')
        mock_compliance_agent.return_value = create_mock_agent('compliance')
        
        yield {
            'manager': mock_manager_agent,
            'architect': mock_architect_agent,
            'developer': mock_developer_agent,
            'qa': mock_qa_agent,
            'compliance': mock_compliance_agent
        }


class TestManagerAgent:
    """Tests for Manager agent initialization."""

    def test_get_manager_agent(self, mock_load_context, mock_agent):
        """Test that manager agent can be created successfully."""
        from buildgentic.manager.agent import get_manager_agent
        
        agent = get_manager_agent("openai/gpt-4o")
        
        assert agent is not None
        assert agent.name == 'manager'
        mock_agent['manager'].assert_called_once()

    def test_get_manager_agent_card(self, mock_load_context):
        """Test that manager agent card can be created successfully."""
        from buildgentic.manager.agent import get_manager_agent_card
        
        agent_url = "http://localhost:8008/a2a/manager"
        card = get_manager_agent_card(agent_url)
        
        assert card is not None
        assert card.name == "Manager Agent"
        assert card.url == agent_url
        assert card.version == "1.0"


class TestArchitectAgent:
    """Tests for Architect agent initialization."""

    def test_get_architect_agent(self, mock_load_context, mock_agent):
        """Test that architect agent can be created successfully."""
        from buildgentic.architect.agent import get_architect_agent
        
        agent = get_architect_agent("openai/gpt-4o")
        
        assert agent is not None
        assert agent.name == 'architect'
        mock_agent['architect'].assert_called_once()

    def test_get_architect_agent_card(self, mock_load_context):
        """Test that architect agent card can be created successfully."""
        from buildgentic.architect.agent import get_architect_agent_card
        
        agent_url = "http://localhost:8008/a2a/architect"
        card = get_architect_agent_card(agent_url)
        
        assert card is not None
        assert card.name == "Architect Agent"
        assert card.url == agent_url
        assert card.version == "1.0"


class TestDeveloperAgent:
    """Tests for Developer agent initialization."""

    def test_get_developer_agent(self, mock_load_context, mock_agent):
        """Test that developer agent can be created successfully."""
        from buildgentic.developer.agent import get_developer_agent
        
        agent = get_developer_agent("openai/gpt-4o")
        
        assert agent is not None
        assert agent.name == 'developer'
        mock_agent['developer'].assert_called_once()

    def test_get_developer_agent_card(self, mock_load_context):
        """Test that developer agent card can be created successfully."""
        from buildgentic.developer.agent import get_developer_agent_card
        
        agent_url = "http://localhost:8008/a2a/developer"
        card = get_developer_agent_card(agent_url)
        
        assert card is not None
        assert card.name == "Developer Agent"
        assert card.url == agent_url
        assert card.version == "1.0"


class TestQAAgent:
    """Tests for QA agent initialization."""

    def test_get_qa_agent(self, mock_load_context, mock_agent):
        """Test that QA agent can be created successfully."""
        from buildgentic.qa.agent import get_qa_agent
        
        agent = get_qa_agent("openai/gpt-4o")
        
        assert agent is not None
        assert agent.name == 'qa'
        mock_agent['qa'].assert_called_once()

    def test_get_qa_agent_card(self, mock_load_context):
        """Test that QA agent card can be created successfully."""
        from buildgentic.qa.agent import get_qa_agent_card
        
        agent_url = "http://localhost:8008/a2a/qa"
        card = get_qa_agent_card(agent_url)
        
        assert card is not None
        assert card.name == "QA Agent"
        assert card.url == agent_url
        assert card.version == "1.0"


class TestComplianceAgent:
    """Tests for Compliance agent initialization."""

    def test_get_compliance_agent(self, mock_load_context, mock_agent):
        """Test that compliance agent can be created successfully."""
        from buildgentic.compliance.agent import get_compliance_agent
        
        agent = get_compliance_agent("openai/gpt-4o")
        
        assert agent is not None
        assert agent.name == 'compliance'
        mock_agent['compliance'].assert_called_once()

    def test_get_compliance_agent_card(self, mock_load_context):
        """Test that compliance agent card can be created successfully."""
        from buildgentic.compliance.agent import get_compliance_agent_card
        
        agent_url = "http://localhost:8008/a2a/compliance"
        card = get_compliance_agent_card(agent_url)
        
        assert card is not None
        assert card.name == "Compliance Agent"
        assert card.url == agent_url
        assert card.version == "1.0"


class TestAllAgents:
    """Integration tests for all agents."""

    def test_all_agents_can_be_initialized(self, mock_load_context, mock_agent):
        """Test that all agents can be initialized together without errors."""
        from buildgentic.manager.agent import get_manager_agent
        from buildgentic.architect.agent import get_architect_agent
        from buildgentic.developer.agent import get_developer_agent
        from buildgentic.qa.agent import get_qa_agent
        from buildgentic.compliance.agent import get_compliance_agent
        
        model_name = "openai/gpt-4o"
        
        # Initialize all agents
        manager = get_manager_agent(model_name)
        architect = get_architect_agent(model_name)
        developer = get_developer_agent(model_name)
        qa = get_qa_agent(model_name)
        compliance = get_compliance_agent(model_name)
        
        # Verify all agents were created
        assert manager is not None
        assert architect is not None
        assert developer is not None
        assert qa is not None
        assert compliance is not None
        
        # Verify agent names
        assert manager.name == 'manager'
        assert architect.name == 'architect'
        assert developer.name == 'developer'
        assert qa.name == 'qa'
        assert compliance.name == 'compliance'

    def test_all_agent_cards_can_be_generated(self, mock_load_context):
        """Test that all agent cards can be generated without errors."""
        from buildgentic.manager.agent import get_manager_agent_card
        from buildgentic.architect.agent import get_architect_agent_card
        from buildgentic.developer.agent import get_developer_agent_card
        from buildgentic.qa.agent import get_qa_agent_card
        from buildgentic.compliance.agent import get_compliance_agent_card
        
        base_url = "http://localhost:8008/a2a"
        
        # Generate all agent cards
        manager_card = get_manager_agent_card(f"{base_url}/manager")
        architect_card = get_architect_agent_card(f"{base_url}/architect")
        developer_card = get_developer_agent_card(f"{base_url}/developer")
        qa_card = get_qa_agent_card(f"{base_url}/qa")
        compliance_card = get_compliance_agent_card(f"{base_url}/compliance")
        
        # Verify all cards were created
        assert manager_card is not None
        assert architect_card is not None
        assert developer_card is not None
        assert qa_card is not None
        assert compliance_card is not None
        
        # Verify card names
        assert manager_card.name == "Manager Agent"
        assert architect_card.name == "Architect Agent"
        assert developer_card.name == "Developer Agent"
        assert qa_card.name == "QA Agent"
        assert compliance_card.name == "Compliance Agent"
        
        # Verify all cards have required fields
        for card in [manager_card, architect_card, developer_card, qa_card, compliance_card]:
            assert card.version == "1.0"
            assert card.capabilities is not None
            assert card.skills is not None
            assert len(card.skills) > 0
