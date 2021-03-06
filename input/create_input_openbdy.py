#!/usr/bin/python
# -*- encoding: utf8 -*-

""" Test the basic features of the library:
Setup of uniform grid
PV inversion of an analytical PV distribution
"""

#import qgsolver.qg as qg
from qgsolver.qg import qg
from qgsolver.io import write_nc

if __name__ == "__main__":
    
    qg = qg(hgrid = {'Nx':150, 'Ny':100}, vgrid = {'Nz':3 },
            K = 0.e0, dt = 0.5*86400.e0)
    #
    qg.set_q()
    qg.invert_pv()
    write_nc([qg.PSI, qg.Q], ['psi', 'q'], 'output.nc', qg)
    #
    test=2
    if test==0:
        # one time step and store
        qg.tstep(1)
        write_nc([qg.PSI, qg.Q], ['psi', 'q'], 'output.nc', qg, create=False)
    elif test==1:
        # write/read/write
        qg.tstep(1)
        write_nc([qg.PSI, qg.Q], ['psi', 'q'], 'output1.nc', qg, create=True)
        qg.set_q(file_q='output.nc')
        qg.tstep(1)
        write_nc([qg.PSI, qg.Q], ['psi', 'q'], 'output1.nc', qg, create=False)
    else:
        while qg.tstepper.t/86400. < 200 :
            qg.tstep(1)
            write_nc([qg.PSI, qg.Q], ['psi', 'q'], 'output.nc', qg, create=False)

    if qg._verbose:
        print 'Test done \n'
