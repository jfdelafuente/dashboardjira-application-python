# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Specify-based project** - a spec-driven development workflow system that uses feature specifications to drive implementation through structured phases. The repository uses custom slash commands to orchestrate the workflow from specification through planning, task generation, and implementation.

## Workflow Architecture

### Phase-Based Development Process

The Specify workflow follows a strict phase progression:

1. **Specification Phase** (`/speckit.specify`) - Creates feature specifications from natural language descriptions
2. **Planning Phase** (`/speckit.plan`) - Generates technical implementation plans from specifications
3. **Task Generation** (`/speckit.tasks`) - Breaks plans into actionable, dependency-ordered tasks
4. **Implementation Phase** (`/speckit.implement`) - Executes tasks according to the plan

### Supporting Commands

- **Constitution Management** (`/speckit.constitution`) - Define project-wide principles and constraints
- **Clarification** (`/speckit.clarify`) - Resolve underspecified requirements in specifications
- **Analysis** (`/speckit.analyze`) - Cross-artifact consistency validation before implementation
- **Checklist Generation** (`/speckit.checklist`) - Create domain-specific quality checklists
- **GitHub Issues** (`/speckit.taskstoissues`) - Convert tasks to GitHub issues with dependency tracking

## Key Concepts

### Feature Branches and Specs

- Features are tracked in numbered branches: `###-feature-name` (e.g., `001-user-auth`)
- Each feature has a directory under `specs/###-feature-name/`
- Feature directories contain:
  - `spec.md` - Technology-agnostic feature specification
  - `plan.md` - Technical implementation plan (stack, architecture, phases)
  - `tasks.md` - Dependency-ordered implementation tasks
  - `research.md` - Technical decisions and rationale (optional)
  - `data-model.md` - Entity definitions and relationships (optional)
  - `contracts/` - API specifications (OpenAPI/GraphQL schemas) (optional)
  - `quickstart.md` - Integration test scenarios (optional)
  - `checklists/` - Domain-specific quality validation checklists (optional)

### Branch Number Allocation

The system auto-increments feature numbers by checking:
1. Remote branches matching `###-*` pattern
2. Local branches matching `###-*` pattern
3. Directories in `specs/` matching `###-*` pattern

Takes the maximum number found + 1.

### User Story-Centric Task Organization

Tasks are organized by **user stories** (not by technical layers):
- Each user story becomes its own phase
- Stories are prioritized (P1, P2, P3)
- Each story must be independently testable
- Tasks within a story are labeled `[US1]`, `[US2]`, etc.

## PowerShell Helper Scripts

The `.specify/scripts/powershell/` directory contains utility scripts:

- **create-new-feature.ps1** - Create feature branch and directory structure
  - Auto-generates branch names using keyword extraction and stop word filtering
  - Supports manual short names via `-ShortName` parameter
  - Enforces GitHub's 244-byte branch name limit

- **check-prerequisites.ps1** - Validate workflow prerequisites
  - Modes: `-RequireTasks`, `-IncludeTasks`, `-PathsOnly`
  - Returns JSON with feature paths and available documents

- **setup-plan.ps1** - Initialize planning phase artifacts

- **update-agent-context.ps1** - Update AI agent context files with tech stack

### Common Script Parameters

- `-Json` - Output in JSON format for machine parsing
- `-Help` - Display usage information
- All scripts resolve repository root via git or `.specify` marker

## Constitution System

The `.specify/memory/constitution.md` file defines **non-negotiable project principles** that guide all technical decisions and implementation choices. The current constitution (v1.0.0, ratified 2025-12-21) establishes four core principles:

### Core Principles

1. **Code Quality Standards** - Style guides, static analysis, documentation, no duplication
2. **Testing Discipline** - TDD mandatory, Red-Green-Refactor cycle, 80% unit coverage minimum
3. **User Experience Consistency** - Consistent patterns, actionable errors, WCAG 2.1 AA compliance
4. **Performance Requirements** - P95 latency targets, resource limits, optimization mandatory

