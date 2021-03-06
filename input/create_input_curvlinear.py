#!/usr/bin/python
# -*- encoding: utf8 -*-

""" Create metrics, psi, pv fields for a curvlinear grid
"""

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from netCDF4 import Dataset

# maybe temporary
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.fftpack._fftpack import zfft

d2r = np.pi/180.


def create_nc(filename, lon, lat, zc, zf):
    
    ### create a netcdf file
    rootgrp = Dataset(filename, 'w',
                      format='NETCDF4_CLASSIC', clobber=True)

    # create dimensions
    rootgrp.createDimension('x', lon.shape[1])
    rootgrp.createDimension('y', lat.shape[0])
    rootgrp.createDimension('zc', zc.size)
    rootgrp.createDimension('zf', zf.size)
    
    # create variables
    dtype='f8'
    nc_lon = rootgrp.createVariable('lon',dtype,('y','x'))
    nc_lat = rootgrp.createVariable('lat',dtype,('y','x'))
    nc_zc = rootgrp.createVariable('zc',dtype,('zc'))
    nc_zf = rootgrp.createVariable('zf',dtype,('zf'))
    
    nc_lon[:] = lon
    nc_lat[:] = lat
    nc_zc[:] = zc
    nc_zf[:] = zf
        
    #rootgrp.createVariable(name,dtype,('z','y','x',)))
    return rootgrp



if __name__ == "__main__":
    
    # build horizontal coordinates
    lon = np.linspace(-50,-35,150)
    lat = np.linspace(30,40,100)
    LON, LAT = np.meshgrid(lon,lat)
    
    # plot hgrid
    plt.figure(figsize=(8,3))
    ax=plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-55,-30, 25, 45],ccrs.PlateCarree())
    ax.plot(LON[::10,::10],LAT[::10,::10],'k-',transform=ccrs.PlateCarree())
    ax.plot(LON.transpose()[::10,::10],LAT.transpose()[::10,::10],'k-',transform=ccrs.PlateCarree())
    plt.title('Horizontal grid (every 10 points)', size=10) # to modify the title
    lon_tcks = range(-55,-30, 5)
    lat_tcks = range(25,45,5)
    ax.set_xticks(lon_tcks, crs=ccrs.PlateCarree())
    ax.set_yticks(lat_tcks, crs=ccrs.PlateCarree())
    ax.coastlines(resolution='50m') # Currently can be one of “110m”, “50m”, and “10m”
    ax.gridlines()
    #figname='figs/snapshot_'+vkey.replace (" ", "_")+'_magnitude.jpg'
    plt.savefig('figs/curvilinear_input_hgrid.jpg', dpi=300)
    #print figname+' printed'
    
    # build vertical coordinates
    zf = -np.linspace(1,0,11)**2
    zf = 4000*zf
    zc = (zf[:-1]+zf[1:])*0.5
    e3 = np.diff(zf)
    
    
    # plot vertical grid
    plt.figure()
    plt.plot(np.zeros(zf.shape),zf,'kx')
    plt.plot(np.zeros(zc.shape),zc,'k+')
    
    
    # compute metric terms assuming spherical earth
    R = 6371.*1e3;
    E1 = R * np.cos(d2r*LAT)
    E2 = R * np.ones(LON.shape)
    #
    e1 = np.diff(LON,axis=1) *d2r
    e1 = np.hstack((e1,e1[:,[-1]]))    
    e1 = e1 * E1
    #
    e2 = np.diff(LAT,axis=0) *d2r
    e2 = np.vstack((e2,e2[[-1],:]))
    e2 = e2 * E2
    
    
    # plot horizontal metrics
    plt.figure(figsize=(8,3))
    ax=plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-55,-30, 25, 45],ccrs.PlateCarree())
    im = ax.pcolormesh(lon,lat,e1,transform=ccrs.PlateCarree())
    cbar = plt.colorbar(im, format="%.1f")
    plt.title('e1 [m]', size=10) # to modify the title
    lon_tcks = range(-55,-30, 5)
    lat_tcks = range(25,45,5)
    ax.set_xticks(lon_tcks, crs=ccrs.PlateCarree())
    ax.set_yticks(lat_tcks, crs=ccrs.PlateCarree())
    ax.coastlines(resolution='50m') # Currently can be one of “110m”, “50m”, and “10m”
    ax.gridlines()    
    plt.savefig('figs/curvilinear_input_e1.jpg', dpi=300)

    # plot horizontal metrics
    plt.figure(figsize=(8,3))
    ax=plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-55,-30, 25, 45],ccrs.PlateCarree())
    im = ax.pcolormesh(lon,lat,e2,transform=ccrs.PlateCarree())
    cbar = plt.colorbar(im, format="%.1f")
    plt.title('e2 [m]', size=10) # to modify the title
    lon_tcks = range(-55,-30, 5)
    lat_tcks = range(25,45,5)
    ax.set_xticks(lon_tcks, crs=ccrs.PlateCarree())
    ax.set_yticks(lat_tcks, crs=ccrs.PlateCarree())
    ax.coastlines(resolution='50m') # Currently can be one of “110m”, “50m”, and “10m”
    ax.gridlines()    
    plt.savefig('figs/curvilinear_input_e2.jpg', dpi=300)

        
    # store metric terms
    #zc = np.hstack((zc,zc[[-1]]))
    rootgrp = create_nc('curv_metrics.nc', LON, LAT, zc, zf)
    #
    dtype='f8'
    #nc_zf = rootgrp.createVariable('zf',dtype,('zf'))
    #nc_zf[:] = zf
    # 
    nc_e1 = rootgrp.createVariable('e1',dtype,('y','x'))
    nc_e1[:] = e1
    nc_e2 = rootgrp.createVariable('e2',dtype,('y','x'))
    nc_e2[:] = e2
    #nc_e3 = rootgrp.createVariable('e3',dtype,('zc'))
    ##nc_e3[:] = e3.append(e3[-1])
    #nc_e3[:] = np.hstack((e3,e3[[-1]]))
    
    rootgrp.close()
    
    # compute the Coriolis frequency and a reference value
    f = 2.*2.*np.pi/86400.*np.sin(d2r*LAT)
    f0 = np.mean(f)
    
    # create a reference profile
    N2 = 1e-3*(zf-10.)/zf[0]
    # tmp !!
    N2[:] = 1e-5
    print 'Set N2 to a constant = '+str(N2[0])
    #print N2[:]
 
    # create a potential vorticity anomaly
    lon0 = np.mean(lon)
    lat0 = np.mean(lat)
    def dist(lon,lat):
        return R*np.arccos(np.sin(d2r*lat)*np.sin(d2r*lat0) \
                           + np.cos(d2r*lat)*np.cos(d2r*lat0)*np.cos(d2r*(lon-lon0)))
    q = 0.1*f0*np.sin(2.*np.pi*zc[:,np.newaxis,np.newaxis]/zf[0]) \
        * np.exp(-(dist(LON,LAT)[np.newaxis,...]/(100.*1e3))**2) \
        * np.cos(2.*np.pi/(200*1e3)*dist(lon,lat0)) # sinusoidal pattern in the zonal direction
