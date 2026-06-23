import traceback
try:
    import boxmot
    print('OK: imported boxmot', getattr(boxmot, '__version__', 'no-version'))
    import inspect
    print('module file:', inspect.getfile(boxmot))
    print('dir snippet:', [a for a in dir(boxmot) if not a.startswith('_')][:40])
except Exception:
    traceback.print_exc()