### Quality Gates by Phase

- **Specification**: Testable requirements, measurable success criteria, max 3 clarifications
- **Planning**: Tech stack aligns with performance, architecture supports testability
- **Implementation**: All tests pass, static analysis clean, performance validated
- **Review**: Constitution compliance verified, breaking changes documented

### Technical Decision Framework

Prioritize: Correctness → Testability → Performance → UX → Simplicity → Maintainability

**Complexity justification required for:**
- New frameworks/dependencies
- Advanced patterns (CQRS, event sourcing)
- Custom abstractions
- Performance optimizations that sacrifice readability

### Constitution Authority

- Constitution violations detected during `/speckit.analyze` are flagged as CRITICAL
- Violations must be fixed OR justified in plan.md Complexity Tracking table
- Constitution supersedes all other coding standards
- Versioning: `MAJOR.MINOR.PATCH` (increment based on governance impact)

Constitution changes propagate to:
- `.specify/templates/plan-template.md` (Constitution Check section)
- `.specify/templates/spec-template.md` (scope/requirements alignment)
- `.specify/templates/tasks-template.md` (task categorization)

## Templates

Located in `.specify/templates/`:

- **spec-template.md** - Feature specification structure (technology-agnostic)
- **plan-template.md** - Implementation plan structure (tech-specific)
- **tasks-template.md** - Task breakdown format with strict checklist syntax
- **checklist-template.md** - Quality validation checklist format
- **agent-file-template.md** - AI agent context file structure

### Task Format Requirements (CRITICAL)

Every task MUST follow this exact format:

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

Components:
- Checkbox: `- [ ]` (markdown checkbox)
- Task ID: `T001`, `T002`, etc. (sequential)
- `[P]` marker: Optional, indicates task can run in parallel
- `[Story]` label: `[US1]`, `[US2]` - REQUIRED for user story phase tasks
- Description: Clear action with exact file path

Examples:
- `- [ ] T001 Create project structure per implementation plan`
- `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- `- [ ] T012 [P] [US1] Create User model in src/models/user.py`

## Specification Quality Standards

Specifications must be:
- **Technology-agnostic** - No frameworks, languages, databases, or implementation details
- **User-focused** - Written for business stakeholders, not developers
- **Testable** - Requirements must have clear acceptance criteria
- **Measurable** - Success criteria must be quantifiable

### Clarification Limits

- Maximum **3 `[NEEDS CLARIFICATION]` markers** per specification
- Only use for critical decisions affecting scope/security/UX
- Make informed guesses for everything else, document in Assumptions section
- Prioritize: scope > security/privacy > user experience > technical details

## Important Workflow Rules

### When Running Commands

1. **Always use PowerShell scripts** - They're optimized for the workflow and handle edge cases
2. **Always pass `-Json` flag** - Parse JSON output for structured data
3. **Quote arguments with spaces** - PowerShell syntax: `"I'm building a feature"`
4. **Check prerequisites first** - Run `check-prerequisites.ps1` before planning/implementation phases

### Phase Progression

- Never skip phases - each phase builds on artifacts from the previous one
- `/speckit.specify` creates the spec - run this first for new features
- `/speckit.plan` requires `spec.md` to exist
- `/speckit.tasks` requires `plan.md` to exist
- `/speckit.implement` requires `tasks.md` to exist

### Task Execution

- Respect task dependencies - sequential tasks must run in order
- `[P]` marked tasks can run in parallel (different files, no dependencies)
- Mark tasks complete in `tasks.md` by changing `- [ ]` to `- [X]`
- Halt execution on non-parallel task failures

## Modified Files vs Untracked Files

The git status shows **modified files** in `.claude/commands/` and `.specify/templates/`. These are template files that are tracked in git. The untracked `.specify/scripts/powershell/` directory contains the actual PowerShell scripts.

When working in this repository:
- Changes to slash commands affect workflow behavior
- Changes to templates affect artifact structure for new features
- Existing feature specs/plans/tasks are not auto-updated when templates change
