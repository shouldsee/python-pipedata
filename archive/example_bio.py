# from delay_and_cache import delay_and_cache as _dac
from delay_and_cache import cacheThisFrame as _ctf
# from delay_and_cache import CachedProxy
from delay_and_cache import frame__default
from pymisca.header import func__setAsAttr as _attach

import inspect
import functools
def _open(*a):
    assert isinstance(a[0])
class BaseFile(object):
    _DEBUG = 1
    def __call__(self,*a,**kw):
        return self
    def __init__(self, path):
        self._path=path
    def open(self,*a, **kw):
        return open(self._path,*a, **kw)
    
class InputFile(BaseFile):
    def changed(self, ):
        if self._DEBUG:
            return 1
        '''
        Decide whether this file has changed since last run.
        '''
        pass
    
class CachedFile(BaseFile):    
    def changed(self, ):
        if self._DEBUG:
            return 1
        '''
        Decide whether this file has changed since last run.
        '''
        pass
    
    def __init__(self, path, frame=None):
        self._frame = frame__default(frame)
        super(CachedFile,self).__init__(path)
        
    def upstream_changed(self,):
        _frame = self._frame
        return 1
#     def open(self, *a,**kw):
#         pass
#     pass
#     def __init__(self,)
# CachedProxy._DEBUG = 1

import os        


INPUT_FILE = InputFile('test_R1_.fastq')
INPUT_GENOME = 'test.fa'

def func__addSelf(f):
    def g(*a,**kw):
#         kw['self'] = f
        return f(f,*a,**kw)
    return functools.wraps(f)(g)
def func__fill_defaults(f):
    d = frame__default().f_locals
    (args, varargs, keywords, defaults) = inspect.getargspec(f)
    for key in args[:len(args) - len(defaults)]:
        defaults = (d[key],)+defaults
    f.__defaults__ = defaults
#             (args, varargs, keywords, defaults) = inspect.getargspec(func)
    return f

def _output_kw(okw):
    def _dec(func):
        assert 'return_value' not in okw, (okw.keys(), func)
        
        func.output_kw =  okw
        
        
        def gunc(*a,**kw):
            
#             (args, varargs, keywords, defaults) = inspect.getargspec(func)
#             input_kw = zip()
            @_attach(func)
            def upstream_changed(a=a,kw=kw):
                print "123",a,kw
                for ele in a + tuple(kw.values()):
                    print ele                    
                return 1
#             kw['self'] = gunc
            okw['return_value'] = func(func,*a,**kw)
            return okw
        gunc = functools.wraps(func)(gunc)
        return gunc 
#         gunc = func__addSelf(gunc)        
    return _dec

# @_input_kw(dict)
@_output_kw({
    "BAM":CachedFile("test.fastq.bam" )
})
@func__fill_defaults
def make_bam( self, INPUT_FILE):
#     if INPUT_FILE().changed():
    if self.upstream_changed():
        print("RUNNING:%s"%self)
        lines = list( INPUT_FILE().open('r') )
        with self.output_kw['BAM'].open("w") as f:
            f.write(str(lines))
    else:
        print("SKIPPING:%s"%self)
        pass
    return

@_output_kw({})
def make_csv( self, make_bam=make_bam, ):
    make_bam()
#     print make_bam()['BAM']
    return 1


if __name__ == '__main__':
    os.chdir("tests/")
    make_csv()
#     print("[middle]",middle())