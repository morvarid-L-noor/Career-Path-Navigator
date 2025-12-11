# Prompt Versioning and Configuration System

## Overview

This directory contains the prompt versioning and configuration system that allows the AI team to:
- Version prompts independently of code deployments
- A/B test between providers and prompt variations
- Roll back to previous versions 
- Track which version generated which outputs

## Directory Structure

```
config/
├── features/
│   ├── career_path_navigator.json          # Active feature configuration
│   └── career_path_navigator.v1.2.2.json   # Archived versions for rollback
├── schema/
│   └── feature_config_schema.json          # JSON schema for validation
└── PROMPT_VERSIONING_README.md             

prompts/
└── career_path_navigator/
    ├── system/
    │   ├── v2.1.txt                        # System prompt versions
    │   └── v2.0.txt
    └── user/
        ├── v1.5.txt                        # User template versions
        └── v1.4.txt
```

## Key Files

### Feature Configuration (`config/features/career_path_navigator.json`)

The main configuration file that defines:
- Feature version (semantic versioning: MAJOR.MINOR.PATCH)
- Prompt version references
- Provider configuration with failover
- A/B testing experiments
- Feature flags
- Output tracking configuration
- Rollback information

### Prompt Files (`prompts/career_path_navigator/`)

Actual prompt templates stored as text files:
- **System prompts**: Define the AI's role and behavior
- **User templates**: Template for user-specific prompts (supports template variables)

### Schema (`config/schema/feature_config_schema.json`)

JSON schema for validating configuration files before deployment.

## Usage Examples

### Creating a New Prompt Version

1. Create a new prompt file: `prompts/career_path_navigator/system/v2.2.txt`
2. Update the feature config to reference the new version:
   ```json
   "prompts": {
     "system": {
       "version": "v2.2",
       "file": "prompts/career_path_navigator/system/v2.2.txt"
     }
   }
   ```
3. Increment the feature version (patch): `1.2.3` → `1.2.4`

### Setting Up an A/B Test

Add an experiment to the `ab_testing.experiments` array:
```json
{
  "experiment_id": "new_prompt_test",
  "name": "Testing New Prompt v2.2",
  "enabled": true,
  "split": {
    "variant_a": {
      "name": "Current Prompt",
      "provider": "primary",
      "traffic_percentage": 50,
      "prompt_version": { "system": "v2.1" }
    },
    "variant_b": {
      "name": "New Prompt",
      "provider": "primary",
      "traffic_percentage": 50,
      "prompt_version": { "system": "v2.2" }
    }
  }
}
```

### Rolling Back

1. Identify the target version from `rollback.previous_versions`
2. Load the archived config file
3. Copy it to become the active configuration
4. Update status to "active"
5. The system will hot-reload automatically

## Versioning Strategy

- **Feature Versions**: Semantic versioning (1.2.3)
- **Prompt Versions**: Independent versioning (v2.1, v1.5)
- **Storage**: Archived versions kept in `config/features/` with `.v{VERSION}.json` suffix

See `prompt_versioning_strategy.md` for detailed explanation.

