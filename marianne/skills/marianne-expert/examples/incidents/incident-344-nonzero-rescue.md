# Incident 344: The Non-Zero Exit Rescue

## The Saga
In one of the complex pipeline scores (`scores-internal/repro-344-obs1-cli.yaml`), a CLI sheet ran a sequence of shell operations: committing a generated report to git and then executing an exit command with status 1 (`exit 1`) to trigger a downstream branch condition.

Under the initial baton design, any non-zero exit code returned by a sheet's execution process was treated as a fatal execution failure. The baton immediately aborts the current run, markings the sheet as `FAILED` and scheduling retries.

However, in this case, the sheet's objective was to write the file, and its declared post-execution validations were `file_exists` and `content_contains` checks on that exact file. Although the command completed its output objective and all user-configured validation checks passed successfully, the baton still aborted the run because of the `exit 1` status.

## The Symptom
The job would repeatedly fail and retry on sheet 1 despite the output file being completely written, valid, and present. This caused frustration as the system reported failure for a functionally successful task.

## The Lessons
1. **Validations Are the Ground Truth:** The ultimate arbiter of a sheet's success is its validation suite, not the exit code of the shell command. If all user-configured validations pass, the task's contract has been satisfied.
2. **The Non-Zero Rescue Pattern:** The baton was patched (`18226a9`) to introduce the "Non-Zero Exit Rescue" pattern. If a shell command exits with a non-zero status but all validations pass, the baton logs a `nonzero_exit_rescued` event and marks the sheet execution as `COMPLETED` successfully.
