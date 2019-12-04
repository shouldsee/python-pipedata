from collections import OrderedDict as _dict
import subprocess

import inspect

import asciitree
from asciitree.drawing import BOX_DOUBLE

def _dbgf():        
    import pdb,traceback
    print(traceback.format_exc())
    import traceback
    traceback.print_stack()
    traceback.print_exc()
    pdb.set_trace()    
def _dbgfs():        
    import pdb,traceback
    pdb.set_trace()    

def dict_flatten(d,k0='',sep='.',idFunc = lambda x:x,out=None):
    if out is None:
        out= []
    for _k,v in d.iteritems():
        k = idFunc(_k)
        k = sep.join((k0,k))
        out.append((k+'_KEY', _k))
        if isinstance(v,dict) and len(v):
            dict_flatten(v,k,sep, idFunc, out)
        else:
            out.append((k,v))

    return _dict(out)


def _tree_as_string(d):
    if len(d)!=1:
        d=dict(ROOT=d)
    box_tr = asciitree.LeftAligned(draw=asciitree.BoxStyle(gfx=BOX_DOUBLE, horiz_len=1))(d)
    return box_tr


def _get_upstream_tree(lst):
    fmt = lambda x:"%s:%s"%(x.__class__.__name__,x.recordId)
    d = _dict([(fmt(x), 
        _get_upstream_tree(x.input_kw.values())) for x in lst])
    return d

_ID = lambda x:(x.index,x)
def _get_root_nodes(self,exclude=None):
    if exclude is None:
        exclude = set()
    exclude = set(_ID(x) for x in exclude)
    
    it = _get_upstream_graph(self,)
    it = [x for x in it if x[0] not in exclude]
    rootNodes, leafNodes = zip(*it)
    # return 

    # print set(rootNodes),set(leafNodes)
    return set(rootNodes)  - set(leafNodes) 

def _get_upstream_graph(self, edgelist=None):
    if edgelist is None:
        edgelist = []
    for x in self.input_kw.values():
        edgelist.append(( _ID(self),  _ID(x)))
        _get_upstream_graph(x, edgelist)
    return edgelist


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
def _shell(cmd,debug=0,silent=0,
              executable=None,
              encoding='utf8',error='raise',
#               env = None,
              shell = 1,
              getSuccessCode = False,
              raw = False,
              **kwargs
             ):
    if executable is None:
        executable = "bash"
    if not silent:
        buf = '[CMD]{cmd}\n'.format(**locals())
        sys.stderr.write(buf)

    # if debug:
    #     return 'dbg'
    try:
        res = subprocess.check_output(cmd,shell=shell,
#                                           env=_env,
                                     executable=executable,
                                     **kwargs)

        if encoding is not None:
            res=  res.decode(encoding)
        res = res.rstrip() if not raw else res
        suc = True
    except subprocess.CalledProcessError as e:
        errMsg = u"command '{}' return with error (code {}): {}\
            ".format(e.cmd, e.returncode, e.output)
        e = RuntimeError(
                errMsg)
        if error=='raise':
            raise e
        elif error=='ignore':
            res = (errMsg)
            suc = False
     #### allow name to be returned
    if getSuccessCode:
        return suc,res
    else:
        return res

def frame_default(frame=None):
    '''
    return the calling frame unless specified
    '''
    if frame is None:
        frame = inspect.currentframe().f_back.f_back ####parent of caller by default
    else:
        pass    
    return frame
frame__default = frame_default