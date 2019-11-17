from ast import *
from os import urandom,walk,getcwd,chdir,rename
from os.path import join,abspath,basename,dirname,exists
from string import printable,ascii_letters,digits
from random import choice
from shutil import rmtree,copytree
from astor import to_source
import importlib

PROJECT = '<PROJECT_PATH>'
LOCAL_PR = join('.',basename(PROJECT))

def random_filename(l=10):
    fn = '0'
    while fn[0] in digits:
        fn = ''.join([choice(ascii_letters+digits) for x in range(l)])
    return fn

class PyFile():
    def __init__(self,path,analyzer):

        self.analyzer = analyzer
        self.sourcepath = path
        self.basename = basename(self.sourcepath)
        self.new_basename = random_filename()+'.py'
        self.new_sourcepath = join(dirname(self.sourcepath),self.new_basename)

        self.basename_stripped = self.basename[:-3]
        self.new_basename_stripped = self.new_basename[:-3]
        self.code = open(self.sourcepath,'r').read()

    def __repr__(self):
        return 'Pyfile(basename={})'.format(self.basename)

    def _get_ast_tree(self):
        return parse(self.code)

    def get_all_imports(self):
        i = ImportGather()
        t = self._get_ast_tree()
        i.visit(t)
        return i.all_imports

    def apply_rename(self):
        rename(self.sourcepath,self.new_sourcepath)

    def apply_new_tree(self,t):
        self.code = to_source(t)
        open(self.sourcepath,'w').write(self.code)


    def load_dependencies(self):
        #only works after analyzer has a full list of all files
        self.dependencies = set()

        for _import in self.get_all_imports():
            subimports = import_obj_to_str(_import)
            for subimport in subimports:
                path = self.analyzer.import_str_to_source(subimport)[0]
                if path:
                    for otherfile in self.analyzer.files:

                        if otherfile.sourcepath == path:
                            self.dependencies.add(otherfile)

    def adjust_imports(self):
        t = self._get_ast_tree()
        print(self.sourcepath)
        i = ImportChanger(self.dependencies)
        i.visit(t)
        self.apply_new_tree(t)

class ImportGather(NodeVisitor):

    def __init__(self):
        self.all_imports = set()

    def visit_Import(self,node):
        self.all_imports.add(node)

    def visit_ImportFrom(self,node):
        self.all_imports.add(node)

class ImportChanger(NodeVisitor):

    def __init__(self,dep):
        self.dependencies = dep

    def visit_Import(self,node):
        self.handle_import(node)

    def visit_ImportFrom(self,node):
        self.handle_import(node)

    def visit_Name(self,node):
        name = node.id
        for dep in self.dependencies:
            if name == dep.basename_stripped:
                node.id = dep.new_basename_stripped

        return node

    def dep_name_in_mod_name(self,dep,modname):
        if dep.basename_stripped in modname:
            return modname.replace(dep.basename_stripped,dep.new_basename_stripped)

    def handle_import(self,n):

        if type(n) == Import:

            all_imports = n.names
            for ind,element in enumerate(all_imports):
                mod_name = element.name
                for dep in self.dependencies:
                    replaced = self.dep_name_in_mod_name(dep,mod_name)
                    if replaced:
                        all_imports[ind].name = replaced

            n.names = all_imports
            return n

        if type(n) == ImportFrom:

            #change strings in module
            for ind,name in enumerate(n.names):
                for dep in self.dependencies:
                    if name.name == dep.basename_stripped:
                        n.names[ind].name = dep.new_basename_stripped

            mod_name = n.module
            #print(self.dependencies,dump(n))
            for dep in self.dependencies:
                replaced = self.dep_name_in_mod_name(dep,mod_name)
                if replaced:
                    n.module = replaced

            return n

class ProjectAnalyzer():

    def __init__(self,root):
        self.root = root
        self.files = [PyFile(f,self) for f in self.iterate_py_files()]

    def iterate_py_files(self):
        lst = []
        for r,f,files in walk(self.root):
            for file in files:
                if file.endswith('.py'):
                    file = abspath(join(r,file))
                    lst.append(file)
        return lst

    def import_str_to_source(self,impstr):
        org_impstr = basename(self.root)+'.'+impstr

        impstr = org_impstr
        while len(impstr.split('.')) > 1:
            try:
                path = importlib.util.find_spec(impstr)
                if path:
                    return path.origin,impstr
                else:
                    raise Exception
            except Exception as e:
                impstr = '.'.join(impstr.split('.')[:-1])

        return None,None

    def obfuscate_imports(self):

        for file in self.files:
            file.load_dependencies()

        for file in self.files:
            file.adjust_imports()

        for file in self.files:
            file.apply_rename()

def import_obj_to_str(i):

    if type(i) == ImportFrom:
        objs = []
        names = i.names
        if names:
            for obj in names:
                try:
                    objs.append(i.module+'.'+obj.name)
                except:
                    pass
            return  objs
        else:
            return [i.module]
    if type(i) == Import:
        return [i.names[0].name]

def main():
    if exists(LOCAL_PR):
        rmtree(LOCAL_PR)

    copytree(PROJECT,LOCAL_PR)
    P = ProjectAnalyzer(abspath(LOCAL_PR))
    P.obfuscate_imports()

if __name__ == '__main__':
    main()
