import linecache
import inspect
from pipedata._util import cached_property,_dict,_dbgf


class _INIT_VALUE(object):
    pass



returned =  _INIT_VALUE()

class AbstractNode(object):
    # ChangedOutputError = ChangedOutputError
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
        return "%s(recordId=%s,index=%r)" % (
            self.__class__.__name__,
            self.recordId,
            # self.func.__code__, 
            self.index
            # ':tag:%s'% self.tag if self.tag else ''
            )

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
        return self.index.get_record( self.recordId, {})        

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
        assert 0,"TBI"
    @cached_property
    def changed_upstream( self,):
        assert 0,"TBI"

    @cached_property
    def changed_upstream_safe( self,):
        assert 0,"TBI"


    @property
    def changed_safe(self):
        try:
            changed = self.changed
            e = None
        except self.ChangedError as e:
            changed = 1
            # print (e)
        # finally:
        return changed,e


    def get_upstream_tree(self):
        return "END"

    @cached_property
    def called_value(self,*a,**kw):
        return self._get_called_value()
    def _get_called_value(self,*a,**kw):
        '''
        #### evalutaion of value/sideeffects
        Core functionality to make  
        '''
        # print("[UPSTRAM_CHANGED]",self)
        # if self.__class__.__name__ == 'RemoteNode':
        #     _dbgf()

        if self.changed_upstream:
            for x in self.input_kw.values():
                with x.index.realpath().dirname():
                    x.called_value
            # [ x.called_value for x in self.input_kw.values() ]
        msg = "%s,%s,%s"%(self.recordId,self.changed_upstream,self.changed)
        if any([self.changed_upstream,self.changed]): 
            self.running = 1
            # print("RUNNING:%s"%self)
            print("[RUNNING]%s"%msg)
            input_kw, output_kw = self.initialised_tuples
            args = inspect.getargspec(self.func)[0]
            self.returned = self.func(*([x[1] for x in zip(args, (self, input_kw.values(), output_kw.values() ))]) )

            self.running = 0
            self.runned = 1
        else:
            print("[SKIPPING]%s"%msg)
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
            d = self.index.node_dict
            # d = self._root.input_kw
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

        # self._root = self.indexFile._symbolicRootNode
        # self._root = _root = frame.f_locals['_symbolicRootNode']
        self.index.node_dict[self.name] = self
        # self._root.input_kw[ self.name ] = self
    class ChangedError(Exception):
        pass
    class IndexedMissingFileError(ChangedError):
        '''
        index_absent=0, file_absent=1
        suppress if the hooks not enabled
        '''
        pass
    class IndexedDiffFileError(ChangedError):
        '''
        index_absent=0, file_absent=1
        suppress if the hooks not enabled
        '''
        pass
    class ChangedSelfError(ChangedError):
        pass
    class ChangedNodeError(ChangedError):
        pass
    class ChangedOutputError(ChangedError):
        pass
