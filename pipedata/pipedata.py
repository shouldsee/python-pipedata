import functools
from collections import OrderedDict as _dict
import json
import os,sys

from decorator import decorator
import types

### getsource
import inspect
import linecache 

## for indexing
import dill
from filelock import FileLock

_DEBUG = 1

# from _inspect_patch import inspect

from _ast_util import ast_proj
def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

@property
def os_stat_result_null(
    _null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
    ):
    return _null

def os_stat_safe(fname):
    if file_not_empty(fname):
        return os.stat(fname)
    else:
        return os_stat_result_null

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

class BaseFile(object):
    _DEBUG = _DEBUG
    DEBUG_NO_CACHE = 0
    VERBOSE = 0
    def __repr__(self,):
        return "%s(%r)"%(self.__class__.__name__,self.path)

    def __call__(self,*a,**kw):
        return self
    def __init__(self, path):
        self.path=path
    def open(self,*a, **kw):
        return open(self.path,*a, **kw)
    
    # @cached_property
    @property
    def cached_index_dict(self,):
        '''
        !!! This should be cached based on mtime
        '''
        return index_file_read(self.path)

    
def st_time_size(st):
    return (st.st_mtime, st.st_size)

def index_get_default(frame=None):
    frame = frame__default(frame)
    parent = BaseFile(frame.f_locals['__file__'].replace('.pyc','.py')+'.index')
    # print parent.path
    return parent

def index_file_read(fname,):
    # with FileLock( fname +'.lock') as lock:
    if file_not_empty(fname):
        with open( fname, "r") as f:
            # it = ()
            d = dill.load(f, )
            # object_pairs_hook=_dict)
    else:
        d = _dict()
    return d



update_queue = _dict()
def index_file_update( key, value):
    update_queue[key] = value

def index_file_flush(fname=None,frame=None):
    if fname is None:
        fname = index_get_default(frame__default(frame)).path

    with FileLock( fname +'.lock') as lock:
        d = index_file_read(fname)
        d.update( update_queue )
        with open(fname,"w") as f:
            dill.dump( d, f)

# def code_index_update( fname, key)

            # return f.read()


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


class TrackedFile(BaseFile):    

    # def index
    HOOKS_ENABLED_LIST = [
        "indexed_missing_file",
        "indexed_diff_file",
    ]


    def _hook_indexed_missing_file(self):
        if "indexed_missing_file" in self.HOOKS_ENABLED_LIST:
            ### when file is indexed but absent
            raise IndexedMissingFileError(os.getcwd()+'|'+str(self)+str(self.indexFile))
    def _hook_indexed_diff_file(self):
        if "indexed_diff_file" in self.HOOKS_ENABLED_LIST:
            raise IndexedDiffFileError(os.getcwd()+'|'+str(self)+str(self.indexFile))

    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        if self.DEBUG_NO_CACHE:
            return 1
        rec = self.indexFile.cached_index_dict.get( self.path , None)
        # file_absent = os_stat_safe(self.path) == os_stat_result_null
        file_absent = not file_not_empty(self.path)
        index_absent = rec is None

        states = [] 
        if file_absent:
            val = 1
            states.append('TARGET_ABSENT')

        if index_absent:
            val = 1
            states.append("INDEX_ABSENT")

        if file_absent and not index_absent:

            self._hook_indexed_missing_file()

        if not (file_absent or index_absent):

            v1 = st_time_size( rec['stat_result'])
            v2 = st_time_size( os_stat_safe(self.path) )
            if  v1!= v2:
                if self.VERBOSE:
                    print (self.path, zip(v1,v2))
                val=1; states.append("DIFF")
                self._hook_indexed_diff_file()
            else:
                val=0; states.append("SAME")

        return val,states
        # return (0,"SAME")

    def index_update(self,):
        # if not file_not_empty(self.path):
        #     path.Path(self.path).dirname()
        #     os.path.makedirs_p()
        index_file_update( 
            self.path, 
            dict(stat_result = os.stat( self.path ))
        )
        return 

    @cached_property
    def changed(self):
        val,states  = self._changed()
        if self.VERBOSE:
            print("[CheckingChange]:{self.path}.changed={val}.state={states}".format(**locals()))
        return val

    
    def __init__(self, path, frame=None):
        self._frame = frame__default(frame)
        self.indexFile = self._frame.f_locals['_indexFile']
            # parent = index_get_default(self._frame)
        del self._frame

        super(TrackedFile,self).__init__(path)

