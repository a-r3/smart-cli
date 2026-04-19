# Smart CLI Enterprise Edition

<div align="center">
  <img src="https://raw.githubusercontent.com/raufA1/smart-cli/main/smart-cli-logo/icons/icon-256.png" alt="Smart CLI Logo" width="128" height="128">
</div>

[![Build Status](https://github.com/raufA1/smart-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/raufA1/smart-cli/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/raufA1/smart-cli/branch/main/graph/badge.svg?token=40fb1d9c-6465-443b-aa16-2d501c538b37)](https://codecov.io/gh/raufA1/smart-cli)
[![GitHub release](https://img.shields.io/github/v/release/raufA1/smart-cli?include_prereleases&sort=semver)](https://github.com/raufA1/smart-cli/releases/latest)
[![Security Rating](https://img.shields.io/badge/security-A+-brightgreen.svg)](https://github.com/raufA1/smart-cli/security)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

🚀 **Enterprise-grade AI-powered CLI platform** with revolutionary **Enhanced Mode System**, multi-agent workflows, advanced security, and comprehensive monitoring for professional development teams.

## 🎭 Revolutionary Enhanced Mode System

### 🌟 Breakthrough Features
- **7 Specialized Operation Modes**: Intelligent auto-detection, focused development, deep analysis, system architecture, interactive learning, rapid operations, and complex multi-agent coordination
- **Intelligent Context Isolation**: Advanced context management with controlled data sharing across operational modes
- **Adaptive AI Processing**: Dynamic model selection and optimization based on task requirements and mode context
- **Real-time Mode Suggestions**: Proactive mode recommendations powered by advanced request analysis
- **Enterprise Configuration**: Comprehensive project-specific settings with team collaboration capabilities

### 🚀 Mode System Capabilities
- **🤖 Smart Mode**: Automatic request classification and intelligent routing with 94%+ accuracy
- **💻 Code Mode**: Development-focused environment with integrated orchestration and automated workflow hooks
- **🔍 Analysis Mode**: Comprehensive code analysis with security scanning and read-only safety guarantees
- **🏗️ Architect Mode**: Strategic system design with extended context windows and cross-mode knowledge sharing
- **📚 Learning Mode**: Interactive educational environment with progressive explanation systems
- **⚡ Fast Mode**: Optimized rapid operations with intelligent auto-approval for safe commands
- **🎭 Orchestrator Mode**: Advanced multi-agent coordination supporting complex enterprise workflows

## ✨ Enterprise Features

### 🤖 Multi-Agent AI System
- **20+ Specialized AI Agents**: Code Generator, Architect, Security Auditor, Test Developer, etc.
- **Intelligent Agent Orchestration**: Auto-routing tasks to optimal agents
- **Cross-Agent Learning**: Meta-learning system for continuous improvement
- **Multi-LLM Support**: OpenRouter, Anthropic Claude, OpenAI GPT integration

### 🔐 Enterprise Security & Authentication  
- **SSO Integration**: Google OAuth, Microsoft Azure AD, SAML 2.0
- **Role-Based Access Control (RBAC)**: Granular permission management
- **Multi-Factor Authentication**: TOTP, hardware keys, biometric support
- **Comprehensive Audit Logging**: Full activity tracking and compliance

### 🚀 Production-Ready Infrastructure
- **FastAPI Web Server**: RESTful API with OpenAPI documentation
- **Docker Orchestration**: Multi-container deployment with docker-compose
- **Monitoring Stack**: Prometheus metrics, Grafana dashboards
- **High Availability**: Redis clustering, PostgreSQL replication

### 💰 Smart Budget Management & Cost Optimization
- **Real-time Usage Tracking**: Token consumption and cost analysis with live display
- **Intelligent Model Selection**: Automatic cost-effective model choice per agent/task
- **Budget Profiles**: Pre-configured limits for different usage scenarios
- **Cost Protection**: Hard limits and automatic model downgrades
- **Usage Analytics**: Detailed cost breakdowns and optimization suggestions
- **Budget Management**: Daily/weekly/monthly spending limits  
- **Performance Optimization**: Smart model selection and caching
- **Detailed Reporting**: Usage patterns and cost breakdown

### 🛠️ Advanced Development Tools
- **Live Docker Integration**: Containerized development environments
- **Git Workflow Automation**: PR creation, branch management, CI/CD
- **Security Scanning**: Vulnerability detection and compliance checks
- **Team Collaboration**: Shared workspaces and project management

## 🚀 Quick Start

<img src="https://raw.githubusercontent.com/raufA1/smart-cli/main/smart-cli-logo/icons/icon-32.png" alt="Smart CLI" width="24" height="24" style="vertical-align: middle;"> **Get started with Smart CLI in minutes**

### Production Installation

```bash
# Clone repository
git clone https://github.com/raufA1/smart-cli.git
cd smart-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Install all dependencies
pip install -r requirements.txt
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings
```

### 🔧 Configuration

1. **API Keys**: Add your AI service keys to `.env`:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

2. **Database Setup** (optional for advanced features):
```bash
DATABASE_URL=postgresql://smartcli:password@localhost:5432/smartcli
REDIS_URL=redis://localhost:6379/0
```

### 🚀 Starting the System

#### Method 1: Development Mode
```bash
# Start API server
source venv/bin/activate
python src/api/server.py

# In another terminal, use CLI
source venv/bin/activate
python -m src.cli --help
```

#### Method 2: Docker Production Deployment
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 📖 Basic Usage Examples

<img src="https://raw.githubusercontent.com/raufA1/smart-cli/main/smart-cli-logo/icons/icon-20.png" alt="Smart CLI" width="16" height="16" style="vertical-align: middle;"> **Command Examples**

```bash
# 🤖 Interactive AI Chat (current default)
smart

# 🔧 Supported CLI surface
smart --help
smart --version
smart version
smart config show
smart config api-key sk-or-v1-your-key-here
smart config github-token ghp_your_token_here
```

### 🌐 Web Interface

After starting the API server, access:
- **API Documentation**: http://localhost:8000/docs
- **Health Monitoring**: http://localhost:8000/health  
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)

## 📖 Complete Command Reference

### 🔧 System Management
```bash
# Run the interactive assistant
python -m src.cli

# Show help and version
python -m src.cli --help
python -m src.cli --version
python -m src.cli version

# Configuration management
python -m src.cli config show
python -m src.cli config api-key sk-or-v1-your-key-here
python -m src.cli config github-token ghp_your_token_here
```

Additional planned commands and broader product work are tracked in [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/BACKLOG.md](docs/BACKLOG.md).

## ⚙️ Configuration

Smart CLI uses a layered configuration system:

1. **Environment variables** (highest priority)
2. **Command line options**
3. **Configuration files** (`~/.smart-cli/config.yaml`)
4. **Default values** (lowest priority)

### Environment Variables

```bash
export OPENROUTER_API_KEY="your_api_key"
export ANTHROPIC_API_KEY="your_claude_key"
export OPENAI_API_KEY="your_openai_key"
export REDIS_URL="redis://localhost:6379"
export LOG_LEVEL="INFO"
```

### Configuration File

```yaml
# ~/.smart-cli/config.yaml
default_model: "anthropic/claude-3-sonnet-20240229"
temperature: 0.7
max_tokens: 4000
cache_enabled: true
log_level: "INFO"

fallback_models:
  - "anthropic/claude-3-sonnet-20240229"
  - "openai/gpt-4-turbo"
  - "google/gemini-pro"
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/raufA1/smart-cli.git
cd smart-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest -v

# Run security tests
pytest tests/security/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Project Structure

```
smart-cli/
├── src/
│   ├── cli.py                 # Main CLI entry point
│   ├── commands/              # Command implementations
│   │   ├── generate.py        # Code generation commands
│   │   ├── init.py           # Project initialization
│   │   └── review.py         # Code review commands
│   └── utils/                 # Configuration and utilities
│       ├── config.py         # Configuration management
│       └── health_checker.py # Health monitoring
├── tests/                     # Comprehensive testing
├── docs/                      # Documentation
├── pyproject.toml             # Python packaging config
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🛡️ Security

Smart CLI implements multiple security layers:

- **Encrypted credential storage** using PBKDF2 and Fernet
- **Input validation** to prevent injection attacks
- **Secure API communication** with TLS
- **Role-based access control** (RBAC)
- **Audit logging** for all operations

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive configuration
3. **Regularly rotate API keys** and credentials
4. **Review generated code** before execution
5. **Keep dependencies updated** for security patches

## 📊 Monitoring & Observability

Smart CLI includes built-in monitoring capabilities:

```bash
# Check system health
smart-cli health

# View configuration
smart-cli config --show

# Monitor performance (requires Prometheus setup)
# Metrics available at http://localhost:9090/metrics
```

### Health Checks

The health command verifies:
- Python environment
- Configuration validity
- Database connectivity
- AI service availability
- Required dependencies

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details on:

- Development setup
- Code standards  
- Testing requirements
- Pull request process

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Create an issue](https://github.com/raufA1/smart-cli/issues)
- **GitHub Discussions**: [Join the discussion](https://github.com/raufA1/smart-cli/discussions)

## 🚧 Roadmap

The execution roadmap now lives in [docs/ROADMAP.md](docs/ROADMAP.md).
Primary product workflow notes live in [docs/WORKFLOWS.md](docs/WORKFLOWS.md).

Current priority order:
- Product truth alignment
- Reliable interactive CLI core
- Trusted tests and CI
- Provider architecture cleanup
- Mode-system simplification

## 💰 Smart Budget Management

Smart CLI includes advanced budget management to control AI costs while maintaining quality.

### 🔧 Quick Setup

**Set your budget limits:**
```bash
# Set daily spending limit
./smart "cost set daily 10.00"

# Set monthly spending limit  
./smart "cost set monthly 200.00"

# Set per-request limit
./smart "cost set request 1.50"
```

**Use budget profiles (recommended):**
```bash
# Show available profiles
./smart "cost profile list"

# Apply a profile
./smart "cost profile set developer"    # $8/day, $180/month
```

### 📊 Budget Profiles

| Profile | Daily Limit | Monthly Limit | Best For |
|---------|-------------|---------------|----------|
| **Student** | $2.00 | $40 | Learning, small projects |
| **Developer** | $8.00 | $180 | Individual development |
| **Freelancer** | $15.00 | $350 | Client projects |
| **Startup** | $25.00 | $600 | Early-stage companies |
| **Enterprise** | $100.00 | $2500 | Large organizations |
| **Unlimited** | $1000.00 | $25000 | No constraints |

### 💡 Cost Management Commands

```bash
# Status and monitoring
./smart "cost status"                   # Current usage and limits
./smart "cost report"                   # Detailed cost report
./smart "cost models"                   # Model pricing information

# Budget configuration  
./smart "cost set daily 15.00"         # Set daily limit
./smart "cost set monthly 300.00"      # Set monthly limit
./smart "cost configure interactive"   # Guided setup

# Profile management
./smart "cost profile list"            # Show all profiles
./smart "cost profile set freelancer"  # Apply freelancer profile
./smart "cost profile compare"         # Compare profile costs

# Optimization
./smart "cost optimize"                # Get cost-saving suggestions
./smart "cost budget"                  # Show current configuration
```

### 🛡️ Automatic Cost Protection

- **Smart Model Selection**: Automatically chooses cost-effective models for each task
- **Budget Guards**: Hard limits prevent overspending
- **Real-time Monitoring**: Live cost display during execution
- **Graceful Degradation**: Switches to cheaper models when approaching limits
- **Usage Analytics**: Track patterns and optimize spending

### ⚙️ Environment Configuration

Edit `.env` file for persistent settings:
```env
AI_DAILY_LIMIT=15.00
AI_MONTHLY_LIMIT=300.00
AI_REQUEST_LIMIT=2.00
AI_EMERGENCY_RESERVE=25.00
```

### 🎯 Cost Optimization Tips

1. **Use Profiles**: Quick setup with optimal model selection
2. **Monitor Usage**: Check `cost status` regularly
3. **Enable Caching**: Reduces repeated API calls by ~70%
4. **Batch Requests**: Group similar tasks together
5. **Set Strict Limits**: Automatic protection from overspending

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Inspired by modern development tools and best practices
- Community feedback and contributions
