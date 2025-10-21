# BuildGentic

[![Build Status](https://dev.azure.com/ucpdh23/buildgentic/_apis/build/status/buildgentic-CI)](https://dev.azure.com/ucpdh23/buildgentic/_build/latest?definitionId=1)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**BuildGentic** is a proof-of-concept (POC) Agentic AI system designed to autonomously create and manage AI-powered software development workflows. By orchestrating multiple specialized AI agents, BuildGentic transforms business requirements into fully implemented solutions.

## 🌟 Overview

BuildGentic leverages a multi-agent architecture where each agent specializes in a specific aspect of the software development lifecycle. The agents communicate using the Agent-to-Agent (A2A) protocol, enabling seamless collaboration and task delegation.

### Key Features

- 🤖 **Multi-Agent Architecture**: Five specialized agents working in harmony
- 🔄 **A2A Protocol**: Standardized agent-to-agent communication
- 🔗 **Azure DevOps Integration**: Seamless work item management and tracking
- 🚀 **FastAPI Backend**: High-performance REST API server
- 🧠 **LLM-Powered**: Utilizes Google ADK and LiteLLM for intelligent decision-making
- 📦 **Modular Design**: Easy to extend with new agents and capabilities

## 🏗️ Architecture

BuildGentic consists of five core agents:

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Manager** | Project Coordinator | Transforms business requirements into development tasks and manages overall workflow |
| **Architect** | System Designer | Creates architectural designs and technical specifications |
| **Developer** | Code Implementation | Writes and implements code changes based on specifications |
| **QA** | Quality Assurance | Tests and validates code quality and functionality |
| **Compliance** | Standards Enforcement | Ensures code adheres to security, regulatory, and organizational standards |

### Communication Flow

```
Business Requirement → Manager → [Architect, Developer, QA, Compliance] → Implemented Solution
                          ↓
                    Azure DevOps
                    (Work Items)
```

## 📋 Prerequisites

- Python 3.10 or higher
- Azure DevOps account (for work item management)
- OpenAI API key or compatible LLM provider
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ucpdh23/buildgentic.git
cd buildgentic
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the Package

```bash
pip install -e .
```

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Azure DevOps Configuration
AZURE_DEVOPS_ORGANIZATION=your-organization
AZURE_DEVOPS_PROJECT=your-project
AZURE_DEVOPS_PAT=your-personal-access-token
AZURE_DEVOPS_USER_EMAIL=your-email@company.com

# Agent Configuration
AGENT_BASE_URL=http://localhost:8008
MODEL_NAME=gpt-4  # or your preferred model

# OpenAI/LLM Configuration
OPENAI_API_KEY=your-openai-api-key
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_DEVOPS_ORGANIZATION` | Your Azure DevOps organization name | Yes |
| `AZURE_DEVOPS_PROJECT` | Your Azure DevOps project name | Yes |
| `AZURE_DEVOPS_PAT` | Personal Access Token for Azure DevOps | Yes |
| `AZURE_DEVOPS_USER_EMAIL` | Your Azure DevOps email address | Yes |
| `AGENT_BASE_URL` | Base URL where agents are hosted | Yes |
| `MODEL_NAME` | LLM model to use (e.g., gpt-4, claude-3) | Yes |
| `OPENAI_API_KEY` | API key for OpenAI or compatible provider | Yes |

## 💻 Usage

### Starting the Server

Run the server using the command-line interface:

```bash
buildgentic
```

Or directly with Python:

```bash
python -m buildgentic.principal
```

The server will start on `http://0.0.0.0:8008` by default.

### API Endpoints

Once running, the A2A server exposes the following endpoints:

- **Health Check**: `GET /health`
- **Agent Cards**: `GET /a2a/{agent_name}_agent/.well-known/agent.json`
- **Agent Execution**: `POST /a2a/{agent_name}_agent/execute`

Available agents: `manager`, `architect`, `developer`, `qa`, `compliance`

### Example: Health Check

```bash
curl http://localhost:8008/health
```

Response:
```json
{
  "status": "ok"
}
```

### Example: Get Manager Agent Card

```bash
curl http://localhost:8008/a2a/manager_agent/.well-known/agent.json
```

## 🔧 Development

### Project Structure

```
buildgentic/
├── buildgentic/           # Main package
│   ├── architect/         # Architect agent
│   ├── compliance/        # Compliance agent
│   ├── developer/         # Developer agent
│   ├── manager/           # Manager agent
│   ├── qa/                # QA agent
│   ├── tools/             # Utility tools (Azure DevOps integration)
│   ├── code_operations/   # Code manipulation utilities
│   ├── a2a_utils.py       # A2A protocol utilities
│   ├── principal.py       # Entry point
│   └── server.py          # FastAPI server configuration
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
└── README.md             # This file
```

### Building the Package

To create a distribution package:

```bash
python setup.py sdist bdist_wheel
```

The built packages will be available in the `dist/` directory.

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Code Style

This project follows PEP 8 guidelines. Run linters before committing:

```bash
pip install flake8 black
black buildgentic/
flake8 buildgentic/
```

## 🔌 Integration with External Systems

### Azure DevOps

BuildGentic integrates with Azure DevOps to:
- Read and create work items
- Update work item status
- Track development progress
- Link code changes to requirements

The integration is handled through the `tools/tools_azureDevOps.py` module.

### A2A Protocol

Agents communicate using the [Agent-to-Agent (A2A) protocol](https://github.com/google/agent-to-agent), enabling:
- Standard message formats
- Agent discovery via agent cards
- Asynchronous task execution
- Error handling and retries

## 📚 API Documentation

When the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8008/a2a/docs
- **ReDoc**: http://localhost:8008/a2a/redoc

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Google ADK](https://github.com/google/agent-development-kit)
- Powered by [LiteLLM](https://github.com/BerriAI/litellm)
- Uses [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- Integrates with [Azure DevOps](https://azure.microsoft.com/en-us/services/devops/)

## 📞 Support

For issues, questions, or contributions, please:
- Open an issue on [GitHub](https://github.com/ucpdh23/buildgentic/issues)
- Review existing documentation
- Check the API documentation at `/docs`

## 🗺️ Roadmap

- [ ] Enhanced error handling and recovery
- [ ] Support for additional LLM providers
- [ ] GitHub integration alongside Azure DevOps
- [ ] Web UI for agent monitoring
- [ ] Advanced agent orchestration patterns
- [ ] Performance metrics and analytics

---

**Note**: This is a proof-of-concept project. Use in production environments at your own discretion.
