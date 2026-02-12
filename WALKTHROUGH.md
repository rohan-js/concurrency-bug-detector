# Concurrency Bug Detector Walkthrough

## Run

```bash
python3 -m concurrency_detector input.log
```

## Expected Signals in `input.log`

The output should include all of the following:

- `DATA RACE DETECTED`
- `LOST UPDATE`
- `NON-SERIALIZABLE EXECUTION`
- `DEADLOCK DETECTED`

## Clean Edge Case

```bash
python3 -m concurrency_detector input_clean.log
```

Expected result: no races, no lost updates, no deadlocks, and serializable execution.

## Log Format

Each non-empty, non-comment line must be:

`<ThreadID> <OP> <Variable> [Value]`

Where:

- `READ` and `WRITE` require `Value`
- `LOCK`, `UNLOCK`, `WAIT`, `SIGNAL` do not allow `Value`