def frame_init(frame=None):
    '''
    Adding constants to this frame
    '''
    frame = frame__default(frame)
    print ("[FRAME_INIT] _symbolicInputNode, _symbolicOutputNode")
    indexFile = frame.f_locals['_indexFile'] = index_get_default(frame)
    # indexFile = frame.f_locals['_indexFileNode'] = index_get_default(frame)


    frame.f_locals['_symbolicRootNode'] = rootNode = SymbolicRootNode(
        lambda self:[x() for x in self.input_kw.values()],
        _dict(), _dict(),0,frame,1,'_symbolicRootNode', None)

    frame.f_locals['_symbolicOutputNode'] = symout  = SymbolicOutputNode(
        lambda self:[x() for x in self.input_kw.values()],
        _dict(), _dict(),0,frame,1,'_symbolicOutputNode',None)

    frame.f_locals['_symbolicInputNode'] = symin  =  RawNode(lambda self:None,
        _dict(), _dict(),0,frame,1,'_symbolicInputNode',None)

    return symin,symout,indexFile

# _counter = -1
class OutputTrackedFile(TrackedFile):
    pass
#     counter = -1
#     def get_node_name(self, name):
#         fmt = "OutputTrackedFile_%s"
#         if name is None:
#             self.__class__.counter += 1
#             return fmt % ("%04d"% self.__class__.counter)
#         else:
#             return fmt % name

#     def __init__(self, path, parent=None,frame=None, name = None):
#         frame=frame__default(frame)
#         name = self.get_node_name(name)
#         frame.f_locals['_symbolicRootNode'].input_kw[name] = self
#         super(OutputTrackedFile,self).__init__(path, frame=frame)

class InputTrackedFile(TrackedFile):
    '''
    '''
    # counter = _counter
    counter = -1
    def get_node_name(self, name):
        if name is None:
            fmt = "InputFileNode_%s"
            self.__class__.counter += 1
            return fmt % ("%04d"% self.__class__.counter)
        else:
            return name

    def __init__(self, path, parent=None,frame=None, nodeClass = None , force = 0, skip=1, name=None):
        if nodeClass is None:
            nodeClass = AutoNode
        frame = frame__default(frame)
        print (self.__class__.counter+1,path,)
        # import traceback
        # traceback.print_stack()
        # print self.get_node_name(name)
        self.node = nodeClass( 
            lambda self, _symbolicInputNode:None,
            input_kw = _dict(), output_kw={'FILE':self}, force=force,
            frame = frame, skip=skip,
            name = self.get_node_name(name),
            tag = path,
             # % path.replace(),
            )
        self.node.path = path

        ### create
        super(InputTrackedFile, self).__init__(path,frame=frame)

    @property
    def changed_upstream(self):
        return self.node.changed_upstream

    def _hook_indexed_diff_file(self):
        print("INPUT_FILE_CHANGED:%s"%self)
        # raise IndexedDiffFileError(self)        
    @property
    def called_value(self):
        return self.node.called_value


    pass

def func__addSelf(f):
    def g(*a,**kw):
#         kw['self'] = f
        return f(f,*a,**kw)
    return functools.wraps(f)(g)

def func__fill_defaults(skip=0,frame=None, d=None):
    '''
    Fill positonal argument using values from frame
    '''

    def _dec(f,d=d):
        if d is None:
            d = frame__default(frame).f_locals
        else:
            assert frame is None
        (args, varargs, keywords, defaults) = inspect.getargspec(f)
        defaults = defaults or () ## this is for kwargs
        # print args,defaults
        for key in args[ skip:len(args) - len(defaults)][::-1]:
            defaults = (d[key],)+defaults
        f.__defaults__ = defaults
        # print defaults
        return f
