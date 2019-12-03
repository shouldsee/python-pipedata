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
def _dumps(s):
    return json.dumps(s, cls=MyEncoder,indent=4)
def _loads(s):
    return json.loads(s)
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
    # print(traceback.format_exc())
    # import traceback
    # traceback.print_stack()
    # traceback.print_exc()
    pdb.set_trace()    
# import jsonpickle as dill
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
        self._symbolicInputNode = RawNode(
            self, lambda self:None,
        _dict(), _dict(),0,frame,1,'_symbolicInputNode',None,)  
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
                f.write(_dumps(d))
                # f.write(dill.dumps( d))
                # , f, )
                # dill.dump( d, f, protocol=dill.HIGHEST_PROTOCOL)


        # return _index_file_flush(self.update_queue, self.path)
    @cached_property
    def records_cached(self):
        if file_not_empty( self.path):
            with open( self.path, "rb") as f:
                # it = ()
                d = _loads(f.read(), )
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




def NodeFromFunc(*a,**kw):
    return RawNode.from_func(*a,**kw)

class _INIT_VALUE(object):
    pass
class ChangedNodeError(Exception):
    pass
returned =  _INIT_VALUE()
class ChangedOutputError(Exception):
    # return 
    pass

class AbstractNode(object):
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
            print("RUNNING:%s"%self)
            input_kw, output_kw = self.initialised_tuples
            args = inspect.getargspec(self.func)[0]
            self.returned = self.func(*([x[1] for x in zip(args, (self, input_kw.values(), output_kw.values() ))]) )
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


    def __repr__(self):
        return '<Node with func:%s%s>' % (self.func.__name__, 
                ':tag:%s'% self.tag if self.tag else '')


