# Incident: The False Doctrine Exception

## The Saga
The codebase and several design specifications frequently referenced a "Doctrine Exception Registry." This doctrine claimed that native backend Python modules (such as `AnthropicApiBackend`) were strictly required for advanced features like streaming, model-guided thinking, and tool use, as generic HTTP clients supposedly could not support them.

During an architectural audit of the instrument registry, a developer noticed that another documented native Python backend, `recursive_light`, had no corresponding backend file (`backends/recursive_light.py` did not exist). Instead, it was silently dispatched through a generic OpenAI-compatible/OpenRouter path, yet it functioned perfectly with streaming and tool capabilities.

Further investigation revealed that the native `AnthropicApiBackend` was simply hard-coded in the backend pool builder based on vestigial "Doctrine Exception" comments. In reality, the generic text-in/text-out client adapters were fully capable of executing identical workflows without specialized Python backend overrides.

## The Symptom
Architectural complexity was inflated by maintaining separate native backend paths under the assumption that they were functionally different. Developers spent time debugging custom native handlers when the generic, unified path would have sufficed.

## The Lessons
1. **Verify Claims against Code:** Documentation and comments can carry forward historic "doctrinal" assumptions that are no longer true in the codebase. Verify every claim by reading the actual implementation.
2. **Minimize Special Cases:** Hardcoded exceptions (like the "Doctrine Exception Registry") should be aggressively audited. If a generic interface is sufficient, avoid creating specialized native routes.
3. **Stale Narratives Masquerade as Truth:** Just because a pattern has a persuasive name ("Doctrine Exception") does not make it a runtime safety property or architectural necessity.
