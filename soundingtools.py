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
    
    def makeCM1sounding(self,z,savename=None,top=12000):
        # z, top in meters

        from thermodynamics import Ttotheta

        # Get qv from Td if qv doesn't already exist.
        try: self.qv
        except: self.qv = dewpointtoqv(self.Td,self.T,self.p)
   
        # Add z to sounding object and calculate potential temperature.
        self.z = z
        self.theta = Ttotheta(self.T,self.p) 

        # Write the text to a file if a file name is specified.
        if savename is not None:
            f = open(savename,'w')

            # Make sure to write qv in g/kg.
            # First, write the ground data.
            string = "%.4f" % self.p[0]+"  "+"%.4f" % self.theta[0]+"  "+"%.4f" % (1000*self.qv[0])+"\n"
            f.write(string)

            # Next, write the rest of the data.
            for j in range(1,len(self.p)):
                string = "%.4f" % self.z[j] + "  " + "%.4f" % self.theta[j] + "  " + "%.4f" % (1000*self.qv[j]) + "  " + "%.4f" % self.u[j] + "  " + "%.4f" % self.v[j] + "\n"
                f.write(string)

            # Make the sounding have same state through remainder of stratosphere to top of model domain.
            if max(self.z) < top:
           
                from thermodynamics import virtualT
                from numpy import exp

                g, Rd = 9.81, 287

                # First, calculate pressure at top by using hypsometric equation.
                dz = top-self.z[-1]
                Tv = virtualT(self.p[-1],self.T[-1],self.qv[-1])
                ptop = self.p[-1]/exp(g*dz/(Rd*Tv))

                # Then calculate theta at top.
                thetatop = Ttotheta(self.T[-1],ptop)

                # Write a line for synthetic sounding data at top.
                string = "%.4f" % top + "  " + "%.4f" % thetatop + "  " + "%.4f" % (1000*self.qv[-1]) + "  " + "%.4f" % self.u[-1] + "  " + "%.4f" % self.v[-1] + "\n"
                f.write(string)

            f.close()

        else:
            print('No path was specified for writing the sounding. Failing gracefully.')

    #*******************************************************************
    
    @property
    def CRH(self): 

        # Returns: Column relative humidity (unitless) as a float.

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

        # Returns CAPE and CIN (J/kg) as a tuple..

        from metpy.units import units
        from metpy.calc import mixed_layer_cape_cin as mlcc

        return mlcc(self.p*units.hPa,self.T*units.K,self.Td*units.K)

    #*******************************************************************





