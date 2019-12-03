from collections import OrderedDict as _dict
import subprocess

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
