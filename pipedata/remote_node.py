from pipedata.base import index_file_read, cached_property,frame__default,_dict
from pipedata.base import IndexedDiffFileError
from pipedata.base import RawNode
import path
import imp
class RemoteNode(RawNode):
    def __repr__(self,):
        return '%s(index=%r, name=%r,force=%r,)'%(self.__class__.__name__,
            self.index,self.name, self.force, )
    def __call__(self):
        return self.called_value
    def __init__(self, index, remote_path, remote_name, name = None, frame=None,force=0 ):
        if name is None:
            name = remote_name
        assert remote_path.endswith(".py")
        self.remote_name = remote_name
        self.remote_path = path.Path(remote_path).realpath()
    # def __init__(self, name, data, frame=None, force = 0):
        frame = frame__default(frame)
        def _f(output_kw={}, func = None, input_kw={},skip=1, tag=None, ):
            if func is None:
                func = lambda:None
            # output_kw = _dict(output_kw)
            super( self.__class__, self).__init__(index, func, input_kw, output_kw, force, frame, skip, name, tag)
        _f()

    # @cached_property
    @property
    def remote_index_file(self):
        return self.remote_path + ".index"

    @cached_property
    def remote_node(self):
        # mod = imp.load_source( self.remote_path.replace(), self.remote_path)
        mod = imp.load_source( "remote_pipe", self.remote_path)
        node = getattr(mod, self.remote_name)
        return node
    # def input_kw

    def _hook_indexed_diff_file(self):
        raise IndexedDiffFileError(self)
        # return 1

    def _hook_indexed_missing_file(self):
        return 1

    @cached_property
    def changed(self):
        return 0
        # return self._changed
        
    @cached_property
    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        rec = index_file_read( self.indexFile.path, ).get( self.name, None)
        file_absent = index_file_read( self.remote_index_file)
        # file_absent = os_stat_safe(self.path) == os_stat_result_null
        # file_absent = False
        index_absent = rec is None
        states = [] 

        if index_absent:
            val = 1
            states.append("INDEX_ABSENT")
        else:
            vold = rec['data']
            vnew = self.data
            if vold != vnew:
                if self.VERBOSE:
                    print (zip(vold.keys(),vold.values(),vnew.values()))
                val=1; states.append("DIFF")
                self._hook_indexed_diff_file()
            else:
                val=0; states.append("SAME")

        if self.VERBOSE:
            print("[CheckingChange]:{self.data}.changed={val}.state={states}".format(**locals()))
        return val

    def index_update(self,):
        print (self.indexFile.path)
        print (self.remote_node.indexFile.path)

        return self.index.index_file_update( 
            "%s:%s" % (self.remote_path, self.remote_name)
            self.remote_node.index_update(),
            # index_file_read(self.remote_index_file,).get(self.remote_name)
            # dict(data = self.data),
            # self.path, 
            # dict(stat_result = stat_result)
        )
        # return 
        # print ("[UPDATING_INDEX]%s\n%s"%(self,stat_result.st_mtime))
        # if not file_not_empty(self.path):
        #     path.Path(self.path).dirname()
        #     os.path.makedirs_p()

        # return 

    @cached_property
    def called_value(self,*a,**kw):
        with path.Path(self.remote_path).dirname():
            return self.remote_node.called_value
