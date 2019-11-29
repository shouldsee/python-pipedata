import inspect
import functools
from collections import OrderedDict as _dict
from filelock import FileLock
import json
import dill
import os
from decorator import decorator

_DEBUG = 1

def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

def os_stat_result_null():
    return os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)]) 
def os_stat_safe(fname):
    if file_not_empty(fname):
        return os.stat(fname)
    else:
        return os_stat_result_null()

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
        d = {}
    return d



update_queue = _dict()
def index_file_update( fname, key):
    update_queue[key] = dict(stat_result = os.stat( key ))

def index_file_flush(fname=None,frame=None):
    if fname is None:
        fname = index_get_default(frame__default(frame)).path

    with FileLock( fname +'.lock') as lock:
        d = index_file_read(fname)
        d.update( update_queue )
        with open(fname,"w") as f:
            dill.dump( d, f)


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
    HOOKS_ENABLED = [
        "indexed_missing_file",
    ]

    def _hook_indexed_missing_file(self):
        if "indexed_missing_file" in self.HOOKS_ENABLED:
            ### when file is indexed but absent
            raise IndexedMissingFileError(os.getcwd()+'|'+str(self)+str(self.parent))
    def _hook_indexed_diff_file(self):
        raise IndexedDiffFileError(self)

    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        if self.DEBUG_NO_CACHE:
            return 1
        rec = self.parent.cached_index_dict.get( self.path , None)
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
                    print self.path, zip(v1,v2)
                val=1; states.append("DIFF")
                self._hook_indexed_diff_file()
            else:
                val=0; states.append("SAME")

        return val,states
        # return (0,"SAME")

    def index_update(self,):
        return index_file_update( self.parent.path, self.path)


    def changed_if_index_absent(self):
        "Assuming initialisation"
        # self.index_update()
        # assert 0, (self.path, self.parent.path)
        return 1

    @cached_property
    def changed(self):
        val,states  = self._changed()
        if self.VERBOSE:
            print("[CheckingChange]:{self.path}.changed={val}.state={states}".format(**locals()))
        return val

    
    def __init__(self, path, parent=None, frame=None):
        self._frame = frame__default(frame)
        if parent is None:
            parent = index_get_default(self._frame)
        del self._frame

        self.parent =  parent
        super(TrackedFile,self).__init__(path)

def frame_init(frame=None):
    '''
    Adding constants to this frame
    '''
    frame = frame__default(frame)
    print ("[FRAME_INIT] _symbolicInputNode, _symbolicOutputNode")
    symout = frame.f_locals['_symbolicOutputNode'] = SymbolicOutputNode(
        lambda self:[x() for x in self.input_kw.values()]
        ,{},{},0,frame,1,'_symbolicOutputNode')
    symin  = frame.f_locals['_symbolicInputNode'] = RawNode(lambda self:None,{},{},0,frame,1,'_symbolicInputNode')
    indexFile = frame.f_locals['_indexFile'] = index_get_default(frame).path
    return symin,symout,indexFile

class InputTrackedFile(TrackedFile):
    '''
    '''
    def __init__(self, path, parent=None,frame=None, nodeClass = None , force = 0, skip=1):
        if nodeClass is None:
            nodeClass = AutoNode
        frame = frame__default(frame)

        self.node = nodeClass( 
            lambda self, _symbolicInputNode:None,
            input_kw = {}, output_kw={'FILE':self}, force=force,
            frame = frame, skip=skip,
            name="InputFileNode",
             # % path.replace(),

            )
        # print (node, node.input_kw)
        ### create
        super(InputTrackedFile, self).__init__(path,frame=frame)
    def _hook_indexed_diff_file(self):
        print("INPUT_FILE_CHANGED:%s"%self)
        # raise IndexedDiffFileError(self)        

    pass

def func__addSelf(f):
    def g(*a,**kw):
#         kw['self'] = f
        return f(f,*a,**kw)
    return functools.wraps(f)(g)

