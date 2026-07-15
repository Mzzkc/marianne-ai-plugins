# Incident: Stale Detector Liveness False-Kills

## The Saga
Marianne's conductor uses a `stale_detection` mechanism to monitor running sheets. If a sheet does not write new logs or update its status for longer than the configured `idle_timeout_seconds` (e.g. 10 minutes), the stale-detector assumes the process has hung (e.g., due to an unhandled deadlock or network hang) and kills it.

During a long-running batch job using the `goose` CLI instrument, several sheets executing complex code generation went silent. The processes were actively executing heavy compilation and local linting tasks but did not output stdout or write to log files for about 12 minutes.

The stale-detector scanned the active jobs registry, noted that the sheet's last activity timestamp exceeded the idle timeout, and issued a `SIGKILL` to the process group, terminating the active and healthy run.

## The Symptom
Conductor logs recorded sheets dying unexpectedly with `idle_timeout` failures after ~600 seconds, even though CPU monitors showed the underlying CLI processes were working at 100% capacity. Jobs that were close to finishing were killed prematurely.

## The Lessons
1. **Silence Does Not Equal Death:** A running process that is not outputting logs is not necessarily hung. Log-based idle timeouts are insufficient for active local shell tasks.
2. **Process-Liveness Verification:** To fix this (`d7c2b04`), a process-liveness gate was added to the stale-detector. Before killing any process group, the conductor checks if the subprocess is still actively running at the OS level (via PID checks). If the process is alive and consuming resources, the stale-detector defers termination, preventing false-kills of slow or quiet sheets.
