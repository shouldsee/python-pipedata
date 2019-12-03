from pipedata.base import cached_property,frame__default,_dict
# from pipedata.base import IndexedDiffFileError
from pipedata.abstract_node import AbstractNode
import path
import imp
class RemoteNode(AbstractNode):
    VERBOSE = 0
    def __repr__(self,):
        return '%s(index=%r, name=%r,force=%r,)'%(self.__class__.__name__,
            self.index,self.name, self.force, )
    def __call__(self):
        return self.called_value
    def __getitem__(self,k):
        return self.output_kw[k]
    def __init__(self, index, remote_path, remote_name, name = None, frame=None,force=0 ):
        if name is None:
            name = remote_name
        assert remote_path.endswith(".py")
        self.remote_name = remote_name
        self.remote_path = path.Path(remote_path).realpath()
        self.force =force
        frame = frame__default(frame)

        # input_kw = 

        def _f(output_kw={}, func = None, input_kw={},skip=1, tag=None, ):
            if func is None:
                func = lambda:None
            def func(self, (remote_node,),):
                _ = '''
                ### should modify remote leaves records to include self
                '''
                self._output_kw = self.remote_node()._output_kw
                # remote_node()
                if remote_node.runned:
                    return remote_node.returned             
                else:
                    return None   
            # output_kw = _dict(output_kw)
            super( self.__class__, self).__init__( index, func, input_kw, output_kw, name)
            # force, frame, skip, name, tag)
        _f()

    def _init_func(self, d=None, skip =1):
        return (dict(remote_node= self.remote_node),_dict())

    # @cached_property
    @property
    def remote_index_file(self):
        return self.remote_path + ".index"

    @cached_property
    def remote_node(self):
        # mod = imp.load_source( self.remote_path.replace(), self.remote_path)
        mod = imp.load_source( "remote_pipe", self.remote_path)
        node = getattr(mod, self.remote_name)
        # def _hook_post_index_update(remote, indexData):
        #     return self.index.index_file_update( 
        #     "%s:%s" % (self.remote_path, self.remote_name),
        #     indexData[1])
        # node._hook_post_index_update = _hook_post_index_update
        return node

    def _hook_indexed_diff_file(self):
        # self.force_index_update = 1
        # return 
        raise self.IndexedDiffFileError(self)

    def _hook_indexed_missing_file(self):
        return 1

    @cached_property
    def changed(self):
        # return 1
        return self._changed
        

    @cached_property
    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        if self.changed_upstream:
            return 1
        else:
            recOld = self.get_record()
            recNew = self.as_record()
        # file_absent = index_file_read( self.remote_index_file )
        # file_absent = os_stat_safe(self.path) == os_stat_result_null

        file_absent = recNew is None
        index_absent = recOld is None
        states = [] 

        if file_absent:
            assert 0,"Impossible"
            states.append('TARGET_ABSENT')
            if not index_absent:
                self._hook_indexed_missing_file()

        if index_absent:
            val = 1
            states.append("INDEX_ABSENT")

        if not (file_absent or index_absent):
            if  recNew!= recOld:
                if self.VERBOSE:
                    print (self.path, zip(recNew.keys(),recNew.values(),recOld.values()))
                val=1; states.append("DIFF")
                self._hook_indexed_diff_file()
            else:
                val=0; states.append("SAME")

        if self.VERBOSE:
            print("[CheckingChange]:{self.recordId}.changed={val}.state={states}".format(**locals()))
        return val

    def as_record(self):
        return _dict([
            ("remote_path" , self.remote_path),
            ("remote_name" , self.remote_name),
            ("remote_record",self.remote_node.as_snapshot()),
            # ("remote_record",self.remote_node.as_record())
            ])
