# Auto-MD

Auto-MD is a CLI tool that automates fetching Jira issue details, managing Git branches, and generating task documentation.

## System Requirements

- Python 3.8+
- Git
- Network connectivity (to access the Jira API)

## Install From Scratch

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/auto-md.git
cd auto-md
```

### 2. Create and Activate a Virtual Environment

#### Using venv (standard)
```bash
# Create the virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

#### Using uv (recommended, faster)
```bash
# Install uv if you have not yet
pip install uv

# Create the virtual environment
uv venv

# Activate the venv the same way as venv above
```

### 3. Install the Project

```bash
# Using standard pip
pip install -e .

# Or using uv (recommended)
uv pip install -e .
```

## Configuration

Before first use, initialize configuration and provide Git and Jira information:

```bash
auto-md init
```

This command will guide you to input the following information:
- Git repository URL
- Git username
- Git password
- Jira username
- Jira password

You can also pass them via command-line flags directly:

```bash
auto-md init --git-url=https://bitbucket.org/example/example.git --git-username=username --git-password=password --jira-username=username --jira-password=password
```

## Usage

### Show Help

```bash
auto-md --help
```

### Run the Full Task Workflow

This command fetches the Jira issue, manages Git branches, generates documentation, and commits to the repository:

```bash
auto-md run DTS-6038
```

The execution includes:
1. Fetching issue information from Jira
2. Finding or creating the related Git branch
3. Generating the task document
4. Committing and pushing the document

### Generate Only the Task Document in the Current Directory

If you only want to generate the task document without Git operations:

```bash
auto-md ai-doc DTS-6038
```

### Generate the Task Document and Save to a Specific Directory

Generate the document and save it under the project's `docs/.tasks` directory:

```bash
auto-md generate-doc DTS-6038
```

## Document Generation

All document generation commands will:
1. Fetch issue information from Jira (including parent issue if present)
2. Use AI to generate a well-structured Markdown document
3. Allow you to provide feedback and regenerate
4. Save the document to the specified location

The generated document contains the following sections:
- Task overview (ID, title, status, etc.)
- Background
- Technical requirements
- Implementation steps
- Notes
- Acceptance criteria
- Related resources

## FAQ

### Configuration

**Problem**: "Configuration not initialized" error
**Solution**: Run `auto-md init` to initialize configuration

**Problem**: Unable to connect to Jira/Git after configuration
**Solution**: Check network connectivity and credentials, then rerun `auto-md init`

### Document Generation

**Problem**: AI-generated document does not meet expectations
**Solution**: During the interactive process, choose "n" and provide concrete suggestions

## Advanced Usage

### Customize Prompts

You can edit the prompt templates in the `prompts.text` file to customize the style and content of generated documents.

### Add Example Documents

Add example Markdown files under the `example` directory. The AI will reference these examples to produce documents with consistent format and style.

## Contributing

Pull Requests and Issues are welcome to help improve this project.

## License

[MIT License](LICENSE)