#             (args, varargs, keywords, defaults) = inspect.getargspec(func)
    return _dec




class _INIT_VALUE(object):
    pass
class ChangedNodeError(Exception):
    pass
returned =  _INIT_VALUE()
class RawNode(object):
    '''
    Decorate a function by
        filling the positional arguments
         attaching a dict of output nodes
         attaching methods related
         :params:skip: how many positional argument to skip 
         Node['returned'] is not cached and should not 
        
    See help(self.func) for original function docstring

    '''        
    _DEBUG = _DEBUG
    returned = returned
    AUTO_UPDATE_OUTPUT = 0
    VERBOSE = 1
    OLD = 0
    force_index_update = 0 
    _root = None


    def __repr__(self):
        return '<Node with func:%s%s>' % (self.f.__name__, 
                ':tag:%s'% self.tag if self.tag else '')
    def __getitem__(self,key):
        return self.output_kw[key]

    def __call__(self,*a,**kw):
        return self.called_value
    
    def __init__(self, func, input_kw, output_kw, force, frame, skip, name, tag):
        if name is not None:
            func.__name__ = name
        self.func_orig = func
        # self.func_orig_source = _get_func_source(func)
        self.f = func
        self.tag = tag
        # self.input_kw = input_kw  or _dict()
        self.output_kw = output_kw
        self.force = force
        # self._frame = 
        frame = frame__default(frame)
        self.indexFile = frame.f_locals['_indexFile']
        self._attach_to_root(frame)
        # self._attach_func(func, frame, skip)
        # del self._frame
        return     
    def func(self,*a,**kw):
        raise Exception("Not initialised")

    @cached_property
    def changed(self):
        '''
        node.changed indicate the result needs re-computation, if:
          - its code is changed 
          - its output is changed
        '''
        print("CHECKING_NODE:%s"%self)        
        if self.force:
           print("CHANGED_FORCED:%s"%self)
           return 1
        if self._changed_code()[0]:
            print( "CHANGED_CODE:%s"%self)
            return 1
        if self._changed_output():
            print( "CHANGED_OUTPUT:%s"%self)
            # print( "CHANGED_OUTPUT:%s\n%s"%(self,))
            print (self,self._changed_output())
            return 1

        if self.OLD:
            if self.changed_upstream:
                print("CHANGED_UPSTREAM:%s"%self)
                return 1
    
        print("[CHANGED_SAME]:%s"%self)
        return 0


    @cached_property
    def changed_upstream( self,):
        self.input_kw
        # it = self.input_kw.values()
        # for x in it:
        #     print self, x, x.changed_upstream,x.changed
        # print (self,zip([x.changed for x in it],it)
        return [x for x in self.input_kw.values() if x.changed_upstream or x.changed]

    # def _changed_upstream(self):
    #     return self._changed_upstream_cache

    def _changed_output(self):
        lst = []
        for k,v in self.output_kw.iteritems():
            if 0:
                pass
            elif isinstance(v,TrackedFile):
                if v.changed:
                    lst.append( (k,v) )
            else:
                assert 0, (k,type(v),v)
        return lst

    def _hook_indexed_diff_file(self):
        return 1

    def _hook_indexed_missing_file(self):
        return 1

    def _hook_code_input_kw_smaller(self):
        _ = '''
        a shrinking input_kw should not trigger a rerun
        '''
        self.force_index_update = 1
        return 0

    def _changed_code(self):
        '''
        Detect whether the underlying function has changed when compared to 
        '''
        # if self._DEBUG:
        #     return (0,'DEBUG')

        rec = self.indexFile.cached_index_dict.get( self.name, None)
        file_absent = False ### this is when a node is deleted from a file
        index_absent = rec is None

        states = [] 

        # ### not relevant
        if file_absent:
            val = 1
            states.append('TARGET_ABSENT')

        if index_absent:
            val = 1
            states.append("INDEX_ABSENT")

        if file_absent and not index_absent:
            val = 1
            self._hook_indexed_missing_file()

        if not (file_absent or index_absent):
            v1 = rec['data']
            v2 = self.as_data()['data']
            assert len(v1) == len(v2),(v1.keys(),v2.keys())

            _dbg = 0            
            for v in (v1,v2):
                src =  '\n'.join(v.pop('func_sourcelines'))
                v['func_ast_tree'] = _tree = ast_proj(src) ###  exclude from comparision
                # print '\n'.join()
                if _dbg:
                    print src
                    print _tree

            if _dbg:
                if self.name =='out10':
                    print (self,self.func_orig.func_code,v1==v2)
            #     if 'line 32' in repr(self.func_orig.func_code):
                    import pdb,traceback
                    print(traceback.format_exc())
                    import traceback
                    traceback.print_stack()
                    traceback.print_exc()
                    pdb.set_trace()
                # print '\n'.join(v1['func_sourcelines'])
                # print '\n'.join(v2['func_sourcelines'])
                # print vars(self)
                # print globals()
            # sys.stdout.write("%s\n"%[(k,oldv==newv),oldv,newv])


            if  v1 != v2:
                diff = _dict()
                for (k, oldv),(k1, newv) in zip(v1.items(),v2.items()):
                    if self.VERBOSE >= 2:
                        sys.stdout.write("%s\n"%[(k,oldv==newv),oldv,newv])
                    assert k==k1,(k,k1, oldv, newv)
                    if oldv!=newv:
                        diff[k] = (oldv, newv)

                # print diff.keys()
                if diff.keys() == [ 'input_kw_keys' ]:
                    oldv, newv =  diff['input_kw_keys']
                    if set(newv).issubset(oldv):
                        return ( self._hook_code_input_kw_smaller(), states)
                states.append("DIFF")
                return (  self._hook_indexed_diff_file(),  states)
            else:
                val=0; states.append("SAME")
                return (val, states)

        if self.VERBOSE:
            print (self, val,states)
        return val,states
        assert 0



    # def input_kw(self):
    #     return  

    # @staticmethod
    def _decorate_change_output(self,f):
        @decorator
        def _dec(f, *a,**kw):
            '''
            Decorate a function 
            return output_kw instead of original value
            `return None` <==> `self.output_kw["return_value"] = None`
            '''
            # okw['returned'] = f( *a, **kw)
            self.returned = f( *a, **kw)
            # return okw            
            return self     
        return _dec(f)       

    def _attach_func(self, func, frame, skip):
        assert 0

    @cached_property
    def input_kw(self):
        # return 
        skip = 1
        ### fill default and add decorate to return output_kw
        func = self.func_orig
        func = func__fill_defaults( skip,  None, self._root.input_kw )(func)
        func = self._decorate_change_output(func)
        self.func = func
        
        ### add input_kw
        # self.input_kw_keys = args[skip:]
        (args, varargs, keywords, defaults) = inspect.getargspec(func)
        input_kw = _dict(zip(args[skip:], defaults))
        return input_kw

    @classmethod
    def from_func(cls, output_kw, input_kw=None,force=0,frame=None,skip=1, name =None, tag = None):
        def _dec(func):
            _frame = frame__default(frame)
            # None

            ### add ouput_kw
            # assert 'returned' not in okw, (okw.keys(), func)
            self = cls(func, input_kw, output_kw, force, _frame, skip, name, tag)
            # self._attach_func(func, _frame, skip)
            return self        

        
        return _dec        

    @property
    def name(self):
        return self.f.__name__



    def _attach_to_root(self,frame=None):
        frame = frame__default(frame)
        self._root = _root = frame.f_locals['_symbolicRootNode']
        self._root.input_kw[ self.name ] = self

        pass
    def _get_func_code(self, func):
        linecache.checkcache( self.indexFile.path.replace('.py.index','.py'))
        # func.__module__.__file__)
        return  inspect.getsource(func)

    @cached_property
    def called_value(self,*a,**kw):
        if self.changed_upstream:
            [ x.called_value for x in self.input_kw.values() ]
        if self.changed: 
        # if self.changed_upstream:
            # result = self._run_result
            print("RUNNING:%s"%self)
            result = self.func(self,*a,**kw)

            runned = 1
            # return self._run(*a,**kw)
        else:
            result = self.output_kw
            runned = 0

        if runned or self.force_index_update:
            _ = '''
            Once running is complete, trigger an update t o index file
            '''
            [x.index_update() for x in self.output_kw.values()]
            index_file_update( self.name, self.as_data())

        self.committed = 1
        return result 

        # return self._run_result

    # def index_update_output_kw(self):
    #     [x.index_update() for x in self.output_kw.values()]
        # return 
    def as_data(self):
        src = self._get_func_code(self.func_orig)

        return _dict(data=_dict([
                    ("func_sourcelines", src.splitlines()),
                    # ("func_ast_tree", ast_proj(src) ), 
                    # ("func_code", (self.func_orig_source)), 
                    ("input_kw_keys",self.input_kw.keys()), 
                    ("output_kw_keys",self.output_kw.keys()), 
                    ("name",self.name ),
                    ("tag",self.tag)
                    ]))



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




