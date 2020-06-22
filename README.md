# PyImportObfuscator
Module level obfuscation in python projects for Pyinstaller builds.

### Abstract
Av's are still using static string detection. Python projects compiled with [Pyinstaller](https://www.pyinstaller.org)
are leaking certain strings from the source python files in the final PE. This can be obfuscated via traditional methods
like encoding, encryption or string obfuscation. But one type of strings that is particularly hard to obfuscate are import strings. The reason for that is that Pyinstaller has to read import strings like “`from my lib import MyClass“` in plain text. If you were to put a base64 encoded snippet into an exec statement (ie obfuscating it), Pyinstaller would not register the import and thus not include the needed library into the bundled application. This is a great chance for antivirus engines, because those hard to change string signatures will be part of the final exe generated, making it harder for red teams to run
for example the [LaZagne Project](https://github.com/AlessandroZ/LaZagne) in pentest engagements.

The aim of this project is to explore the possibility of renaming all packages in a python3 project, across multiple files. This requires detecting system and user level packages, renaming files and then adjusting all python statements that refer to those. [ast](https://docs.python.org/3/library/ast.html) is utilized to find modules in the source code.

*Help on this is very welcome!*

## Workflow
1) Extract all imports from all files in Project
2) Generate new names for files
3) Rename and adjust imports in source code of each file

## Problems 
Imports are not that simple:

- There may be run time imports, via exec or import lib
- Currently, handling from . imports is a problem
- It is hard to adjust all variables because of global and local context
- sometimes, import lib returns None for modules for unknown reasons.
