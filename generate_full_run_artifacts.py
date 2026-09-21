from pathlib import Path

from inboxhero import run_end_to_end

root = Path(__file__).resolve().parent
trace = root / 'trace.jsonl'
outbox = root / 'outbox'

if trace.exists():
    trace.unlink()
if outbox.exists():
    for child in outbox.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        else:
            for nested in child.rglob('*'):
                if nested.is_file() or nested.is_symlink():
                    nested.unlink()
            for nested in sorted(child.rglob('*'), reverse=True):
                if nested.is_dir():
                    nested.rmdir()
    outbox.rmdir()

run_end_to_end('inbox.json', dry_run=False, approved=True, trace_path=trace, outbox_dir=outbox)
print(f'TRACE_EXISTS={trace.exists()}')
print(f'TRACE_LINES={sum(1 for _ in trace.open("r", encoding="utf-8") if _.strip())}')
print(f'OUTBOX_EXISTS={outbox.exists()}')
print(f'OUTBOX_FILES={sorted(p.name for p in outbox.iterdir())[:10]}')