class MasterNode(AbstractNode):
    @property
    def recordId(self):
        return self.name
    def __getitem__(self,key):
        return self.output_kw[key]

    def __init__(self, index, func, input_kw, output_kw, force, name, ):
        super(self.__class__, self).__init__( index, func, input_kw, output_kw, name)

    @classmethod
    def from_func(cls, index, output_kw = {}, force=0,name = None ):
        def _dec(func):
            input_kw = {}
            self = cls(index, func, input_kw, output_kw, force, name)
            return self        
        return _dec        


    @property
    def _changed(self):
        return self._changed_tuple[0]
    @property
    def changed_upstream(self):
        return self._changed_tuple[1]
    def _hook_changed_record(self, changed_code,changed_input):
        return 
    @cached_property
    def _changed_tuple(self):    
        recOld = self.get_record()
        recNew = self.as_record()
        recs = [recOld,recNew]
        if recOld is None:
            print("[CHANGED_INDEX_ABSENT]%s%s"%(self.index,self))
            # self._hook_noindex()
            changed_code, changed_input = 1,1
        else:
            if recOld != recNew:
                diff = _dict()
                trees = [ ast_proj('\n'.join( rec['sourcelines'])) for rec in recs ]
                changed_code = trees[0] != trees[1]
                changed_input = recOld['input_snapshot'] != recNew['input_snapshot']
                changed_output = recOld['output_snapshot'] != recNew['output_snapshot']
                if changed_output:
                    for k in recOld['output_snapshot']:
                        v1 = recOld['output_snapshot'][k]
                        v2 = recNew['output_snapshot'][k]
                        if v1!=v2:
                            print(self,k,v1,v2)
                    raise ChangedOutputError("output for %s has changed since snapshot"%self)
                print("[CHANGED_DIFF](%s,%s),%s%s"%(changed_code,changed_input,self,self.index,))
                changed_code, changed_input
                self._hook_changed_record( changed_code, changed_input)
            else:
                print("[CHANGED_SAME]%s%s"%(self.index,self))
                changed_code, changed_input = 0,0

        return changed_code,changed_input
    def as_snapshot(self):
        return _dict([
        ('class', self.__class__.__name__),
        ('sourcelines', self._get_func_code(self.func).splitlines()),
        ('output_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        ])
        return self.as_record()
    def as_record(self,):
        return _dict([
        ('class', self.__class__.__name__),
        ('sourcelines', self._get_func_code(self.func).splitlines()),
        ('input_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.input_kw.items() ])),
        ('output_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        ])
class SlaveNode(AbstractNode):
    pass
    # def _changed(self):



class RawNode(AbstractNode):
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




    @property
    def recordId(self):
        return self.name

    @property
    def func(self):
        return self.func_orig

    def __repr__(self):
        return '<Node with func:%s%s>' % (self.func.__name__, 
                ':tag:%s'% self.tag if self.tag else '')
    def __getitem__(self,key):
        return self.output_kw[key]

    
    def __init__(self, index, func, input_kw, output_kw, force, frame, skip, name, tag, ):
        # input_kw = None
        # output_kw = None
        frame = frame__default(frame)
        if output_kw is None:
            output_kw = _dict()
        self.tag = tag
        self.force = force
        super( RawNode,self).__init__( index, func, {}, output_kw, name)


    def index_update(self):
        return [x._index_update() for x in self.level_stream]


    @cached_property
    def _changed(self):
        '''
        node.changed indicate the result needs re-computation, if:
          - its code is changed 
          - its output is changed
        '''
        print("CHECKING_NODE:%s,%s"%(self.index,self))        
        if "out5" in self.name :
            pass
            # _dbgfs()
        if self.force:
           print("CHANGED_FORCED:%s,%s"%(self.index,self))
           return 1
        if self._changed_code()[0]:
            print( "CHANGED_CODE:%s,%s"%(self.index,self))
            return 1

        if self._changed_output():
            assert 0,"This should be obsolete and never called" 
            print( "CHANGED_OUTPUT:%s,%s"%(self.index,self))
            # print( "CHANGED_OUTPUT:%s\n%s"%(self,))
            print (self,self._changed_output())
            return 1
    
        print("[CHANGED_SAME]:%s,%s"%(self.index,self))
        return 0




    def _changed_output(self):
        lst = []
        for k,v in self.output_kw.iteritems():
            if hasattr(v,'changed'):
            # if isinstance(v,(TrackedFile,RawNode)):
                if v.changed:
                    lst.append( (k,v) )
            else:
                assert 0, (k,hasattr(v,'changed'),getattr(v,'changed',None),type(v),v)
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
        rec = self.get_record()
        # rec = self.index.get_record(self.name, None)
        file_absent = False ### this is when a node is deleted from a file
        index_absent = rec is None

        states = [] 

        # ### not relevant
        if file_absent:
            val = 1
            states.append('TARGET_ABSENT')

        if index_absent:
            # _dbgf()
            val = 1
            states.append("INDEX_ABSENT")

        if file_absent and not index_absent:
            val = 1
            self._hook_indexed_missing_file()

        if not (file_absent or index_absent):
            v1 = rec['data'].copy()
            v2 = self.as_record()['data'].copy()
            # .copy()
            assert set(v1) == set(v2),(v1.keys(),v2.keys())

            srcs =  []     
            trees = []
            for v in (v1,v2):
                src =  '\n'.join(v.pop('func_sourcelines'))
                srcs.append(src)
                v['func_ast_tree'] = _tree = ast_proj(src) ###  exclude from comparision
                trees.append(_tree)
                # print '\n'.join()


            if 0:
                if self.name =='out5':
                    print (srcs[0])
                    print (trees[0])
                    print (srcs[1])
                    print (trees[1])
                    print (self,self.func_orig.func_code,v1==v2)
            #     if 'line 32' in repr(self.func_orig.func_code):

                # print vars(self)
                # print globals()
            # sys.stdout.write("%s\n"%[(k,oldv==newv),oldv,newv])


            if  v1 != v2:
                diff = _dict()
                for (k, oldv),(k1, newv) in zip(v1.items(),v2.items()):
                    # self.VERBOSE = 2
                    if self.VERBOSE >= 2:
                        sys.stdout.write("%s\n"%[(k,oldv==newv),oldv,newv])
                    assert k==k1,(k,k1, oldv, newv)
                    if oldv!=newv:
                        diff[k] = (oldv, newv)

                # if self.name =='out5':
                #     _dbgf()

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





    @classmethod
    def from_func(cls, index, output_kw=None, input_kw=None,force=0,frame=None,skip=1, name =None, tag = None):
        def _dec(func):
            _frame = frame__default(frame)
            # None

            ### add ouput_kw
            # assert 'returned' not in okw, (okw.keys(), func)
            self = cls(index, func, input_kw, output_kw, force, _frame, skip, name, tag)
            # self._attach_func(func, _frame, skip)
            return self        
        
        return _dec        





    def as_record(self, ):
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



# class TrackedFile(object):    
class TrackedFile(RawNode):    

    # def index
    HOOKS_ENABLED_LIST = [
        "indexed_missing_file",
        "indexed_diff_file",
    ]
    SiblingNode = None

    _DEBUG = _DEBUG
    DEBUG_NO_CACHE = 0
    VERBOSE = 0
    def __repr__(self,):
        return "%s(%r)"%(self.__class__.__name__,self.path)

    def __call__(self,*a,**kw):
        return self

    def __init__(self, index, path,  name=None, func = None, input_kw={},output_kw={},force=0, frame=None,skip=1,tag=None):
        if func is None:
            func = lambda:None
        frame = frame__default(frame)
        super( TrackedFile, self).__init__(index, func,  input_kw, output_kw, force, frame, skip, name, tag)
        self.path=path
    def realpath(self):
        return self.index.path.dirname()/self.path


    def _hook_indexed_missing_file(self):
        if "indexed_missing_file" in self.HOOKS_ENABLED_LIST:
            pass
            ### when file is indexed but absent
        raise IndexedMissingFileError(os.getcwd()+'|'+str(self)+str(self.indexFile))

    def _hook_indexed_diff_file(self):
        # if "indexed_diff_file" in self.HOOKS_ENABLED_LIST:
        raise IndexedDiffFileError(os.getcwd()+'|'+str(self)+str(self.indexFile))

    @cached_property
    def changed(self):
        return self._changed
    @property
    def recordId(self):
        return self.path
    

    @cached_property
    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        if self.DEBUG_NO_CACHE:
            return 1
        rec = self.get_record()
        # with self.index.path.dirname() as cwd:

        # file_absent = os_stat_safe(self.path) == os_stat_result_null
        file_absent = not file_not_empty(self.realpath())
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
            v1 = st_time_size( AttrDict(rec['stat_result']))
            v2 = st_time_size( os_stat_safe(self.realpath()) )
            if  v1!= v2:
                if self.VERBOSE:
                    print (self.realpath(), zip(v1,v2))
                val=1; states.append("DIFF")
                self._hook_indexed_diff_file()
            else:
                val=0; states.append("SAME")

        if self.VERBOSE:
            print("[CheckingChange]:{self.path}.changed={val}.state={states}".format(**locals()))
        return val
            # ,states
            # return (0,"SAME")
    def as_record(self, ):
        # stat_result =os.stat(self.realpath())
        stat_result =os_stat_safe(self.realpath())
        # print ("[UPDATING_INDEX]%s\n%s"%(self,stat_result.st_mtime,))
        return _loads(_dumps( dict(stat_result = stat_result)))


    
#####################
#####################

class TrackedFileNode(TrackedFile):
    pass



class InputTrackedFile(TrackedFile):
    '''
    '''
    # counter = _counter
    default_name_fmt =  "InputFileNode_%s"
    counter = -1
    def __init__(self,*a,**kw):
        pass
        # TrackedFile.__init__(self,*a,**kw)
        super( InputTrackedFile,self).__init__(*a,**kw)        

    def get_node_name(self, name):
        if name is None:
            self.__class__.counter += 1
            # print (self.__class__.counter+1, self.path,)
            return self.default_name_fmt % ("%04d"% self.__class__.counter)

        else:
            return name
        ### create

    def _hook_indexed_diff_file(self):
        print("INPUT_FILE_CHANGED:%s"%self)
        # raise IndexedDiffFileError(self)        

    pass

def func__addSelf(f):
    def g(*a,**kw):
#         kw['self'] = f
        return f(f,*a,**kw)
    return functools.wraps(f)(g)




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




class AutoNode(RawNode):
    pass


class SymbolicRootNode(AbstractNode):

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
    def _changed(self):
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


