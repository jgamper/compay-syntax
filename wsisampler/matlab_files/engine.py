import os

try:
    import matlab
    from matlab import engine
except ImportError:
    raise ImportError('No MATLAB engine found.')

def get_matlab_engine():
    """
    Returns matlab engine with path to functions for WSI appended
    """
    matlab_dir = os.path.dirname(__file__)
    eng = engine.start_matlab()
    eng.cd(r'{}'.format(matlab_dir), nargout=0)
    return eng
