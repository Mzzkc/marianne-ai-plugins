# Backup surfaces and recovery custody

Discover paths instead of assuming that a client is installed. Back up only
accepted target paths and detected adjacent configuration required to restore
the already-integrated surface.

Primary supported surfaces are:

- Marianne built-in and private instrument YAML, musician profiles, technique
  installs, generated catalog, fleet defaults, and current configuration;
- Claude Code user/project settings, plugin manifests, skill assets, and
  model-related environment/config files;
- Codex user/project TOML, instruction/plugin/skill metadata, and model profile
  references;
- Gemini CLI and Antigravity settings, policy/profile files, and model defaults;
- OpenCode JSON/JSONC configuration, agents, commands, and provider references;
- detected Aider, Goose, Crush, Cline CLI, and Ollama model/profile config
  already used by Marianne.

Write compensation metadata before mutation. Preserve exact bytes, SHA-256,
mode, owner/group where permitted, mtime, symlink target, and lstat metadata.
Represent prior absence explicitly so restore removes only a path created by
this transaction. Refuse recursive directory targets.

Keep backups in a timestamped, user-controlled state directory outside target
repositories. Restore in reverse order through staged sibling paths and atomic
replacement where supported. Preflight every backup blob before the first
restore write, then prove every restored byte and metadata field. If restore
fails after beginning, compensate the restore attempt itself. Preserve backup
and working state when exact recovery cannot be proved.

Redact secret values from every public inventory, manifest, backup index, and
receipt. Treat credential, token, secret, cookie, private-key, and equivalent
key names or values as sensitive. Keep operational recovery data protected and
separate from public reports.
