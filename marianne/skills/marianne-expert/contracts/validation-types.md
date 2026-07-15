# Validation Types and Criteria

Marianne runs validation rules after sheet executions to verify semantic outcomes. This contract specifies the 9 supported validation types, their required/optional parameters, and execution logic.

---

## 1. `file_exists`
Verifies that a specified file exists and is a regular file.

*   **Required Fields:**
    *   `path`: Template path (e.g., `{workspace}/build/output.bin`)
*   **Logic:**
    *   Fails if path is missing, does not exist, or is a directory.

---

## 2. `file_modified`
Checks if a file's modification time (`mtime`) is greater than its snapshot taken before the sheet started.

*   **Required Fields:**
    *   `path`: Template path to check
*   **Logic:**
    *   Fails if the file does not exist.
    *   Saves the initial file timestamp before executing the sheet. Passes only if the file's current `mtime` is newer.

---

## 3. `content_contains`
Performs a plain substring check inside a text file.

*   **Required Fields:**
    *   `path`: Target text file path
    *   `pattern`: Raw string substring to find
*   **Logic:**
    *   Fails if the file does not exist, has unreadable encoding, or doesn't contain the literal pattern.

---

## 4. `content_regex`
Performs a regular expression search on a file's contents.

*   **Required Fields:**
    *   `path`: Target text file path
    *   `pattern`: Regular expression pattern
*   **Logic:**
    *   Uses Python's `re.search` with `re.MULTILINE`.
    *   Fails if pattern syntax is invalid, file is missing, or no match is found.

---

## 5. `command_succeeds`
Spawns an asynchronous shell command and checks for exit code 0.

*   **Required Fields:**
    *   `command`: Shell command string (e.g., `pytest {workspace}/tests`)
*   **Optional Fields:**
    *   `working_directory`: Working directory for execution (defaults to workspace)
    *   `timeout_seconds`: Max execution duration (seconds) before killing
*   **Logic:**
    *   Spawns using `asyncio.create_subprocess_exec` with `bash -c` and `start_new_session=True`.
    *   Aborts immediately with `RuntimeError` if the spawned process group matches the conductor daemon's pgid.
    *   Kills the process group cleanly via `SIGTERM` followed by a 2-second grace period and `SIGKILL` on timeout.

---

## 6. `path_in_scope`
Validates that a resolved path stays within an authorized directory tree.

*   **Required Fields:**
    *   `path`: Path to verify
*   **Optional Fields:**
    *   `path_scope`: Path limit scoping root (defaults to `{workspace}`)
*   **Logic:**
    *   Verifies that the target path resolves inside the scope path using `path.is_relative_to(scope)`.
    *   Prevents directory traversal attacks via `..` or symbolic links.

---

## 7. `field_match`
Checks if a field in a structured JSON or YAML file matches a specified expected value or another file's field.

*   **Required Fields:**
    *   `path`: Target JSON/YAML file path
    *   `field_path`: Dot/bracket path to locate the field (e.g., `users[0].details.email`)
*   **Comparison Values (Must specify at least one):**
    *   `expected_value`: Literal value to compare against
    *   `source_path`: Path to a reference JSON/YAML file
*   **Optional Fields:**
    *   `source_field_path`: Dot/bracket path in reference file (defaults to `field_path`)
*   **Logic:**
    *   Loads JSON/YAML data from target and optionally reference paths.
    *   Resolves nested keys and indices, then compares values for equality.

---

## 8. `file_sha256`
Ensures a file's SHA-256 digest matches a pinned hash string.

*   **Required Fields:**
    *   `path`: Path to the file
    *   `sha256`: Expected hex digest (case-insensitive)
*   **Logic:**
    *   Reads the file in 1MB chunks and hashes it. Fails if the file is missing, is not a regular file, or if the hashes mismatch.

---

## 9. `csv_unique_key`
Asserts that all values in a specific CSV column are unique.

*   **Required Fields:**
    *   `path`: Target CSV file path
    *   `key_field`: Column header name to enforce uniqueness on
*   **Logic:**
    *   Reads CSV file using `csv.DictReader`.
    *   Fails if the file is missing, has no header row, does not contain `key_field`, or has duplicate values in that column. Reports the row numbers of the duplicates.
