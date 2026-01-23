# RE:GE - Recursive Engine: Generative Entity

[![Tests](https://img.shields.io/badge/tests-1254%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-85%25-green)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

**A symbolic operating system for myth, identity, ritual, and recursive systems.**

---

## The Problem

Traditional software treats data as inert—stored, retrieved, forgotten. But human experience is recursive: memories echo, identities layer, meanings transform over time. There's no system for managing the *living* aspects of personal mythology—the symbols that gain power through repetition, the contradictions that demand resolution, the creative fragments that deserve canonization.

## The Approach

RE:GE reimagines software as a **symbolic operating system**. Instead of files and folders, it operates on *fragments* with charge levels, *organs* that process ritual invocations, and *protocols* that govern transformation. Every piece of content carries weight (charge 0-100), belongs to tiers (LATENT → CRITICAL), and flows through ceremonial logic.

The system is built on:
- **21 Organs**: Specialized processors from HEART_OF_CANON (mythology) to RITUAL_COURT (contradiction resolution)
- **Ritual Syntax**: Invoke organs through ceremonial commands, not function calls
- **Charge Dynamics**: Content gains or decays importance over time
- **Workflow Orchestration**: Multi-step ritual chains with branching and compensation

## The Outcome

A fully functional Python implementation with:
- **1254 tests** at 85% coverage
- **CLI and REPL** for ritual invocation
- **External bridges** to Obsidian, Git, and Max/MSP
- **6 built-in ritual chains** for canonization, grief processing, emergency recovery
- **Extensible architecture** for custom organs and protocols

---

## Installation

```bash
# Clone the repository
git clone https://github.com/4444J99/recursive-engine--generative-entity.git
cd recursive-engine--generative-entity

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# Execute a ritual invocation
rege invoke '::CALL_ORGAN HEART_OF_CANON
::WITH "a memory of significance"
::MODE mythic
::DEPTH standard'

# Check system status
rege status

# Interactive REPL mode
rege repl

# Manage fragments
rege fragments list
rege fragments create "My Fragment" --charge 65

# View system laws
rege laws list

# Execute a ritual chain
rege chain list
rege chain run canonization_ceremony --context '{"charge": 85}'

# External bridges
rege bridge list
rege bridge connect obsidian --path /path/to/vault
```

### REPL Commands

```
:help          Show available commands
:status        Display system status
:organs        List all organs
:modes ORGAN   Show modes for an organ
:vars          Show session variables
:history       Show command history
:quit          Exit REPL
```

### Python API

```python
from rege.parser.invocation_parser import InvocationParser
from rege.routing.dispatcher import get_dispatcher
from rege.organs.registry import register_default_organs

# Initialize system
register_default_organs()
dispatcher = get_dispatcher()
parser = InvocationParser()

# Parse and execute invocation
invocation = parser.parse("""
::CALL_ORGAN HEART_OF_CANON
::WITH "a memory of significance"
::MODE mythic
::DEPTH standard
""")

result = dispatcher.dispatch(invocation)
print(result.output)
```

### Workflow Orchestration

```python
from rege.orchestration import RitualChainOrchestrator
from rege.orchestration.builtin_chains import register_builtin_chains

# Register built-in chains
register_builtin_chains()

# Execute a ritual chain
orchestrator = RitualChainOrchestrator()
execution = orchestrator.execute_chain(
    "canonization_ceremony",
    context={"charge": 85, "symbol": "important_event"}
)

for result in execution.phase_results:
    print(f"{result.phase_name}: {result.status.value}")
```

## Architecture

### Project Structure

```
recursive-engine--generative-entity/
├── rege/                    # Python implementation
│   ├── core/                # Constants, models, exceptions
│   ├── parser/              # Invocation syntax parser
│   ├── routing/             # Soul Patchbay queue system
│   ├── organs/              # 21 organ handlers
│   ├── protocols/           # FUSE01, recovery, enforcement
│   ├── bridges/             # External integrations (Obsidian, Git, Max/MSP)
│   ├── orchestration/       # Workflow orchestration
│   ├── persistence/         # JSON archive system
│   └── tests/               # 1254 tests
├── docs/                    # Documentation
│   ├── api/                 # API reference
│   ├── cli/                 # CLI command reference
│   ├── bridges/             # Bridge setup guides
│   └── examples/            # Usage examples
└── pyproject.toml           # Package configuration
```

### Core Concepts

#### Organs (21 Implemented)

| Organ | Function |
|-------|----------|
| HEART_OF_CANON | Core mythology and canon events |
| MIRROR_CABINET | Reflection and interpretation |
| MYTHIC_SENATE | Law governance |
| ARCHIVE_ORDER | Storage and retrieval |
| RITUAL_COURT | Ceremonial logic and contradiction resolution |
| CODE_FORGE | Symbol-to-code translation |
| BLOOM_ENGINE | Generative growth and mutation |
| SOUL_PATCHBAY | Modular routing hub |
| ECHO_SHELL | Recursion interface |
| DREAM_COUNCIL | Collective processing |
| MASK_ENGINE | Identity layers and persona |
| CHAMBER_COMMERCE | Symbolic economy |
| BLOCKCHAIN_ECONOMY | Immutable records |
| PROCESS_MONETIZER | Creative monetization |
| AUDIENCE_ENGINE | Fan cultivation |
| PLACE_PROTOCOLS | Spatial context |
| TIME_RULES | Temporal recursion |
| ANALOG_DIGITAL | Format translation |
| PROCESS_PRODUCT | Product conversion |
| CONSUMPTION_PROTOCOL | Ethical consumption |
| STAGECRAFT_MODULE | Performance rituals |

#### Invocation Syntax

```
::CALL_ORGAN [ORGAN_NAME]
::WITH [SYMBOL or INPUT]
::MODE [INTENTION_MODE]
::DEPTH [light | standard | extended | full]
::EXPECT [output_form]
```

#### Charge System

| Tier | Range | Behavior |
|------|-------|----------|
| LATENT | 0-25 | Background, minimal processing |
| PROCESSING | 26-50 | Active consideration |
| ACTIVE | 51-70 | Full engagement |
| INTENSE | 71-85 | Canon candidate |
| CRITICAL | 86-100 | Immediate action required |

#### Ritual Chains

Built-in workflow orchestration:

| Chain | Purpose |
|-------|---------|
| `canonization_ceremony` | Canonize high-charge fragments |
| `contradiction_resolution` | Resolve conflicts between fragments |
| `grief_processing` | Multi-step grief ritual |
| `emergency_recovery` | System recovery sequence |
| `seasonal_bloom` | Seasonal mutation cycle |
| `fragment_lifecycle` | Complete fragment lifecycle |

#### External Bridges

| Bridge | Integration |
|--------|-------------|
| Obsidian | Fragment export/import with YAML frontmatter |
| Git | Hook installation, commit logging |
| Max/MSP | OSC communication for audio/visual |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rege --cov-report=term-missing

# Run specific test file
pytest rege/tests/test_orchestration.py -v
```

## Documentation

- **[API Reference](docs/api/)** - Organs, models, protocols
- **[CLI Commands](docs/cli/commands.md)** - Complete command reference
- **[Bridge Guides](docs/bridges/)** - Obsidian, Git, Max/MSP setup
- **[Examples](docs/examples/)** - Usage examples and patterns

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the project roadmap and planned features.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Repository](https://github.com/4444J99/recursive-engine--generative-entity)
- [Issues](https://github.com/4444J99/recursive-engine--generative-entity/issues)
