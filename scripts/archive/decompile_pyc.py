import marshal
import struct
import sys

pyc_path = 'd:/autotrace/traceai/utils/__pycache__/base.cpython-39.pyc'

with open(pyc_path, 'rb') as f:
    magic = f.read(4)
    timestamp = f.read(4)
    size = f.read(4)
    code = marshal.load(f)

def disasm(code, indent=0):
    result = []
    prefix = '    ' * indent
    result.append(f'{prefix}Code object:')
    result.append(f'{prefix}  argcount: {code.co_argcount}')
    result.append(f'{prefix}  kwonlyargcount: {code.co_kwonlyargcount}')
    result.append(f'{prefix}  nlocals: {code.co_nlocals}')
    result.append(f'{prefix}  stacksize: {code.co_stacksize}')
    result.append(f'{prefix}  flags: {code.co_flags}')
    result.append(f'{prefix}  names: {code.co_names}')
    result.append(f'{prefix}  varnames: {code.co_varnames}')
    result.append(f'{prefix}  filename: {code.co_filename}')
    result.append(f'{prefix}  name: {code.co_name}')
    result.append(f'{prefix}  lineno: {code.co_firstlineno}')
    result.append(f'{prefix}  lnotab: {code.co_lnotab}')
    result.append(f'{prefix}  freevars: {code.co_freevars}')
    result.append(f'{prefix}  cellvars: {code.co_cellvars}')
    
    for const in code.co_consts:
        if isinstance(const, type(code)):
            result.extend(disasm(const, indent + 1))
        else:
            result.append(f'{prefix}  const: {repr(const)[:100]}')
    
    return result

output = '\n'.join(disasm(code))

with open('d:/autotrace/traceai/utils/base_decompiled.py', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done')