def func__fill_defaults(skip=0,frame=None):
    '''
    Fill positonal argument using values from frame
    '''

    def _dec(f):
        d = frame__default(frame).f_locals
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
returned =  _INIT_VALUE()
class RawNode(object):
    _DEBUG = _DEBUG
    returned = returned
    AUTO_UPDATE_OUTPUT = 0
    '''
    Decorate a function by
        filling the positional arguments
         attaching a dict of output nodes
         attaching methods related
         :params:skip: how many positional argument to skip 
         Node['returned'] is not cached and should not 
        
    See help(self.func) for original function docstring

    '''    

    @cached_property
    def changed(self):
        '''
        A node is changed if:
          - its code is changed 
          - its output is changed
        '''
        print("CHECKING_NODE:%s"%self)        
        if self.force:
           print("CHANGED_FORCED:%s"%self)
           return 1
        if self._changed_code():
            print( "CHANGED_CODE:%s"%self)
            return 1
        if self._changed_output():
            print( "CHANGED_OUTPUT:%s"%self)
            return 1
        if self.changed_upstream:
            print("CHANGED_UPSTREAM:%s"%self)
            return 1
    
        print("[CHANGED_SAME]:%s"%self)
        return 0


    @cached_property
    def changed_upstream( self,):
        return [x for x in self.input_kw.values() or () if x.changed]
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

    def _changed_code(self):
        '''
        Detect whether the underlying function has changed when compared to 
        '''
        if self._DEBUG:
            return 0
        assert 0
    def __repr__(self):
        return '<Node with func:%s>' % self.f.__name__
    def __getitem__(self,key):
        return self.output_kw[key]



    def _attach_func(self, func, frame, skip):
        '''
        Decorate and attach the function 
        '''
        @decorator
        def change_output( f, *a,**kw):
            '''
            return output_kw instead of original value
            `return None` <==> `self.output_kw["return_value"] = None`
            '''
            # okw['returned'] = f( *a, **kw)
            self.returned = f( *a, **kw)
            # return okw            
            return self            
        
        ### fill default and add decorate to return output_kw
        func = func__fill_defaults( skip, frame__default(frame))(func)
        func = (change_output(func))
        self.func = func
        
        ### add input_kw
        (args, varargs, keywords, defaults) = inspect.getargspec(func)
        self.input_kw.update(zip(args[skip:], defaults))
        return 
    @property
    def name(self):
        return self.f.__name__
    
    @classmethod
    def from_func(cls, output_kw, input_kw=None,force=0,frame=None,skip=1, name =None):
        def _dec(func):
            _frame = frame__default(frame)
            # None

            ### add ouput_kw
            # assert 'returned' not in okw, (okw.keys(), func)
            self = cls(func, input_kw, output_kw, force, _frame, skip, name)
            self._attach_func(func, _frame, skip)
            return self        

        
        return _dec        
    
    def __init__(self, func, input_kw, output_kw, force, frame, skip, name):
        if name is not None:
            func.__name__ = name
        self.f = func
        self.input_kw = input_kw  or _dict()
        self.output_kw = output_kw
        self.force = force
        self._frame = frame__default(frame)
        self._attach_func(func, frame, skip)
        self._attach_to_symout(frame)
        del self._frame
        return  
    def _attach_to_symout(self,frame=None):
        frame = frame__default(frame)
        frame.f_locals['_symbolicOutputNode'].input_kw[self.f.__name__] = self

        pass


    def called_value(self,*a,**kw):
        return self._run_result

    def __call__(self,*a,**kw):
        return self.called_value

    def index_update_output_kw(self):
        return [x.index_update() for x in self.output_kw.values()]

    @cached_property
    def _run_result(self,*a,**kw):
        
        print("RUNNING:%s"%self)
        output = self.func(self,*a,**kw)

        _ = '''
        # Running would change the outputTrackedFile, 
        and considered as an unexpected change when evaluating self.changed()
        '''
        self.index_update_output_kw()
        return output

class AutoNode(RawNode):
    # _DEBUG = 0

    @property
    # @cached_property ### less verbose
    def called_value(self,*a,**kw):
        _ = '''
        This is a bit redundant
        This is only called if the node is explicitly called
        Usually a node should be specified in "input_kw", and updated by 
        invoking "child_node.changed_upstream", aka if the upstream is changed then the node
        should be runned. 
        But in fact, the node should be run even if its own files got changed

        Thus, the node should be updated if node.changed

        '''

        # if self._DEBUG:
        #     print ('[UPSTREAM_OF]',self,)
        # print ('[UPSTREAM_IS]',self.changed_upstream)
        if self.changed:
        # if self.changed_upstream:
            return self._run_result
            # return self._run(*a,**kw)
        else:
            return self.output_kw ### 

# def SymbolicOutputNodeFunc(self): retrun [x() for x in self.input_kw.values()]
class SymbolicOutputNode(AutoNode):
    def _attach_to_symout(self,frame=None):
        '''
        Do not attach outputNode  to itself
        '''
        pass


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