class AutoNode(RawNode):
    # _DEBUG = 0
    pass
    # @property
    # # @cached_property ### less verbose
    # def called_value(self,*a,**kw):
    #     _ = '''
    #     This is a bit redundant
    #     This is only called if the node is explicitly called
    #     Usually a node should be specified in "input_kw", and updated by 
    #     invoking "child_node.changed_upstream", aka if the upstream is changed then the node
    #     should be runned. 
    #     But in fact, the node should be run even if its own files got changed

    #     Thus, the node should be updated if node.changed

    #     '''

    #     # if self._DEBUG:
    #     #     print ('[UPSTREAM_OF]',self,)
    #     # print ('[UPSTREAM_IS]',self.changed_upstream)
    #     if self.changed:
    #     # if self.changed_upstream:
    #         return self._run_result
    #         # return self._run(*a,**kw)
    #     else:
    #         return self.output_kw ### 

class SymbolicRootNode(AutoNode):

    def _attach_to_root(self,frame=None):
        '''
        Do not attach outputNode  to itself
        '''
        self._root = self
        pass

    @cached_property
    def input_kw(self):
        return _dict()

# def SymbolicOutputNodeFunc(self): retrun [x() for x in self.input_kw.values()]
class SymbolicOutputNode(AutoNode):
    @property
    def changed(self):
        return len(self.changed_upstream)
        # return self._input_kw
    
    
    # def _attach_to_symout(self,frame=None):
    #     '''
    #     Do not attach outputNode  to itself
    #     '''
    #     pass


# class SymbolicInputNode(RawNode):
#     pass


'''
---------------------------------------
Graveyard ahead
--------------------------------------
'''
def _output_kw(okw,skip=1):
    from pymisca.header import func__setAsAttr as _attach
    def _dec(func):
        assert 'return_value' not in okw, (okw.keys(), func)
        func__fill_defaults( skip, frame__default())(func)
#         print '[aaa]',func.__defaults__
        func.output_kw =  okw
        
        
        def gunc(*a,**kw):
#             input_kw = zip()
            (args, varargs, keywords, defaults) = inspect.getargspec(func)
            defaults = defaults or ()
            @_attach(func)
            def upstream_changed(a=a,kw=kw):
                return [(k,ele) for (k,ele) in zip(args,defaults)
                        if ele.changed()]
            okw['return_value'] = func(func,*a,**kw)
            return okw
        gunc = functools.wraps(func)(gunc)
        return gunc 
    return _dec