#        * np.cos(2.*np.pi/(2000.*1e3)*dist(lon,lat0)) # single eddy

    # store variables
    rootgrp = create_nc('curv_pv.nc', LON, LAT, zc, zf)
    #
    nc_f = rootgrp.createVariable('f',dtype,('y','x'))
    nc_f[:] = f    
    nc_f0 = rootgrp.createVariable('f0',dtype)
    nc_f0[:] = f0
    #
    nc_N2 = rootgrp.createVariable('N2',dtype,('zf'))
    nc_N2[:] = N2
    #
    nc_q = rootgrp.createVariable('q',dtype,('zc','y','x'))
    nc_q[:] = q[:]
    #
    rootgrp.close()
  
  
    # plot horizontal metrics
    plt.figure(figsize=(8,3))
    ax=plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-55,-30, 25, 45],ccrs.PlateCarree())
    im = ax.pcolormesh(lon,lat,q[5,:,:]/f0,transform=ccrs.PlateCarree())
    cbar = plt.colorbar(im, format="%.2f")
    plt.title('q/f0 [1]', size=10) # to modify the title
    lon_tcks = range(-55,-30, 5)
    lat_tcks = range(25,45,5)
    ax.set_xticks(lon_tcks, crs=ccrs.PlateCarree())
    ax.set_yticks(lat_tcks, crs=ccrs.PlateCarree())
    ax.coastlines(resolution='50m') # Currently can be one of “110m”, “50m”, and “10m”
    ax.gridlines()
    plt.savefig('figs/curvilinear_input_q.jpg', dpi=300)
        
    
    plt.ion()
    plt.show(); 
    
    

