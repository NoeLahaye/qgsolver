#!/usr/bin/python
# -*- encoding: utf8 -*-
from src_parallel.io import read_nc_petsc


"""  Run QG solver for NATL60 input data
"""

import time
import sys

from qgsolver.qg import qg_model
from qgsolver.io import write_nc, read_nc_3D

#================================================================

def nemo_input_runs(ncores_x=2, ncores_y=6, ping_mpi_cfg=False):
    
    """ Set up processing parameters and run qg solver.
    """

    # LMX domain: Nx=1032, Ny=756, Nz=300

    # vertical subdomain
#     vdom = {'kdown': 0, 'kup': 50-1, 'k0': 200 }  
    vdom = {'kdown': 0, 'kup': 10-1, 'k0': 250 }     # linux with mask

    # horizontal subdomain
#     hdom = {'istart': 0, 'iend': 300-1, 'i0': 350,'jstart': 0, 'jend': 300-1,  'j0': 200}
    hdom = {'istart': 0, 'iend': 50-1, 'i0': 410,'jstart': 0, 'jend': 50-1,  'j0': 590}   # linux with mask
    
    # 448=8x56
    # 512=8x64
    
    ncores_x=2; ncores_y=2  # large datarmor

    
    if ping_mpi_cfg:
        # escape before computing
        return ncores_x, ncores_y
    
    else:
        # proceeds with computations
        start_time = time.time()
        cur_time = start_time
    
        # MPI decomposition of the domain
        # case must be defined before ncores for run_caparmor.py
        casename = 'nemo'
    
        # Boundary condition type: 
        #   true boundary conditions: 
        #    'N': Neumann (density-like),
        #    'D': Dirichlet (streamfunction),
        #   estimated boundary conditions: 
        #    'NBG': Neumann-background,
        #    'DBG': Dirichlet-background,
        #    'NOT': Neumann-other
        #    'DOT': Dirichlet-other
        
        bdy_type = {'top':'N', 'bottom':'N', 'lateral': 'D'}
    
        datapath = 'data/'
        hgrid = datapath+'nemo_metrics.nc'
        vgrid = datapath+'nemo_metrics.nc'
        file_q = datapath+'nemo_pv.nc'
        file_psi = datapath+'nemo_psi.nc'
        file_psi_bg = datapath+'nemo_psi_bg.nc'
        file_psi_ot = datapath+'nemo_psi_ot.nc'
        file_rho = datapath+'nemo_rho.nc'
        qg = qg_model(hgrid=hgrid, vgrid=vgrid, f0N2_file=file_q, K=1.e0, dt=0.5 * 86400.e0,
                      vdom=vdom, hdom=hdom, ncores_x=ncores_x, ncores_y=ncores_y, 
                      bdy_type_in=bdy_type, substract_fprime=True)
        qg.case=casename
    
        if qg.rank == 0: print '----------------------------------------------------'
        if qg.rank == 0: print 'Elapsed time for qg_model ', str(time.time() - cur_time)
        cur_time = time.time()
        
        # read 3D variables. 
        read_nc_3D(qg, ['PSI', 'PSI_BG', 'PSI_OT', 'Q', 'RHO'], 
                   [file_psi, file_psi_bg, file_psi_ot, file_q, file_rho])

        
#         # initialize 3D-variables
#         read_return=read_nc_petsc(qg.Q, 'q', file_q, qg, fillmask=0.)
#         if qg.rank == 0: 
#             print '----------------------------------------------------'
#             if read_return==1:
#                 print 'Elapsed time setting Q ', str(time.time() - cur_time)
#             elif read_return==0:
#                 print 'File '+file_q+' does not exist. Program will stop.'
#                 sys.exit()
#         cur_time = time.time()
#     
#         read_return=read_nc_petsc(qg.PSI, 'psi', file_psi, qg, fillmask=0.)
#         if qg.rank == 0: 
#             print '----------------------------------------------------'
#             if read_return==1:
#                 print 'Elapsed time setting PSI ', str(time.time() - cur_time)
#             elif read_return==0:
#                 qg.PSI=None
#                 print 'File '+file_psi+' does not exist. qg.PSI object is set to None.'
#         cur_time = time.time()
# 
#         read_return=read_nc_petsc(qg.PSI_BG, 'psi', file_psi_bg, qg, fillmask=0.)
#         if qg.rank == 0:
#             print '----------------------------------------------------'
#             if read_return==1:
#                 print 'Elapsed time setting PSI_BG ', str(time.time() - cur_time)
#             elif read_return==0:
#                 qg.PSI_BG=None
#                 print 'File '+file_psi_bg+' does not exist. qg.PSI_BG object is set to None.'
#         cur_time = time.time()
#         
#         read_return=read_nc_petsc(qg.PSI_OT, 'psi', file_psi_ot, qg, fillmask=0.)
#         if qg.rank == 0: 
#             print '----------------------------------------------------'
#             if read_return==1:
#                 print 'Elapsed time setting PSI_OT ', str(time.time() - cur_time)
#             elif read_return==0:
#                 qg.PSI_OT=None
#                 print 'File '+file_psi_ot+' does not exist. qg.PSI_OT object is set to None.'
#         cur_time = time.time()
#     
#         read_return=read_nc_petsc(qg.RHO, 'rho', file_rho, qg, fillmask=0.)
#         if qg.rank == 0: 
#             print '----------------------------------------------------'
#             if read_return==1:
#                 print 'Elapsed time setting RHO ', str(time.time() - cur_time)
#             elif read_return==0:
#                 print 'File '+file_rho+' does not exist. Program will stop'
#                 sys.exit()
#         cur_time = time.time()
       
        # qg.VAR must be set to None if not used
        write_nc([qg.PSI, qg.PSI_BG, qg.PSI_OT, qg.Q], ['psi', 'psi', 'psi', 'q'], 'data/input.nc', qg)

        if qg.rank == 0: print '----------------------------------------------------'
        if qg.rank == 0: print 'Elapsed time for write_nc ', str(time.time() - cur_time)
        cur_time = time.time()
    
        qg.pvinv.solve(qg)
        if qg.rank == 0: print '----------------------------------------------------'
        if qg.rank == 0: print 'Elapsed time for invert_pv ', str(time.time() - cur_time)
        cur_time = time.time()

        write_nc([qg.PSI, qg.Q], ['psi', 'q'], 'data/output.nc', qg)
        if qg.rank == 0: print '----------------------------------------------------'
        if qg.rank == 0: print 'Elapsed time for write_nc ', str(time.time() - cur_time)
        cur_time = time.time()
    
        if qg.rank == 0: print '----------------------------------------------------'
        if qg.rank == 0: print 'Elapsed time  ', str(cur_time - start_time)
    
        return qg


def main(ping_mpi_cfg=False):    
    
    qg = nemo_input_runs(ping_mpi_cfg=ping_mpi_cfg)
        
    if ping_mpi_cfg:
        return qg[0], qg[1]
    elif qg._verbose:
        print 'Test done \n'


if __name__ == "__main__":
    main()   