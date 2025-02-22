# Multi-Agent System with BlackBox AI Integration

A powerful multi-agent system for building applications locally with AI assistance through BlackBox API integration.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-agent-system
```

2. Set up your BlackBox API key:
   - Get your API key from [BlackBox AI](https://www.useblackbox.io/)
   - Create a `.env` file in the project root:
```bash
BLACKBOX_API_KEY=your_api_key_here
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Using BlackBox AI Features

The system integrates with BlackBox AI for enhanced development capabilities:

1. **Code Completion**
   - Intelligent code suggestions
   - Context-aware completions
   - Multi-language support

2. **Code Search**
   - Search through vast code repositories
   - Find relevant code examples
   - Get implementation suggestions

3. **Documentation Generation**
   - Auto-generate documentation
   - Create README files
   - Document functions and classes

## Creating Projects

Create new projects with built-in BlackBox AI assistance:

```bash
# Create a new React project
python main.py create react my-react-app

# Create a new Vue project
python main.py create vue my-vue-app

# Create a new Flask API
python main.py create flask my-flask-api

# Create a new FastAPI service
python main.py create fastapi my-fastapi-service

# List all projects
python main.py list
```

## Project Templates

Available templates with BlackBox AI integration:

- **Frontend**
  - React
  - Vue

- **Backend**
  - Flask
  - FastAPI

Each template comes with:
- Basic project structure
- Development environment setup
- BlackBox AI integration for code assistance
- Automatic dependency management

## Environment Variables

Create a `.env` file with the following:

```env
BLACKBOX_API_KEY=your_api_key_here
```

## API Documentation

### BlackBox AI Integration

The system uses the BlackBox API for various AI-powered features:

1. Code Completion API
```python
await blackbox.code_completion(prompt="your code context")
```

2. Code Search API
```python
await blackbox.code_search(query="search terms")
```

3. Documentation Generation API
```python
await blackbox.generate_documentation(code="your code")
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
