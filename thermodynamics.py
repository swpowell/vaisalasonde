#**************************************************************************************


def w2q(w):
  return w/(1+w)


#**************************************************************************************


def q2w(qv):
  return qv/(1-qv)


#**************************************************************************************


def getRH(qv,T,p):

  # T in K, p in hPa, qv in kg/kg.
  
  qsat = getqvsat(p,T)

  return qv/qsat


#**************************************************************************************


def RHtoqv(T,RH,p):

  # T in K; RH as fraction 0 to 1; p in hPa.

  esat = getsaturationvaporpressure(T)
  wsat = 0.622*esat/(p-esat)
  qsat = wsat/(1+wsat)

  return RH*qsat


#**************************************************************************************


def virtualT(p,T,qv):

  # T in K; p in hPa, qv in kg/kg.
  e = getvaporpressure(p,T,qv)
  w = q2w(qv)
  eps = w*(p/e-1)
  
  return T / ( 1 - e/p*(1-eps) )

  #return T*(1+0.61*q2w(qv))


#**************************************************************************************


def getsaturationvaporpressure(T):

  # T in K.

  import numpy as np
  
  Tc = T-273.15

  esat = np.empty_like(Tc)
  esat[Tc>0] = 6.108*np.exp((17.27*Tc[Tc>0])/(Tc[Tc>0]+237.3))
  esat[Tc<=0] = 6.108*np.exp((21.875*Tc[Tc<=0])/(Tc[Tc<=0]+265.5))

  return esat


#**************************************************************************************


def getvaporpressure(p,T,qv):

  # T in K, p in hPa, qv in kg/kg.

  import numpy as np

  esat = getsaturationvaporpressure(T)
  qsat = getqvsat(p,T)
  RH = qv/qsat
  e = esat*RH

  return e


#**************************************************************************************


def thetatoT(theta,p):

  # theta in K, p in hPa.

  p00, R, cp = 1000, 287, 1004
  return theta / ( (p00/p)**(R/cp) )


#**************************************************************************************


def Ttotheta(T,p):

  # T in K, p in hPa.

  p00, R, cp = 1000, 287, 1004
  return T * ( (p00/p)**(R/cp) )


#**************************************************************************************


def getrho(qv,T,p):

  # Input q in kg/kg, T in K, and p in hPa.

  Rd, Rv = 287, 461.5
  g = 9.81

  e = getvaporpressure(p,T,qv)

  return 100*( (p-e)/(Rd*T) + e/(Rv*T) )


#**************************************************************************************


def getsaturationdeficit(p,T,qv):

  # T in K, p in hPa, qv in kg/kg.

  import numpy as np

  qsat = getqvsat(p,T)

  return qv-qsat


#**************************************************************************************


def getqvsat(p,T):

  # T in K, p in hPa.

  import numpy as np

  esat = getsaturationvaporpressure(T)
  wsat = 0.622*esat/(p-esat)

  return wsat/(1+wsat)


#**************************************************************************************


def computeCRH(p,qv,T):
 
  import numpy as np

  # p in hPa, T in K, qv in kg/kg

  g = 9.81
  qsat = getqvsat(p,T)
  dP = np.gradient(p,axis=0)

  return np.nansum(qv*dP/g,axis=0)/np.nansum(qsat*dP/g,axis=0)


#**************************************************************************************


def getthetae(qv,T,p):

  from numpy import exp

  # Input q in kg/kg, T in K, and p in hPa.

  w = q2w(qv)
  e = getvaporpressure(p,T,qv)
  pd = p-e
  rh = getRH(p/100,T,qv)
  cp, Rd, Rv, Lv = 1004, 287, 461, 2.5e6

  return T*(100000/pd)**(Rd/cp)*rh**(-w*Rv/cp)*exp(Lv*w/(cp*T))

  
#**************************************************************************************


def dewpointtoRH(T,Td):

  e = getsaturationvaporpressure(T)
  ed = getsaturationvaporpressure(Td)

  return ed/e


#**************************************************************************************


def RHtodewpoint(T,RH):

  # T in K.
  # Returns: Dewpoint in K.

  import numpy as np 

  e = getsaturationvaporpressure(T)
  ed = e*RH

  Tc = T-273.15
  Tdc = np.empty_like(ed)
  A = np.log(ed/6.108)

  Tdc[Tc>0] = 237.3*A[Tc>0]/(17.27-A[Tc>0])
  Tdc[Tc<=0] = 265.5*A[Tc<=0]/(21.875-A[Tc<=0])

  return Tdc+273.15
  

#**************************************************************************************


def dewpointtoqv(Td,T,p):

  # Td in K, T in K, p in hPa.
  # Returns qv in kg/kg.

  RH = dewpointtoRH(T,Td)

  return RHtoqv(T,RH,p)


#**************************************************************************************


def qvtodewpoint(qv,T,p):

  # qv in kg/kg, T in K, p in hPa.
  
  RH = getRH(qv,T,p) 

  return RHtodewpoint(T,RH)


#**************************************************************************************
