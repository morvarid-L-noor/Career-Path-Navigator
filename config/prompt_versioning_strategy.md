# Prompt Versioning and Configuration Strategy

## Overview

This document explains how the prompt versioning and configuration system works, how Rails consumes these configurations, the versioning strategy, and the rollback process.

## How Rails Consumes Configurations

Rails consumes the configuration system through a lightweight service layer that loads and caches JSON configuration files. The process works as follows:

1. **Configuration Loader Service**: A Ruby service class (`PromptConfigService`) reads the active feature configuration file (e.g., `career_path_navigator.json`) on application startup and caches it in memory.

2. **Hot Reloading**: The service watches for configuration file changes via a file watcher or webhook. When changes are detected, it validates the new configuration and reloads it without requiring a full application restart.

3. **Prompt Resolution**: When a request comes in, Rails calls the configuration service to:
   - Determine which feature version to use (defaults to "active" status)
   - Resolve prompt file paths based on the versioned prompt references
   - Load the actual prompt templates from the file system
   - Apply any A/B test routing logic to select the appropriate variant

4. **Request Processing**: Rails constructs the full prompt by:
   - Loading the system prompt from the referenced file
   - Loading the user template from the referenced file
   - Filling in template variables with user data
   - Sending the complete prompt to the LLM Gateway with metadata about which versions were used

5. **Output Tracking**: After receiving the AI response, Rails logs metadata (feature version, prompt versions, provider, experiment variant) to the database for analysis and traceability.

## Versioning Strategy

### Feature Versioning (Semantic Versioning)

Feature configurations use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes that require code updates or major prompt rewrites
- **MINOR**: New features, new A/B tests, or significant prompt improvements
- **PATCH**: Bug fixes, small prompt tweaks, or configuration adjustments

Example: `1.2.3` indicates version 1, with 2 minor updates, and 3 patch updates.
  1.0.0  → Initial release
  1.1.0  → Added A/B testing (new feature)
  1.2.0  → Added prompt versioning (new feature)
  1.2.1  → Fixed bug in prompt loading
  1.2.2  → Fixed typo in prompt template
  1.2.3  → Current version (small config adjustment)


### Prompt Versioning (Independent Versioning)

Prompts are versioned independently using a simpler scheme (vMAJOR.MINOR):
- Each prompt file has its own version (e.g., `system/v2.1.txt`, `user/v1.5.txt`)
- Prompts can be updated without changing the feature version
- Multiple prompt versions can coexist and be referenced by different feature versions
- This allows fine-grained control over prompt changes

### Storage Structure

```
config/
  features/
    career_path_navigator.json          # Active version
    career_path_navigator.v1.2.2.json   # Archived versions
    career_path_navigator.v1.2.1.json
prompts/
  career_path_navigator/
    system/
      v2.1.txt
      v2.0.txt
    user/
      v1.5.txt
      v1.4.txt
```

### Deployment Process

1. **Development**: AI team creates new prompt files or updates existing ones with new version numbers
2. **Testing**: New configurations are tested in a staging environment
3. **Version Creation**: A new feature version is created by copying the current config and updating version numbers
4. **Validation**: JSON schema validation ensures configuration integrity
5. **Deployment**: Configuration files are committed to version control (Git) and deployed to the config store (S3/GitHub)
6. **Activation**: The new version is marked as "active" in the main configuration file
7. **Archive**: Previous versions are kept in the `rollback.previous_versions` array for quick access

## Rollback Process

The rollback process is designed to be fast and safe, allowing the AI team to revert to a previous configuration within minutes:

1. **Identify Target Version**: The team identifies which version to roll back to (stored in `metadata.rollback_target` or selected from `rollback.previous_versions`)

2. **Load Archived Config**: The system loads the archived configuration file (e.g., `career_path_navigator.v1.2.2.json`)

3. **Validation**: The archived configuration is validated to ensure it's still valid (prompt files exist, providers are configured correctly)

4. **Activation**: The archived version is copied to become the active configuration, and its status is set to "active"

5. **Prompt File Verification**: The system verifies that all referenced prompt files still exist

6. **Hot Reload**: Rails configuration service detects the change and reloads the configuration without restart

7. **Monitoring**: The team monitors metrics to confirm the rollback was successful

8. **Documentation**: The rollback is logged with timestamp, reason, and who performed it

The entire process can be automated via a simple API endpoint or script that takes a version number and performs the rollback, or it can be done manually by updating the configuration files. The key advantage is that rollbacks don't require code deployments—only configuration file updates.

## Key Benefits

- **Independent Versioning**: Prompts can be updated without code deployments
- **A/B Testing**: Multiple prompt versions can be tested simultaneously
- **Quick Rollbacks**: Revert to previous versions in minutes, not hours
- **Full Traceability**: Every output is tagged with version metadata for analysis
- **Safe Experimentation**: Test new prompts on a subset of traffic before full rollout

