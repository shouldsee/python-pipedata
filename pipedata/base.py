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

import pipedata._ast_util as _ast_util
from pipedata._ast_util import ast_proj
from pipedata._util import cached_property,frame__default
from pipedata._util import  _get_upstream_tree, _tree_as_string,_get_upstream_graph,_get_root_nodes
from pipedata._util import  dict_flatten
from attrdict import AttrDict
import intervaltree,ast

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


    
    
def _open(*a):
    assert isinstance(a[0])


def st_time_size(st):
    return (st.st_mtime, st.st_size)




class SymbolicRootNode(object):
    def __init__(self,*a,**kw):
        pass

    @cached_property
    def input_kw(self):
        return _dict()        

# class NodeDict(_dict,object):
class NodeDict(_dict,):
    index = "[DETACHED]"
    @staticmethod
    def duplicated_key_error(self,  key):
        msg = '''
Duplicated key:{key}
Index: {self.index}
Value is already specified in [TBI]
        '''.format(**locals())
        return self.DuplicatedKeyError(msg)

    def __setitem__(self,key, value):
        if key in self:
            raise self.duplicated_key_error(self, key)
        _dict.__setitem__(self, key,value)

    class DuplicatedKeyError(Exception):
        pass

class SourceTreeMethods(object):
    @staticmethod
    def source_to_itree(buff):
        d = intervaltree.IntervalTree()
    # def source_iter(buff):
        exprs = ast.parse(buff).body
        lines = buff.splitlines(1)
        linenos = [x.lineno-1 for x in exprs] + [len(lines)]
        linenos = zip(linenos[:-1],linenos[1:])
        for expr,(s,e) in zip(exprs,linenos):
            # e = e-1
            # s = s
            # d[s:e] = (expr,''.join(lines[s:e]))
            d[s:e] = buff =  ''.join(lines[s:e])
            # iv = d[s].pop()
            # print(iv.begin,iv.end,s,e)
            # print('[BUFF]',s,e,expr)
            # print(buff)
        return d

