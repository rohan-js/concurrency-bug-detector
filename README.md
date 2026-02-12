# Concurrency Bug Detector

A modular Python CLI tool that analyzes multithreaded execution logs and reports:

- Data races (read-write and write-write)
- Lost updates
- Non-serializable executions
- Deadlocks (wait-for cycles)

## Project Structure

```text
concurrency_detector/
  parser.py
  model.py
  happens_before.py
  race_detector.py
  serializability.py
  deadlock.py
  reporter.py
  main.py
```

## Requirements

- Python 3.10+

## Quick Start

Run directly from source:

```bash
python3 -m concurrency_detector input.log
```

Or install locally and use the CLI command:

```bash
python3 -m pip install .
concurrency-detector input.log
```

## Log Format

Each non-empty, non-comment line must match:

```text
<ThreadID> <OP> <Variable> [Value]
```

Supported ops:

- `READ` and `WRITE` require a `Value`
- `LOCK`, `UNLOCK`, `WAIT`, `SIGNAL` must not include a `Value`

Example:

```text
T1 READ balance 100
T2 WRITE balance 80
T1 LOCK lockA
T2 WAIT lockA
```

## Testing

Run tests with:

```bash
python3 -m unittest discover -s tests -v
```

## CI

GitHub Actions workflow is included at `.github/workflows/ci.yml` and runs tests on push and pull requests.

## License

MIT License. See `LICENSE`.
