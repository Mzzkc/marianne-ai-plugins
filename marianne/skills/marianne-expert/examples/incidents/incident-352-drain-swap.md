# Incident 352: The Drain Swap Deadlock

## The Saga
During a refactoring of the async runner's execution loop, the development team swapped the standard `communicate()` call for a custom stream draining loop to gain finer control over real-time stdout/stderr capture and redaction.

However, the team did not update the test suite's mocks. The existing tests used `AsyncMock` to mock process stream readers. In python's `asyncio`, an unconfigured `AsyncMock` returning from a read call yields empty bytes (`b""`) instantly and repeatedly. When the new custom drain loop ran against these mocks, it entered a tight, non-yielding infinite loop—appending empty bytes to a buffer while consuming 100% CPU.

Because the loop was CPU-bound and never yielded control back to the asyncio event loop (no `await asyncio.sleep(0)` or yielding reads), it starved all other asynchronous tasks. The memory footprint of the test process rapidly expanded until the OS intervened, terminating the execution.

## The Symptom
Pytest execution runs hung indefinitely or terminated abruptly with exit code `137` (SIGKILL by the Out-Of-Memory/OOM killer). The team initially dismissed these failures as transient local machine flakiness or CI runner resource constraints, leading to several hours of lost productivity before the root cause was investigated.

## The Lessons
1. **OOM is a Signal, Not Flakiness:** Exit code `137` is never random; it is the OS telling you that the process has exhausted system memory. Do not retry or proceed until the OOM vector is diagnosed and patched.
2. **Mock Safety Guards:** Mocks must be designed defensively. The custom drain loop was subsequently hardened to detect non-bytes output or repeated empty reads, raising a mock safety exception instead of looping indefinitely.
3. **Yield Control:** Any custom async draining or polling loop must include yielding bounds to prevent starvation of the asyncio event loop in CPU-heavy or mock-failure scenarios.
