from pipedata.base import cached_property,frame__default,_dict
# from pipedata.base import IndexedDiffFileError
from pipedata.abstract_node import AbstractNode
from pipedata.master_node import MasterNode
import path
import imp
# class RemoteNode(AbstractNode):
class RemoteNode(MasterNode):
    VERBOSE = 0
    class RemoteModuleMissing(Exception):
        pass
    def __repr__(self,):
        return '%s(index=%r, name=%r,force=%r,)'%(self.__class__.__name__,
            self.index,self.name, self.force, )
    def __call__(self):
        return self.called_value
    def __getitem__(self,k):
        return self.output_kw[k]
    def __init__(self, index, remote_path, remote_name, name = None, frame=None,force=0 ):
        assert remote_path.endswith(".py")
        self.remote_name = remote_name
        self.remote_path = (index.realpath().dirname() / remote_path).realpath()
        # .realpath()
        self.force =force
        frame = frame__default(frame)

        index = index
        func = self.func_template
        input_kw = {}
        output_kw = {}
        name = remote_name if name is None else name
        super( self.__class__, self).__init__( index, func, input_kw, output_kw, name, force)

    @staticmethod
    def func_template(self, (remote_node,),):
        _ = '''
        ### should modify remote leaves records to include self
        '''
        # with self.remote_path.dirname():
        self._output_kw = self.remote_node()._output_kw
        # remote_node()
        if remote_node.runned:
            return remote_node.returned             
        else:
            return None           

    def _init_func(self, d=None, skip =1):
        '### intercept before self.initialised_tuples '
        input_kw =  _dict(remote_node=self.remote_node)
        output_kw = _dict()
        return (input_kw, output_kw)

    @property
    def remote_connected(self):
        return self.remote_path.exists()

        # try:
        #     return self.remote_node.index
        # except self.RemoteModuleMissing as e:
        #     return e
        # finally:
        #     return None


    @cached_property
    def remote_node(self):
        if not self.remote_path.exists():
            raise self.RemoteModuleMissing(self.remote_path)
        import warnings
        # warnings.filterwarnings("ignore", message=".*not found while handling absolute import.*")
        warnings.filterwarnings("ignore", module = self.remote_path)
        mod = imp.load_source( self.remote_path, self.remote_path)
        node = getattr(mod, self.remote_name)
        return node

    def index_update(self):
        self.remote_node.index_update()
        return [x._index_update() for x in self.level_stream]        

    def as_record(self):
        rec = super(RemoteNode,self).as_record()
        rec['self'].update(
                [
                ("remote_path" , self.remote_path),
                ("remote_name" , self.remote_name),
                ("remote_record",self.remote_node.as_snapshot()),
                ])
        rec['output_snapshot'] = []
        return rec
    def as_snapshot(self):
        rec = super(RemoteNode,self).as_snapshot()
        rec['self'].update(
                [
                ("remote_path" , self.remote_path),
                ("remote_name" , self.remote_name),
                ("remote_record",self.remote_node.as_snapshot()),
                ])
        rec['output_snapshot'] = []
        return rec
    # @property
    # def remote_index_file(self):
    #     return self.remote_path + ".index"        

    # def _hook_indexed_diff_file(self):
    #     raise self.IndexedDiffFileError(self)

    # def _hook_indexed_missing_file(self):
    #     return 1

    # @cached_property
    # def changed(self):
    #     # return 1
    #     return self._changed
    
    # @cached_property
    # def _changed(self, ):
    #     '''
    #     A cached file 
    #      A file is changed  since last run if 
    #         - if the file is not indexed
    #         - if mtime or size is different
    #     '''
    #     if self.changed_upstream:
    #         return 1
    #     else:
    #         recOld = self.get_record()
    #         recNew = self.as_record()

    #     file_absent = recNew is None
    #     index_absent = recOld is None
    #     states = [] 

    #     if file_absent:
    #         assert 0,"Impossible"
    #         states.append('TARGET_ABSENT')
    #         if not index_absent:
    #             self._hook_indexed_missing_file()

    #     if index_absent:
    #         val = 1
    #         states.append("INDEX_ABSENT")

    #     if not (file_absent or index_absent):
    #         if  recNew!= recOld:
    #             if self.VERBOSE:
    #                 print (self.path, zip(recNew.keys(),recNew.values(),recOld.values()))
    #             val=1; states.append("DIFF")
    #             self._hook_indexed_diff_file()
    #         else:
    #             val=0; states.append("SAME")

    #     if self.VERBOSE:
    #         print("[CheckingChange]:{self.recordId}.changed={val}.state={states}".format(**locals()))
    #     return val


    # def as_record(self):
    #     return _dict([
    #             ("remote_path" , self.remote_path),
    #             ("remote_name" , self.remote_name),
    #             ("remote_record",self.remote_node.as_snapshot()),
    #             ])


