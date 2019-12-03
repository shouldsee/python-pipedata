import functools
from collections import OrderedDict as _dict
import json
import os,sys

from decorator import decorator
# import types

### getsource
import inspect
import linecache 

## for indexing
import dill
from filelock import FileLock

_DEBUG = 1
# import path as _path
from path import Path
import shutil
# from _inspect_patch import inspect

from pipedata._ast_util import ast_proj
from pipedata._util import cached_property
from attrdict import AttrDict

try:
    from IPython.lib.pretty import pretty
except:
    def pretty(ob):
        return json.dumps(ob,indent=4,default=repr)

def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
    if file_not_empty(fname):
        return os.stat(fname)
    else:
        return _os_stat_result_null

class MyEncoder(json.JSONEncoder):
    # def s
    def default(self, o):
        if isinstance(o, os.stat_result):
            return {"st_mtime": o.st_mtime, "st_size":o.st_size}
        else:
            assert 0,(o,type(o))
class Dumper(object):
    @staticmethod
    def _dumps(s):
        return json.dumps(s, cls=MyEncoder,indent=4)
    @staticmethod
    def _loads(s):
        return json.loads(s)
    pass
dumper = Dumper


def frame__default(frame=None):
    '''
    return the calling frame unless specified
    '''
    if frame is None:
        frame = inspect.currentframe().f_back.f_back ####parent of caller by default
    else:
        pass    
    return frame
    
    
def _open(*a):
    assert isinstance(a[0])


def st_time_size(st):
    return (st.st_mtime, st.st_size)


def _dbgf():        
    import pdb,traceback
    print(traceback.format_exc())
    import traceback
    traceback.print_stack()
    traceback.print_exc()
    pdb.set_trace()    
def _dbgfs():        
    import pdb,traceback
    pdb.set_trace()    



class SymbolicRootNode(object):
    def __init__(self,*a,**kw):
        pass

    @cached_property
    def input_kw(self):
        return _dict()        

class IndexNode(object):
# class Pipeline(object):
    @property 
    def node_dict(self):
        return self._root.input_kw
    def __repr__(self):
        return "%s(path=%r)"%(self.__class__.__name__, str(self.path))
    def __init__(self,path = None, frame=None):
        frame = frame__default(frame)

        self._symbolicRootNode = SymbolicRootNode(
            self, lambda :None, _dict(),_dict(), None)


        if path is None:
            path = os.path.realpath( frame.f_locals['__file__'].replace('.pyc','.py')+'.index')

        self.path = Path(path).realpath()
        self.update_queue = _dict()

    @property
    def _root(self):
        return self._symbolicRootNode

    def realpath(self):
        return self.path

    def index_file_update(self, key, value):
        self.update_queue[key] = value
        return (key,value)
    def index_file_flush(self, ):
        fname = self.path
        with FileLock( fname +'.lock') as lock:
            d = self.records_cached.copy()
            d.update( self.update_queue )
            print("[FLUSHING_INDEX]",self.path)
            with open(fname,"wb") as f:
                f.write(dumper._dumps(d))


    @cached_property
    def records_cached(self):
        if file_not_empty( self.path):
            with open( self.path, "rb") as f:
                # it = ()
                d = dumper._loads(f.read(), )
                # object_pairs_hook=_dict)
        else:
            d = _dict()
        return d        
    def get_record(self,key,default):
        return self.records_cached.get(key,default)

    def make_copy(self, dest, name = None):

        if dest is None:
            dest = 'test_build'
        
        dest = Path(dest)
        # shutil.rmtree(name)
        # os.makedirs_p(dest)
        # dest.makedirs_p()
        assert dest.makedirs_p().isdir(),(dest,)

        fn = self.path.replace('.index','')
        fn = fn.replace('.pyc','.py')
        fn = Path(fn)
        # assert fn.endswith('.py'),fn
        if name is None:
            name = fn.basename()
        assert name.endswith('.py') and fn.endswith('.py'),(fn,name)
        shutil.copy2(fn, dest / name )
        # if self.path.exists():
        _dest = dest / name+'.index'
        _dest.unlink_p()
         # if _dest.exists() else None
        
        #     shutil.copy2( self.path, dest /  name+'.index')

        
        return dest


class RawNode(object):
    pass
class AutoNode(RawNode):
    pass

class TrackedFile(object):    
    pass    

class TrackedFileNode(object):
    pass

class InputTrackedFile(object):
    pass


'''
############################
############################
############################
############################
---------------------------------------
Graveyard ahead
--------------------------------------
'''


def list_flatten_totype(lst, typ, strict=1,):
    _this = list_flatten_totype
    if isinstance(lst, typ):
        return [lst]
    elif isinstance(lst,list) or isinstance(lst,tuple):
        lst = sum((_this(x,typ, strict) for x in lst),[])
        return lst
    else:
        if strict:
            assert 0,(type(lst),repr(lst))
        return [repr(lst)]





def _get_func_code(func):
    del func.__doc__
    code = func.__code__
    # return code.co_code

    _varnames = () ### varnames is already in input_kw
    _code = types.CodeType(
        code.co_argcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code,  ### important
        code.co_consts, #### if docstring is present
        code.co_names,
        (), #  code.co_varnames,
        "", #  code.co_filename,
        "", #  code.co_name,
        0 , # code.co_firstlineno,
        "",  # code.co_lnotab,
        code.co_freevars,
        code.co_cellvars,
    )    
    # return code.co_code
    return (code.co_consts,code.co_code)
    # return _code
