import rpc_client
import h5py
import numpy as np
import base64
import json
from collections import OrderedDict




#  0 -  3  Version = 1          (uint32)
#  4       'G'                  (byte)
#  5       'F'                  (byte)
#  6       'A'                  (byte)
#  7       0                    (byte)
#  8 - 15  number of rows       (int64)
# 16 - 23  number of columns    (int64)
# 24 - 31  0                    (int64)
# 32 - 39  0                    (int64)
# 40 - ..  matrix data elements (float64)
#          [0,0] [0,1] ... [0,ncols-1]
#          [1,0] [1,1] ... [1,ncols-1]
#          ...
#          [nrows-1,0] ... [nrows-1,ncols-1]
def toMatBase64(array):
    """
    returns s,v
    s - a base64 encoded string containing the bytes in a format compatible with
    gonum.mat.Dense.MarshalBinary, header version 1
    v - the value that was base64 encoded, is of a custom np.dtype specific to the length of the projectors
    array - an np.array with dtype float64 (or convertable to float64)
    """
    ncol, nrow = array.shape
    dt = np.dtype([('version', np.uint32), ('magic', np.uint8, (4,)), ("nrow", np.int64),
               ("ncol",np.int64), ("zeros",np.int64,2), ("data", np.float64,nrow*ncol)])
    a = np.array([( 1,[ord("G"),ord("F"),ord("A"),0],nrow,ncol,[0,0],array.ravel())],dt)
    s = base64.b64encode(a)
    return s, a[0]

def getConfigs(filename):
    """
    returns an OrderedDict mapping channel number to a dict for use in calling
    self.client.call("SourceControl.ConfigureProjectorsBasis", config)
    to set Projectors and Bases
    extracts the channel numbers and projectors and basis from the h5 file
    filename - points to a _model.h5 file created by Pope
    """
    out = OrderedDict()
    if not h5py.is_hdf5(filename):
        print("{} is not a valid hdf5 file")
        return out
    h5 = h5py.File(filename,"r")
    for key in h5.keys():
        channum = int(key)
        projectors = h5[key]["svdbasis"]["projectors"].value
        basis = h5[key]["svdbasis"]["basis"].value
        config = {
            "ProcessorInd": channum,
            "ProjectorsBase64": toMatBase64(projectors)[0],
            "BasisBase64": toMatBase64(basis)[0],
        }
        out[channum]=config
    return out
