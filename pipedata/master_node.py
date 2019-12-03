from pipedata.base import cached_property,_dict, dumper
from pipedata._ast_util import ast_proj
from pipedata.abstract_node import AbstractNode

from path import Path
import re
from pipedata.base import os_stat_safe

class MasterNode(AbstractNode):
    @property
    def recordId(self):
        return self.name
    def __getitem__(self,key):
        return self.output_kw[key]

    def __init__(self, index, func, input_kw, output_kw,  name, force, ):
        self.force= force
        super( MasterNode, self).__init__( index, func, input_kw, output_kw, name)

    @classmethod
    def from_func(cls, index, output_kw = {}, force=0,name = None ):
        def _dec(func):
            input_kw = {}
            self = cls(index, func, input_kw, output_kw,  name, force,)
            # self.initalised_tuples
            return self        
        return _dec        


    @property
    def changed(self):
        return any(self._changed_tuple)

    @staticmethod
    def _hook_changed_output(self,recOld,recNew):
        for k in recOld['output_snapshot']:
            v1 = recOld['output_snapshot'][k]
            v2 = recNew['output_snapshot'][k]
            if v1!=v2:
                print(self,k,v1,v2)
        raise self.ChangedOutputError("output for %s has changed since snapshot"%self)


    def _hook_changed_record(self, changed_self,changed_input):
        return 

    @cached_property
    def _changed_tuple(self):    
        recOld = self.get_record()
        recNew = self.as_record().copy()
        recs = [recOld,recNew]
        if recOld is None:
            # print("[CHANGED_INDEX_ABSENT]%s%s"%(self.index,self))
            # self._hook_noindex()
            changed_self, changed_input, changed_output = 1,1,1

        else:
            if recOld != recNew:
                diff = _dict()
                for rec in recs:
                    rec['self']['ast_tree'] =ast_proj('\n'.join( rec['self'].pop('sourcelines')) )
                # trees = [ ast_proj('\n'.join( rec['sourcelines'])) for rec in recs ]
                # changed_self = trees[0] != trees[1]
                changed_self = recOld['self'] != recNew['self']
                changed_input = recOld['input_snapshot'] != recNew['input_snapshot']
                changed_output = recOld['output_snapshot'] != recNew['output_snapshot']
                if changed_output:
                    self._hook_changed_output(self, recOld,recNew)
                # print("[CHANGED_DIFF](%s,%s,%s),%s%s"%(changed_self,changed_input,changed_output,self,self.index,))
                changed_self, changed_input,changed_output
                self._hook_changed_record(changed_self, changed_input)
            else:
                # print("[CHANGED_SAME]%s%s"%(self.index,self))
                changed_self, changed_input, changed_output = 0,0,0
        changed_input = 0
        return (changed_self,changed_input,changed_output)
        
    def as_snapshot(self):
        return _dict([
        ('class', self.__class__.__name__),
        ('self',_dict( [('sourcelines', self._get_func_code(self.func).splitlines())]) ),
        # ('self',[('sourcelines', self._get_func_code(self.func).splitlines())]),
        ('output_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        ])
        return self.as_record()
    def as_record(self,):
        return _dict([
        ('class', self.__class__.__name__),
        ('self',_dict( [('sourcelines', self._get_func_code(self.func).splitlines())]) ),
        # ('sourcelines', self._get_func_code(self.func).splitlines()),
        ('input_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.input_kw.items() ])),
        ('output_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        ])


class SlaveNode(AbstractNode):
    class DanglingSlaveError(Exception):
        pass

    @cached_property
    def master(self):
        '''
        Graph completion stage
        Look up local index for master
        '''
        res = []
        for x in self.index.node_dict.values():
            if self in x.output_kw.values():
                res.append(x)
        if len(res)!=1:
            raise self.DanglingSlaveError("Parent for %s is %s"%(self,res))
        return res[0]

    @property
    def changed(self):
        return self.master.changed
    @property
    def changed_upstream(self):
        return self.master.changed_upstream
    @property
    def called_value(self,):
        if not self.master.running:
            self.master.called_value
        return self
    def as_snapshot(self):
        return self.as_record()
    def as_record(self):
        assert 0,"Must return a self-contained record"
    def recordId(self):
        assert 0, "must be informative"
        return 


class SlaveFile(SlaveNode):

    def __init__(self, index,  path,):
        func = lambda:None
        input_kw = {}
        output_kw = {}
        name = re.sub('[^a-zA-Z0-9_]','_',path)
        # super( self.__class__, self).__init__(index, func,  input_kw, output_kw, name, )
        super( SlaveFile, self).__init__(index, func,  input_kw, output_kw, name, )
        self.path=Path(path )

    def realpath(self):
        return self.index.path.dirname()/self.path

    @property
    def recordId(self):
        return self.path

    def as_record(self, ):
        # stat_result =os.stat(self.realpath())
        stat_result =os_stat_safe(self.realpath())
        # print ("[UPDATING_INDEX]%s\n%s"%(self,stat_result.st_mtime,))
        return dumper._loads( dumper._dumps( dict(stat_result = stat_result)))


class AutoMasterNode(MasterNode):
    # ChangedOutputError = 
    # class ChangedSelfError(MasterNoed.ChangedError):
    #     pass
    # ChangedOutputError = ChangedSelfError
    def _hook_changed_output(self,recOld,recNew):
        for k in recOld['output_snapshot']:
            v1 = recOld['output_snapshot'][k]
            v2 = recNew['output_snapshot'][k]
            if v1!=v2:
                print(self,k,v1,v2)        
        raise self.ChangedSelfError(self)

    def _get_called_value(self,*a,**kw):
        super(AutoMasterNode,self)._get_called_value()
        return self.output_kw['_SLAVE']
    pass


class SelfSlaveFile(SlaveFile):
    _ = '''

    A SelfSlaveFile is really an empty MasterNode with a SlaveFile.
    Upon file change, it triggers a custom hook
    '''
    @staticmethod
    def _hook_changed_output(self,recOld,recNew):
        print("[FILE_UPDATED] %s"%self)
    
    def __init__(self, index, path, name = None):
        # super(self.__class__, self).__init__(index,path)
        super(SelfSlaveFile, self).__init__(index,path)
        func = lambda: self
        input_kw = {}
        output_kw = {'_SLAVE': self}
        if name is None:
            name = '_AutoMasterNode_' + self.name 
        # assert 0,name
        force=0
        # class _AutoMasterNode(AutoMasterNode):
        self._master = AutoMasterNode(index, func, input_kw, output_kw, name, force, )
        self._master._hook_changed_output = self._hook_changed_output


InputFile = SelfSlaveFile

    # def changed(self):
    #     pass
    # def changed_upstream(self):
    #     pass