class IndexNode(SourceTreeMethods,object,):
    # def DEBUG_INEDX_FLUSH(self):
    DEBUG_INDEX_FLUSH_QUEUE = 0
    @property 
    def node_dict(self):
        return self._node_dict
    @property 
    def index(self):
        return self
        # return self._root.input_kw
    @property 
    def input_kw(self):
        return self._node_dict

    @property 
    def recordId(self):
        return "_ROOT"
        # self._node_dict
    
    def __repr__(self):
        return "%s(path=%r)"%(self.__class__.__name__, str(self.path))
    def __init__(self,path = None, frame=None):
        frame = frame__default(frame)
        if path is None:
            path = os.path.realpath( frame.f_locals['__file__'].replace('.pyc','.py')+'.index')
        self.path = Path(path).realpath()
        self._node_dict = NodeDict()
        self._node_dict.index = self
        self.update_queue = _dict()
        self.rootNodes = set()
        self.frame = frame
        self.lineno = frame.f_lineno - 1
        assert self.script_path.exists(),(self.script_path,)
        self.sourceTree = self.source_to_itree(open(self.script_path,'r').read())
        # expr = ast.parse(self.sourceTree[self.f_lineno].pop().data).body[0]
        # if isinstance(expr,ast.assign):

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["frame"]
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.frame = None

    def realpath(self):
        return self.path
    def write_sourceTree(self,fn):
        with open(fn, 'w') as f:
            for x in sorted( self.sourceTree):
                f.write(x.data)
        (fn + 'c').unlink_p()
        # path.Path(fn.replace())
        # os.path.unlink_p()

    def index_file_update(self, key, value):
        self.update_queue[key] = value
        return (key,value)

    def index_file_flush(self, ):
        # assert self.sync
        ### flush all index

        [ [remote_index.index_file_flush(),
            sys.stdout.write('[REMOTE_INDEX_FLUSH]%s\n'%remote_index)] 
            for remote_index in self.remote_index_set]

        if self.DEBUG_INDEX_FLUSH_QUEUE:
            print("[FLUSHING_INDEX]%s%s"%(self.path,
             dumper._dumps([(k,v.get('meta',{})) for k,v in self.update_queue.items()])))
        
        fname = self.path
        with FileLock( fname +'.lock') as lock:
            d = self.records_cached.copy()
            d.update( self.update_queue )
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

    @property
    def script_path(self):
        fn = self.path.replace('.index','')
        fn = fn.replace('.pyc','.py')
        fn = Path(fn)
        # assert fn.exists(),(fn,)
        assert fn.endswith('.py'),(fn,)
        return fn

    def make_copy(self, dest, name = None):

        if dest is None:
            dest = 'test_build'
        
        dest = Path(dest)
        # shutil.rmtree(name)
        # os.makedirs_p(dest)
        # dest.makedirs_p()
        assert dest.makedirs_p().isdir(),(dest,)


        fn = self.script_path
        if name is None:
            name = fn.basename()
        assert name.endswith('.py') and fn.endswith('.py'),(fn,name)
        shutil.copy2(fn, dest / name )
        # if self.path.exists():
        _dest = dest / name+'.index'
        _dest.unlink_p()
        return dest

    def set_rootNodes(self,vals=None):
        vals = vals or []
        for val in vals:
            if val in self.node_dict:
                self.rootNodes.add((self, self.node_dict[val]))
            else:
                assert 0, "did not find node with recordId %r"%val
        if not vals:
            try:
                self.rootNodes.update(_get_root_nodes(self, exclude=set([self])))
            except Exception as e:
                print(e)
                self.rootNodes.add((self.index, self))
        assert self.rootNodes,('Should not be empty',self.rootNodes)
        return self.rootNodes

    def main(index):
        print('START' + 20*"-")
        print('[INDEX]%s'%index)
        argv = sys.argv
        verbose = '--verbose' in argv 

        val = []
        if '--roots' in argv:
            val = argv[argv.index('--roots')+1]
            val = val.split(',')
        index.set_rootNodes(val)

        if '--changed' in argv:
            del argv[argv.index('--changed')]
            for k,v in index.node_dict.items():
                changed,err = v.changed_safe
                if err is None:
                    err = ''
                if verbose>=1:
                    print('\t'.join(("[CHANGED=%s]"%changed, k, v.__class__.__name__, repr(err), v.index.realpath(), )))
                else:
                    print('\t'.join(("[CHANGED=%s]"%changed, k, v.__class__.__name__, )))
                # print("[CHANGED=%d]"%v.changed_safe(),k,v, )
        elif '--changed-upstream' in argv:
            for node,status in index.remote_node_status_set:
                 print("%s,%s"%(status,node))                 
            for k,v in index.node_dict.items():
                changed_upstream = v.changed_upstream_safe
                # err = None
                # if err is None:
                #     err = ''
                if verbose>=1:
                    print('\t'.join((
                        "[CHANGED_UPSTREAM=%s]"%(int(bool(changed_upstream))),
                        k,
                         repr(changed_upstream), 
                         v.__class__.__name__,  
                         v.index.realpath(), )))
                else:
                    changed_upstream = [x.recordId for x,e in changed_upstream][::-1]
                    print('\t'.join((
                        "[CHANGED_UPSTREAM=%s]"%(int(bool(changed_upstream))),
                         k,
                         repr(changed_upstream), 
                         v.__class__.__name__,  
                         # v.index.realpath(), 
                         )))                        
        elif '--tree' in argv:
            # rootNodes = sum(list(_get_root_nodes(x)) for x in index.input_kw.values(),[])
            # rootNodes = _get_root_nodes(index,exclude=set([index]))
            print(_tree_as_string(_get_upstream_tree([x[1] for x in index.rootNodes],)))
        elif '--copy-source' in argv:
            '''
            Scenarios:
                - 1. testing a pipeline
            '''
            dest = argv[argv.index('--copy-source')+1]
            dest = Path(dest).realpath()
            dest.makedirs_p()
            assert dest.isdir(),(dest,)
            assert not dest.listdir(),"Destination not empty:%r"%dest

            nodes_to_copy = d = _dict()
            for x in index.rootNodes:
                d.update(x[1].get_upstream_nodes(0))
            nodes_to_copy = dict_flatten(nodes_to_copy,idFunc=lambda x:x.recordId,)
            s = set()
            [s.update(v.level_stream) for v in nodes_to_copy.values() if v is not None]
            nodes_to_copy = s
            indexes_to_copy = set(v.index for v in nodes_to_copy)
            # for node in set(index.node_dict.values()) & nodes_to_copy:
            for node in nodes_to_copy:
                print(node.__class__,node.recordId, node.lineno)
            # assert 0
            # for node in 

            from pipedata.types import SelfSlaveFile,RemoteNode
            import imp
            def _copy(src,dest):
                assert os.path.exists(src),(src,)
                if not os_stat_safe(src)==os_stat_safe(dest):
                    dest.dirname().makedirs_p()
                    shutil.copy2(src,dest)
                    return 1
                else:
                    return 0
            _move = shutil.move            

            indexMap = _dict()
            oldIndexPathMap = _dict()

            for i,index in enumerate(indexes_to_copy):
                _ddir = dest / ("stage%03d"%i)
                _dscript = _ddir/'pipe.py'

                print(_copy( index.script_path,  _dscript),'[COPY]')
                newIndex = imp.load_source(_dscript,_dscript).index
                indexMap[index] = newIndex
                oldIndexPathMap[index.script_path] = index 
            # for k,v in indexMap.items():
            #     print k,v

            for node in nodes_to_copy:
                newIndex = indexMap[node.index]
                oldIndex = node.index
                if isinstance(node, SelfSlaveFile):
                    _src = node.path
                    node.index = newIndex
                    if node.relpath.isabs():
                        node.relpath = node.relpath.replace(os.sep,'_')
                    _dest = newIndex.path.dirname() / node.relpath
                    _copy( _src, _dest )
                    _buffer = '''{node.__class__.__name__}(index=index,path="{node.relpath}",name="{node._master.name}")'''.format(**locals())
                    node.rewrite(newIndex, _buffer)

                if isinstance(node, RemoteNode):
                    node.index = newIndex
                    node.remote_path = indexMap[oldIndexPathMap[node.remote_path]].script_path
                    node.rewrite(newIndex)

            for newIndex in indexMap.values():
                newIndex.write_sourceTree(newIndex.script_path)


            for (dp,dn,fns) in os.walk(dest):
                for fn in fns:
                    print((dp/fn),(dp/fn).exists())

            # assert 0,(nodes_to_copy,)
        elif '--graph' in argv:
            print(dumper._dumps(map(repr,_get_upstream_graph(index))))
            # return
        else:
            index.sync()
        print('END' + 20*"-")

    @property
    def remote_node_status_set(index):
        s = set()
        for x in index.node_dict.values():
            if getattr(x,'remote_connected',None) is not None:
                s.add((x,x.remote_connected))
        return s
    @property
    def remote_index_set(self):
        s = set()
        for node,status in self.remote_node_status_set:
            if status:
                s.add( node.remote_node.index)

        return s


        # return  set( x.remote_index_safe for x in index.node_dict.values() if hasattr(x,'remote_node'))
        
    def sync(self):
        with self.realpath().dirname():
            [x() for x in self.node_dict.values()]
        self.index_file_flush()

    def collect_static(self):
        print()
        pass


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
