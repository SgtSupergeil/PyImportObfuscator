# PyImportObfuscator
This project failed. It does not work correctly.

### Abstract
Because Av's are still using string detection, Projects compiled with Pyinstaller
are leaking strings in the final PE. this can be obfuscated via traditional methods
like encoding or string obfuscation and polymorphic. But Pyinstaller has to "see"
plain import strings in order to load all modules. So when compiling to an exe,
these import strings cannot change. The aim of this program is to change the names
of all files in a python project and adjust all import statements accordingly. This is
done via python's [ast](https://docs.python.org/3/library/ast.html) lib to parse python3 code, which is by far the best method.

*Help on this is very welcome!*

## Workflow
1) Extract all imports from all files in Project
2) Generate new names for files
3) Rename and adjust imports in sourcecode of each file

## Why it fails
Imports are not that simple:

- There may be runtime imports, via exec or importlib
- Currently, handling from . imports is a porblem
- It is hard to adjust all variables because of global and local context
- sometimes, importlib returns None for modules for unknown reasons
