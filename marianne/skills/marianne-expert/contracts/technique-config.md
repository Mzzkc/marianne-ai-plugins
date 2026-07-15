# ECS Technique Configuration

Techniques are composable components attached to agent entities following the Entity-Component-System (ECS) pattern. They define capabilities, tool access, and protocols available to musicians.

---

## TechniqueKind

An enumeration defining the category of the technique component.

| Value | Name | Description |
|---|---|---|
| `"skill"` | `SKILL` | Text-based methodology document injected into the prompt cadenza context. |
| `"mcp"` | `MCP` | Tool server integration conforming to the Model Context Protocol. |
| `"protocol"` | `PROTOCOL` | Communication protocols allowing inter-agent interaction (e.g., A2A). |

---

## TechniqueConfig

Pydantic model representing the configuration for a single technique.

### Fields

*   **`kind`** (`TechniqueKind`)
    *   *Description:* The technique category (`skill`, `mcp`, or `protocol`).
*   **`phases`** (`list[str]`)
    *   *Description:* The agent cycle phases when this technique is active (e.g., `['recon', 'work', 'integration']`). A wildcard value of `"all"` makes it active in all phases. Empty list disables it.
*   **`config`** (`dict[str, Any]`, default `{}`)
    *   *Description:* Kind-specific options:
        *   **For `skill`:**
            *   `path` (`str`): Explicit path to the skill document. If omitted, the loader auto-discovers documentation from designated search paths.
        *   **For `mcp`:**
            *   `server` (`str`): The name of the registered MCP server from the pool.
            *   `transport` (`str`): Connection method (`stdio` or `sse`).
        *   **For `protocol`:**
            *   Protocol-specific wiring and routing parameters.
