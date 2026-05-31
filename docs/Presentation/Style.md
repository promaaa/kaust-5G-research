# Writing Style Guide for Research Progress Reports

## Title

- One main title only, no subtitle
- Do not use em-dashes in the title
- Use sentence case only (only capitalize the first letter of the first word, proper nouns, and acronyms)

## Structure

- Start with "What changed since last update" section at the top
- Use numbered lists (1., 2., 3.) for that section, not markdown dash lists
- Use tables for structured data (metrics, configurations, hardware)
- Use YAML code blocks for parameters and configuration values
- End with "Next Steps" section

## Section Headers

- Do not prefix sections with numbers (not "## 1. Problem:", use "## Problem:")
- Use sentence case only (only capitalize the first letter of the first word, proper nouns, and acronyms)
- A colon may follow the header (e.g., "## Problem: 5G bars but no internet")
- When a colon is used, the text after the colon follows sentence case (all lowercase): "## Problem: full IP connectivity over the NR radio link" not "## Problem: Full IP Connectivity Over the NR Radio Link"
- Avoid em-dashes in section headers

## Body Text

- Do not use em-dashes. Use commas, periods, or conjunctives instead.
- Write in clear, concise, natural language.
- Avoid decorative punctuation.

## Lists

- In "What changed since last update", use numbered list format with period
- Keep items concise, one line each
- Use colons to separate the action from the detail: "Radio profile tuned: switched from 51 PRB to 106 PRB"

## Tables

- Use headers without backticks: "| Machine | Role |" not "| Machine | Role |"
- Keep column headers short

## YAML / Code Blocks

- Use triple backtick code blocks with language label (```yaml)
- Use inline backticks for variables, parameters, IP addresses, file paths

## Tone

- Be factual and direct
- Use past tense for completed work
- Use present tense for current state
- Speculation should be labeled as such ("Bottleneck unknown")