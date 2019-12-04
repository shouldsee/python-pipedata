from pipedata.base import cached_property,_dict, dumper
from pipedata._ast_util import ast_proj
from pipedata.abstract_node import AbstractNode

from path import Path
import re
from pipedata.base import os_stat_safe



class MasterNode(AbstractNode):
    DEBUG_SOURCE_CHANGE= 0
    DEBUG_CHANGE_TUPLE = 1
    @property
    def recordId(self):
        return self.name
    def __getitem__(self,key):
        return self.output_kw[key]

    def __init__(self, index, func, input_kw, output_kw,  name, force, frame=None):
        self.force= force
        super( MasterNode, self).__init__( index, func, input_kw, output_kw, name, )
        # self.frame_default(frame))

    @classmethod
    def from_func(cls, index, output_kw = {}, force=0,name = None ):
        def _dec(func):
            input_kw = {}
            self = cls(index, func, input_kw, output_kw,  name, force,)
            # self.initalised_tuples
            return self        
        return _dec        



    @staticmethod
    def _hook_changed_output(self,recOld,recNew):
        raise self.ChangedOutputError("output for %s has changed since snapshot"%self)

    def _hook_changed_record(self, changed_self,changed_input):
        return 

    def get_upstream_tree(self):
        d = _get_upstream_tree(self,)
        return d

    @property
    def changed(self):
        return any(self.changed_tuple)

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


    @cached_property
    def changed_upstream( self,):
        return self.changed_upstream_safe
        self.input_kw
        return (
            [x for x in self.input_kw.values() if any([ x.changed_upstream, x.changed])]
            + [self] if (self.changed_tuple[0:2])==(0,1) else []
            )


    @cached_property
    def changed_upstream_safe( self,):
        self.input_kw
        # lst = []
        _set = set()
        for x in self.input_kw.values():
            if any([ x.changed_upstream_safe, x.changed_safe[0]]):
                # if x.changed_upstream:
                    # lst.append(x.changed_upstream)
                _set.update(x.changed_upstream_safe)
                _set.add((x,x.changed_safe[1]))
                # _set.add((x,None))
        if (self.changed_tuple_safe[0:2]==(0,1)):
            # _set.add((self,self.changed_safe))
            _set.add((self,self.changed_safe[1]))
            # _set.add((self,self.changed_safe))
            # lst.append((self,self.changed_safe))
        return _set


    @cached_property
    def changed_tuple_safe(self):    
        recOld = self.get_record()
        # .copy()
        recNew = self.as_record()
        # .copy()
        recs = [recOld,recNew]
        if not recOld:
            # print("[CHANGED_INDEX_ABSENT]%s%s"%(self.index,self))
            # self._hook_noindex()
            changed_self, changed_input, changed_output,changed_noindex = 0,0,0,1

        else:
            changed_noindex = 0
            if recOld != recNew:
                changed_self = recOld['self'] != recNew['self']
                changed_input = recOld['input_snapshot'] != recNew['input_snapshot']
                changed_output = recOld['output_snapshot'] != recNew['output_snapshot']
                if self.DEBUG_SOURCE_CHANGE and changed_self:    
                    print (dumper._dumps([recOld.get('meta'),recNew.get('meta') ]))
                # if changed_output:
                #     self._hook_changed_output(self, recOld,recNew)
                # print("[CHANGED_DIFF](%s,%s,%s),%s%s"%(changed_self,changed_input,changed_output,self,self.index,))
                changed_self, changed_input, changed_output,changed_noindex
                # self._hook_changed_record(changed_self, changed_input)
            else:
                # print("[CHANGED_SAME]%s%s"%(self.index,self))
                changed_self, changed_input, changed_output,changed_noindex = 0,0,0,changed_noindex

        # changed_input = 0
        if self.DEBUG_CHANGE_TUPLE:
            print("[CHANGED_TUPLE](%d,%d,%d,%d),%s,%s"%(
                changed_self,changed_input,changed_output,changed_noindex,self.recordId,
                # self.__class__,
                self.index.__hash__()
                )
            )
        return (changed_self,changed_input,changed_output,changed_noindex)

    @cached_property
    def changed_tuple(self,):
        changed_self, changed_input, changed_output,changed_noindex = self.changed_tuple_safe
        if changed_output:
            self._hook_changed_output(self, {},{})
        if any(self.changed_tuple_safe[:3]):
            self._hook_changed_record(changed_self, changed_input)
        return self.changed_tuple_safe


    def get_source(self):
        return  self._get_func_code(self.func)
    def as_snapshot(self):
        return _dict([
        ('class', self.__class__.__name__),
        # ('recordId',self.recordId),
        ('self',_dict([('ast_tree',  ast_proj(self.get_source()) )])),
        ('meta',_dict( [
            ('sourcelines',  self.get_source().splitlines()),
            # ('output_alias_dict',_dict([(v.recordId,k) for k,v in self.output_kw.items()]))
            ]) ),
        ('output_snapshot', _dict( [ ( k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        ])
        return self.as_record()
    def as_record(self,):
        # d = self.as_snapshot()
        return _dict([
        ('class', self.__class__.__name__),
        # ('recordId',self.recordId),
        ('self',_dict([('ast_tree',  ast_proj(self.get_source()) )])),
        ('meta',_dict( [
            ('sourcelines',  self.get_source().splitlines()),
            # ('output_alias_dict',_dict([(v.recordId,k) for k,v in self.output_kw.items()]))
            ]) ),
        ('input_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.input_kw.items() ])),
        ('output_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        # ('output_snapshot', _dict( [ (k, v.as_snapshot()) for k,v in self.output_kw.items() ])),
        ])


class SlaveNode(AbstractNode):
# class SlaveNode(object):
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
    def changed_safe(self):
        # assert 0
        return self.master.changed_safe
    @property
    def changed_upstream_safe(self):
        # assert 0
        # print(s)
        return self.master.changed_upstream_safe

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

    def _index_update(self):
        ' Slave is contained in the MasterNode.as_data()["output_snapshots"]'
        pass

    # def _attach_to_root(self):
    #     '''
    #     Usually one would not need to directly get slave from node dict, 
    #     but from the MasterNode.output_kw instead
    #     '''
    #     self.index.node_dict["_SLAVE_" +self.recordId] = self


class SlaveFile(SlaveNode):
    def __repr__(self,):
        s = ','.join('%s="%s"'%(k, (getattr(self,k))) 
            for k in ['path', 'name',])
        s = '%s(index=index,%s)\n### index=%r'%(self.__class__.__name__,s,self.index)
        return s

    def __init__(self, index,  path, name = None, frame=None):
        func = lambda:None
        input_kw = {}
        output_kw = {}
        if name is None:
            name = re.sub('[^a-zA-Z0-9_]','_',path)
        # super( self.__class__, self).__init__(index, func,  input_kw, output_kw, name, )
        # super( SlaveFile, self).__init__(index, func,  input_kw, output_kw, name, self.frame_default(frame) )
        self.relpath=Path(path )
        super( SlaveFile, self).__init__(index, func,  input_kw, output_kw, name, )
        if self.__class__ == SlaveFile:
            assert self.realpath().startswith(self.index.path.dirname()),"Slave file must be in project directory"
        # assert not self.relpath.startswith('/'),

    @property
    def path(self):
        return self.realpath()
    
    def realpath(self):
        return self.index.path.dirname()/self.relpath

    @property
    def recordId(self):
        return self.relpath
        
    @property
    def name(self):
        return self.relpath

    def as_record(self, ):
        # stat_result =os.stat(self.realpath())
        stat_result =os_stat_safe(self.realpath())
        # print ("[UPDATING_INDEX]%s\n%s"%(self,stat_result.st_mtime,))
        return dumper._loads( dumper._dumps( dict(recordId=self.recordId, stat_result = stat_result)))



class AutoMasterNode(MasterNode):
    _slave = None
    def __init__(self, index, func, input_kw, output_kw, name, force,slave,  ):
        self._slave = slave
        super(AutoMasterNode,self).__init__(index, func, input_kw, output_kw, name, force, )
        return     
    # ChangedOutputError = 
    # class ChangedSelfError(MasterNoed.ChangedError):
    #     pass
    # ChangedOutputError = ChangedSelfError
    _slave = None
    def _hook_changed_output(self,recOld,recNew):
        # for k in recOld['output_snapshot']:
        #     v1 = recOld['output_snapshot'][k]
        #     v2 = recNew['output_snapshot'][k]
        #     if v1!=v2:
        #         print(self,k,v1,v2)        
        raise self.ChangedSelfError(self)

    def _get_called_value(self,*a,**kw):
        super(AutoMasterNode,self)._get_called_value()
        # return self.output_kw[self._slave.recordId]
        return self.output_kw["_SLAVE"]
        # '_SLAVE']
    # def _
    # pass
    @property
    def recordId(self):
        return self._slave.recordId


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
        # output_kw = {self.recordId: self}
        if name is None:
            name = '_AutoMasterNode_' + self.name 
        force=0
        # class _AutoMasterNode(AutoMasterNode):
        self._master = AutoMasterNode(index, func, input_kw, output_kw, name, force, self)
        self._master._hook_changed_output = self._hook_changed_output
        self._master._slave = self



InputFile = SelfSlaveFile

    # def changed(self):
    #     pass
    # def changed_upstream(self):
    #     pass