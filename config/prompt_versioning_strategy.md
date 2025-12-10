# Prompt Versioning and Configuration Strategy

## How Rails Consumes Configurations

Rails consumes the configuration system through a lightweight service layer that loads and caches JSON configuration files. A Ruby service class (`PromptConfigService`) reads the active feature configuration file (e.g., `career_path_navigator.json`) on application startup and caches it in memory.

The service watches for configuration file changes via a file watcher or webhook. When changes are detected, it validates the new configuration and reloads it without requiring a full application restart.

When a request comes in, Rails calls the configuration service to determine which feature version to use, resolve prompt file paths based on versioned prompt references, load the actual prompt templates from the file system, and apply any A/B test routing logic to select the appropriate variant.

Rails constructs the full prompt by loading the system prompt from the referenced file, loading the user template from the referenced file, filling in template variables with user data, and sending the complete prompt to the LLM Gateway with metadata about which versions were used. After receiving the AI response, Rails logs metadata (feature version, prompt versions, provider, experiment variant) to the database for analysis and traceability.

## Versioning Strategy

Feature configurations use semantic versioning (MAJOR.MINOR.PATCH): MAJOR for breaking changes that require code updates, MINOR for new features or significant prompt improvements, PATCH for bug fixes or small prompt tweaks. Example: `1.2.3` indicates version 1, with 2 minor updates, and 3 patch updates.

Prompts are versioned independently using a simpler scheme (vMAJOR.MINOR). Each prompt file has its own version (e.g., `system/v2.1.txt`, `user/v1.5.txt`). Prompts can be updated without changing the feature version, and multiple prompt versions can coexist and be referenced by different feature versions, allowing fine-grained control over prompt changes.

**Storage Structure:**
```
config/features/career_path_navigator.json          # Active version
config/features/career_path_navigator.v1.2.2.json   # Archived versions
prompts/career_path_navigator/system/v2.1.txt       # System prompt versions
prompts/career_path_navigator/user/v1.5.txt         # User template versions
```

## Rollback Process

The rollback process is designed to be fast and safe, allowing the AI team to revert to a previous configuration within minutes:

1. **Identify Target Version**: Select from `rollback.previous_versions` or `metadata.rollback_target`
2. **Load Archived Config**: Load the archived configuration file (e.g., `career_path_navigator.v1.2.2.json`)
3. **Validation**: Validate the archived configuration (prompt files exist, providers configured correctly)
4. **Activation**: Copy archived version to become active configuration, set status to "active"
5. **Prompt File Verification**: Verify all referenced prompt files still exist
6. **Hot Reload**: Rails configuration service detects change and reloads without restart
7. **Monitoring**: Monitor metrics to confirm rollback success
8. **Documentation**: Log rollback with timestamp, reason, and who performed it

The entire process can be automated via a simple API endpoint or script that takes a version number and performs the rollback. The key advantage is that rollbacks don't require code deployments—only configuration file updates.
