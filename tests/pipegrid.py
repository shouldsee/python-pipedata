# from delay_and_cache import delay_and_cache as _dac
# from delay_and_cache import cacheThisFrame as _ctf
# from delay_and_cache import CachedProxy
# from delay_and_cache import frame__default

import inspect
import functools
from collections import OrderedDict as _dict
from filelock import FileLock
import json
_DEBUG = 1

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

from pymisca.shell import file__notEmpty as file_not_empty
# import dill as json
import dill
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

def index_file_flush(fname,):
    with FileLock( fname +'.lock') as lock:
        d = index_file_read(fname)
        d.update( update_queue )
        with open(fname,"w") as f:
            dill.dump( d, f)


            # return f.read()
class TrackedFile(BaseFile):    
    # def index
    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        if self.DEBUG_NO_CACHE:
            return 1
        rec = self.parent.cached_index_dict.get( self.path ,None)
        if not file_not_empty(self.path):
            return (1,"TARGET_ABSENT")
        if rec is None:
            # print "ABSENT"
            return (self.changed_if_index_absent(),"INDEX_ABSENT")
            # return 1
        v1 = st_time_size(rec['stat_result'])
        v2 = st_time_size(os.stat(self.path))
        if  v1!= v2:
            if self.VERBOSE:
                print self.path, zip(v1,v2)
            return (1,"DIFF")
        return (0,"SAME")

    def index_update(self,):
        return index_file_update( self.parent.path, self.path)


    def changed_if_index_absent(self):
        "Assuming initialisation"
        self.index_update()
        # assert 0, (self.path, self.parent.path)
        return 1

    def changed(self):
        val,state  = self._changed()
        if self.VERBOSE:
            print("[CheckingChange]:{self.path}.changed={val}.state={state}".format(**locals()))
        return val


    def get_default_parent(self,frame=None):
        frame = frame__default(frame)
        return BaseFile("./test.index")
    
    def __init__(self, path, parent=None, frame=None):
        self._frame = frame__default(frame)
        if parent is None:
            parent = self.get_default_parent(self._frame)
        del self._frame

        self.parent =  parent
        super(TrackedFile,self).__init__(path)
        
#     def upstream_changed(self,):
#         _frame = self._frame
#         return 1
#     def self_changed(self):
#         return     
#     def open(self, *a,**kw):
#         pass
#     pass
#     def __init__(self,)
# CachedProxy._DEBUG = 1

class InputTrackedFile(TrackedFile):
    pass
    # def changed_if_index_absent(self):
    #     index_file_update( self.parent.path, self.path)
    #     return 1

import os        

from decorator import decorator

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
    '''
    Decorate a function by
        filling the positional arguments
         attaching a dict of output nodes
         attaching methods related
         :params:skip: how many positional argument to skip 
         Node['returned'] is not cached and should not 
        
    See help(self.func) for original function docstring

    '''    
    def changed_self(self):
        return self._changed_code() or self._changed_output()
    def changed(self):
        '''
        A node is changed if:
          - its code is changed 
          -  
        '''
        return  self.changed_self() or self.changed_upstream()

    def _changed_output(self):
        lst = []
        for k,v in self.output_kw.iteritems():
            if 0:
                pass
            elif isinstance(v,TrackedFile):
                _changed = v._changed()
                if _changed[0]==1:
                    assert _changed[1] != 'DIFF', ("[UNEXPECTED_MODIFICTAION]", v.path, )
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

    def changed_upstream( self,):
        return [x for x in self.input_kw.values() or () if x.changed()]

    @classmethod
    def from_func(cls, okw, skip=1,input_kw=None,force=0):

        
        def _dec(func):
            frame = None

            ### add ouput_kw
            # assert 'returned' not in okw, (okw.keys(), func)
            self = cls(func, input_kw, okw, force)

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
            return self
        
        return _dec        
    
    def __init__(self, f, input_kw, output_kw, force):
        self.f = f
        self.input_kw = input_kw  or _dict()
        self.output_kw = output_kw
        self.force = force
        return  

    @cached_property
    def called_value(self,*a,**kw):
        return self.func(self, *a,**kw)

    def __call__(self,*a,**kw):
        return self.called_value
        

class AutoNode(RawNode):
    # _DEBUG = 0
    @cached_property
    def called_value(self,*a,**kw):
        # if self._DEBUG:
        #     print ('[UPSTREAM_OF]',self,)
        # print ('[UPSTREAM_IS]',self.changed_upstream())
        if self.changed_upstream() or self.force:
            print("RUNNING:%s"%self)
            output = self.func(self,*a,**kw)
            [x.index_update() for x in self.output_kw.values()]
            return output
        else:
            print("SKIPPING:%s"%self)
            return self.output_kw ### 


'''
---------------------------------------
Graveyard ahead
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

