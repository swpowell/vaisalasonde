class Sounding:

    def __init__(self,p,T,Td,u=None,v=None):
        # p in hPa, T, Td in K
        
        from thermodynamics import dewpointtoqv

        self.p = p
        self.T = T
        self.Td = Td
        if u is not None and v is not None:
            self.u = u
            self.v = v

        # Get qv from Td.
        self.qv = dewpointtoqv(self.Td,self.T,self.p)
    

    #*******************************************************************

    def plot(self,savename=None):
        # p in hPa, T and Td in K, qv in kg/kg.
        # u and v (optional) in m/s.
        # All inputs are 1-D arrays.

        from matplotlib import pyplot as plt
        from metpy.units import units
        from metpy.plots import SkewT
        import numpy as np

        plt.rcParams['figure.figsize'] = (6,8)

        # Set lower limit for plotting on p-axis.
        maxp = np.max(self.p)

        skew = SkewT()

        # Plot data.
        skew.plot(self.p*units.hPa, self.T*units.K, 'r')
        skew.plot(self.p*units.hPa, self.Td*units.K, 'g')
        if self.u is not None and self.v is not None:
            skew.plot_barbs((self.p*units.hPa)[::100],(self.u*units.meters/units.seconds)[::100],(self.v*units.meters/units.seconds)[::100])

        # Add some lines and labels.
        skew.plot_dry_adiabats()
        skew.plot_moist_adiabats()
        skew.plot_mixing_lines()
        skew.ax.set_ylabel('Pressure (hPa)')
        skew.ax.set_xlabel(r'Temperature ($^{\circ}$C), Mixing Ratio (g kg$^{-1}$)')
        # Set lower limit for plotting on p-axis.
        skew.ax.set_ylim(max(maxp,1000),100)

        # Save plot to a file based on input name.
        if savename is not None:
            fig = plt.gcf()
            fig.savefig(savename)

    #*******************************************************************
    
    @property
    def CRH(self): 

        import numpy as np
        from thermodynamics import getqvsat

        g = 9.81

        # Get saturation qv.
        qsat = getqvsat(self.p,self.T)
        dP = np.gradient(self.p,axis=0)

        return np.nansum(self.qv*dP/g,axis=0)/np.nansum(qsat*dP/g,axis=0)

    #*******************************************************************

    @property
    def CAPE_CIN(self):

        # Returns CAPE and CIN (J/kg).

        from metpy.units import units
        from metpy.calc import mixed_layer_cape_cin as mlcc

        return mlcc(self.p*units.hPa,self.T*units.K,self.Td*units.K)

    #*******************************************************************





