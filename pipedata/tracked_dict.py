from pipedata.base import cached_property,frame__default,_dict
from pipedata.base import IndexedDiffFileError
from pipedata.base import RawNode

class TrackedDict(RawNode):
    def __repr__(self,):
        return 'TrackedDict(index=%s, name=%r,force=%r,data=%r,)'%(self.index, self.name, self.force, self.data.items())

    def __call__(self,*a,**kw):
        return self

    def __init__(self, index, name, data, frame=None, force = 0):
        self.data = _dict(data)
        frame = frame__default(frame)
        def _f(output_kw={}, func = None, input_kw={},skip=1, tag=None, ):
            if func is None:
                func = lambda:None
            # output_kw = _dict(output_kw)
            super( self.__class__, self).__init__(index, func, input_kw, output_kw, force, frame, skip, name, tag)
        _f()

    def _hook_indexed_diff_file(self):
        raise IndexedDiffFileError(self)
        # return 1

    def _hook_indexed_missing_file(self):
        return 1

    @cached_property
    def changed(self):
        return self._changed
        
    @cached_property
    def _changed(self, ):
        '''
        A cached file 
         A file is changed  since last run if 
            - if the file is not indexed
            - if mtime or size is different
        '''
        rec = self.get_record()
        # file_absent = os_stat_safe(self.path) == os_stat_result_null
        file_absent = False
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
    def as_record(self):
        return dict(data = self.data)

    # def _index_update(self,):

    #     # print ("[UPDATING_INDEX]%s\n%s"%(self,stat_result.st_mtime))
    #     # if not file_not_empty(self.path):
    #     #     path.Path(self.path).dirname()
    #     #     os.path.makedirs_p()
    #     self.index.index_file_update( 
    #         self.name, 
    #         dict(data = self.data),
    #         # self.path, 
    #         # dict(stat_result = stat_result)
    #     )
    #     return 