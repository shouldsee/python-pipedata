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

# @property
# def os_stat_result_null(
#     _null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
#     ):
#     os.stat_result(st_mode=33188, st_ino=3567490, st_dev=2053, st_nlink=1, st_uid=1000, st_gid=1000, st_size=2, st_atime=1575340363, st_mtime=1575340597, st_ctime=1575340597)
#     return _null

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

    # dumps(s, cls=MyEncoder )
        # return o.__dict__   
# def file_not_empty(fpath):
#     return os_stat_safe(fpath) != os_stat_result_null

def frame__default(frame=None):
    '''
    return the calling frame unless specified
    '''
    if frame is None:
        frame = inspect.currentframe().f_back.f_back ####parent of caller by default
    else:
        pass    
    return frame

class cached_property(object):
    """
    Descriptor (non-data) for building an attribute on-demand on first use.
    Source: https://stackoverflow.com/a/4037979/8083313
    """
    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)

        # Cache the value; hide ourselves.
        setattr(instance, self._attr_name, attr)
        return attr
    
    
def _open(*a):
    assert isinstance(a[0])


def st_time_size(st):
    return (st.st_mtime, st.st_size)




class IndexedMissingFileError(Exception):
    '''
    index_absent=0, file_absent=1
    suppress if the hooks not enabled
    '''
    pass
class IndexedDiffFileError(Exception):
    '''
    index_absent=0, file_absent=1
    suppress if the hooks not enabled
    '''
    pass



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
    def __repr__(self):
        return "%s(path=%r)"%(self.__class__.__name__, str(self.path))
    def __init__(self,path = None, frame=None):
        frame = frame__default(frame)

        self._symbolicRootNode = SymbolicRootNode(
            self, lambda :None, _dict(),_dict(), None)
        ##### outputNode not enabled
        # self._symbolicOutputNode = AbstractNode(
        #     self, lambda :None, _dict(),_dict(), "_symbolicOutputNode")
        # self._symbolicOutputNode = SymbolicOutputNode(
        #     self,
        #     lambda self:[x() for x in self.input_kw.values()],
        # _dict(), _dict(),0,frame,1,'_symbolicOutputNode',None, )

        # self._symbolicInputNode = RawNode(
        #     self, lambda self:None,
        # _dict(), _dict(),0,frame,1,'_symbolicInputNode',None,)  

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
                # dill.dump( d, f, )
                f.write(dumper._dumps(d))
                # f.write(dill.dumps( d))
                # , f, )
                # dill.dump( d, f, protocol=dill.HIGHEST_PROTOCOL)


        # return _index_file_flush(self.update_queue, self.path)
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


class _INIT_VALUE(object):
    pass
class ChangedNodeError(Exception):
    pass
class ChangedOutputError(Exception):
    pass
returned =  _INIT_VALUE()

