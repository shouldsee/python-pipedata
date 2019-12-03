
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



    def __init__(self, index, func, input_kw, output_kw, force, frame, skip, name, tag, ):
        assert 0,"obsolete"
        # input_kw = None
        # output_kw = None
        frame = frame__default(frame)
        if output_kw is None:
            output_kw = _dict()
        self.tag = tag
        self.force = force
        super( RawNode,self).__init__( index, func, {}, output_kw, name)


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





def func__addSelf(f):
    def g(*a,**kw):
#         kw['self'] = f
        return f(f,*a,**kw)
    return functools.wraps(f)(g)

def NodeFromFunc(*a,**kw):
    return RawNode.from_func(*a,**kw)


class ______________TrackedFile(RawNode):    

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
        return dumper._loads( dumper._dumps( dict(stat_result = stat_result)))



