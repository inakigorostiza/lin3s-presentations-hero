# Example Decks

Four educational presentations built with this skill on Anthropic's Claude Code documentation. They serve as both proof points and reference output for what the skill produces.

Open any `.pptx` in PowerPoint, or import slide-by-slide into Google Slides via *File → Import slides → Upload → All slides*.

## 1. Claude Code: A Powerful Coding Assistant (`01_Claude_Code_Presentation.pptx`)

16 slides covering coding assistants, tool use, Claude Code setup, and adding context with `CLAUDE.md`. The first deck built and the one where most of the template's quirks were discovered.

Section structure:
1. What is a Coding Assistant?
2. Claude Code Setup
3. Adding Context

## 2. Introduction to Subagents (`02_Introduction_to_Subagents.pptx`)

21 slides covering Claude Code's subagent feature — what subagents are, how to create them, how to design effective ones, and when to use them. Introduces the dark/light Yes/No decision cards used on slide 19 (the Decision Rule).

Section structure:
1. What Are Subagents?
2. Creating a Subagent
3. Designing Effective Subagents
4. Using Subagents Effectively

## 3. Agent Teams (`03_Agent_Teams.pptx`)

23 slides covering Claude Code's experimental Agent Teams feature — coordinating multiple Claude instances with shared task lists and direct teammate-to-teammate messaging. Features the architectural diagram comparing subagents vs agent teams.

Section structure:
1. What Are Agent Teams?
2. Setting Up Your First Team
3. Controlling Teammates
4. How Agent Teams Work
5. Best Practices & Examples

## 4. Claude Code Fundamentals (`04_Claude_Code_Fundamentals.pptx`)

25 slides — the largest deck. Comprehensive coverage of seven topics: coding assistants, setup, context management, conversation control, custom commands, MCP servers, and GitHub integration.

Section structure:
1. What Is a Coding Assistant?
2. Claude Code Setup
3. Adding Context
4. Controlling Context
5. Custom Commands
6. MCP Servers
7. GitHub Integration

## What these have in common

All four decks share the structural patterns the skill encodes:

- **Title** + **Agenda** at the start, **Thank You** at the end
- **Section dividers** with `NN ― TT` indicators (e.g. `02 ― 05`)
- **3-column comparisons** for any list of 3-5 named items
- **Image + text** slides for diagrams and screenshots
- **Code blocks on the right** for commands, configuration, and prompts
- **Problem/Solution cards** on quote slides for decision rules

Each deck reuses the same template — only the content changes. That's the point: the skill turns a `.docx` into a finished `.pptx` while keeping the visual identity consistent across every deck built with it.

## Source documents

The Word documents these were built from aren't included here (they're Anthropic's documentation). If you want to see the source-to-output mapping, the `.pptx` titles match the section titles in [Claude Code's documentation](https://code.claude.com/docs).