class AbstractNode(object):
    ChangedOutputError = ChangedOutputError
    force_index_update = 0 
    tag = None
    def __init__(self, index, func, input_kw, output_kw, name):
        assert not input_kw,"input_kw should be extracted from the function"
        if name is not None:
            func.__name__ = name
        self.func_orig = func
        self._level_stream = {self,}
        self.init_output_kw = output_kw
        self.index = self.indexFile = index
        self._attach_to_root()
        self.runned = 0 
        self.running = 0

    def __repr__(self):
        return "%s(recordId=%s,func=%r,index=%r)" % (
            self.__class__.__name__,
            self.recordId,
            self.func, 
            self.index
            # ':tag:%s'% self.tag if self.tag else ''
            )
        # return '{self.__class__.__name__}()'.format(**locals())
        # return '<Node with func:%s%s>' % (self.func.__name__, 
        #         ':tag:%s'% self.tag if self.tag else '')

    def __call__(self,*a,**kw):
        return self.called_value

    def as_record(self):
        assert 0 ,"TBI"
        # raise Exception("Not initialised")
    def as_snapshot(self):
        return self.as_record()

    @cached_property
    def _changed(self):
        assert 0,"TBI"
    @property
    def recordId(self):
        return self.name
        # assert 0,"TBI"

    @property
    def name(self):
        return self.func.__name__
        pass

    @property
    def func(self,):
        return self.func_orig

    def _get_func_code(self, func):
        sourcefile = self.index.path.replace('.py.index','.py')
        linecache.checkcache( sourcefile )
        # func.__module__.__file__)
        return  inspect.getsource(func, )
        # sourcefile)

    def get_record(self):
        return self.index.get_record( self.recordId, None)        

    def _index_update(self):
        # print ("[UPDATING_INDEX]%s"%self,)
        return self.index.index_file_update( self.recordId, self.as_record())

    def index_update(self):
        return [x._index_update() for x in self.level_stream]

    # def index_update(self):
    #     return self._index_update()

    @property
    def level_stream(self,):
        return self._level_stream

    def merge(self,other):
        self._level_stream.update(other._level_stream)
        other._level_stream.update(self._level_stream)
        other._level_stream = self._level_stream
        return self


    @property
    def changed(self):
        self.initialised_tuples ## lookup upsteram and downstream
        return any([ x._changed for x in self.level_stream])

    @cached_property
    def changed_upstream( self,):
        self.input_kw
        return [x for x in self.input_kw.values() if any([ x.changed_upstream, x.changed])]



    @cached_property
    def called_value(self,*a,**kw):
        return self._get_called_value()
    def _get_called_value(self,*a,**kw):
        '''
        #### evalutaion of value/sideeffects
        Core functionality to make  
        '''
        if self.changed_upstream:
            for x in self.input_kw.values():
                with x.index.realpath().dirname():
                    x.called_value
            # [ x.called_value for x in self.input_kw.values() ]
        if any([self.changed_upstream,self.changed]): 
            self.running = 1
            print("RUNNING:%s"%self)
            input_kw, output_kw = self.initialised_tuples
            args = inspect.getargspec(self.func)[0]
            self.returned = self.func(*([x[1] for x in zip(args, (self, input_kw.values(), output_kw.values() ))]) )

            self.running = 0
            self.runned = 1
        else:
            self.runned = 0

        # if self.runned or self.force_index_update:
        if self.runned:
            _ = '''
            Once running is complete, trigger an update to index file
            '''
            self.index_update()
            self.index_updated = 1
        else:
            self.index_updated = 0
            pass
            # [x.index_update() for x in self.output_kw.values()]
        self.committed = 1
        return self



    ###### initialisation of graph
    def _init_func(self, d=None, skip =1):
        f = self.func
        if d is None:
            d = self._root.input_kw
            # d = frame__default(frame).f_locals
        else:
            pass
            # assert frame is None
        (args, varargs, keywords, defaults) = inspect.getargspec(self.func)
        defaults = defaults or () ## this is for kwargs

        self, input, output = args + ( 3 - len(args) ) * [(),]
        input_kw = _dict([ (key,d[key])  for key in input])
        output_kw = _dict([ (key,d[key])  for key in output])
        return input_kw,output_kw


    @cached_property
    def initialised_tuples(self):
        ### fill default and add decorate to return output_kw
        # self.func = self.func_orig

        input_kw,output_kw = self._init_func()
        self.func.__defaults__ = ( input_kw.values(), output_kw.values())
        # _dec(self.func)
        if output_kw:
            assert not self.init_output_kw,"Decorator must be empty if the 3rd argument exists of funcion %s" % self.func.func_code
            output_kw = output_kw
        else:
            output_kw = self.init_output_kw
        self._output_kw = output_kw
        self._level_stream.update( output_kw.values() )
        return input_kw,output_kw

    @property
    def output_kw(self):
        # input_kw,output_kw = self.initialised_tuples
        self.initialised_tuples
        return self._output_kw
    @property
    def input_kw(self):
        input_kw,output_kw = self.initialised_tuples
        return input_kw

    def _attach_to_root(self,):
        # frame = frame__default(frame)
        self._root = self.indexFile._symbolicRootNode
        # self._root = _root = frame.f_locals['_symbolicRootNode']
        self._root.input_kw[ self.name ] = self


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
