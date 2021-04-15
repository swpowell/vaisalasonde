#Author: Scott Powell, Naval Postgraduate School
#Purpose: Read in sounding files from Vaisala and calculate various quantities.
#Updated: 12 March 2021

#User must unzip .mwx file and put all .xml files into a directory before starting. The code currently assumes that the data is stored in an S3 bucket but can be modified for local access in function read.


#****************************************************************


def listfilesinbucket(bucket,prefix):

  import boto3

  s3 = boto3.client('s3')
  paginator = s3.get_paginator('list_objects_v2')
  pages = paginator.paginate(Bucket=bucket,Prefix=prefix)
  fnames = []
  for page in pages:
    for obj in page['Contents']:
      fnames.append(obj['Key'])

  return fnames


#****************************************************************


def findsoundingend():



    return I


#****************************************************************


def read(fname):

    import boto3
    import xml.etree.ElementTree as ET 
    from pandas import DataFrame

    ## The code below reads the file from S3.
    files = listfilesinbucket('onr-calico','soundings/'+fname+'/' )

    try:
        key = [i for i in files if 'SynchronizedSoundingData.xml' in i][0]                                               
    except:
        ValueError('No such file exists')

    s3 = boto3.resource('s3')
    obj = s3.Object('onr-calico',key)

    # This reads the file stored in obj. 
    body = obj.get()['Body'].read()
    
    # ***End of block for reading from S3.***

    ## If not using S3, you need to add custom code below here to access, open, and read the file. Comment about the above block for S3 access.


    
    # ***End of custom code block.
 
    ## Parse the XML file and put into pandas.

    root = ET.XML(body)
    varlist = ['Pressure','Height','Temperature','Humidity','WindEast','WindNorth','WindSpeed','WindDir','Dropping']
    columns=['Pressure','Height','Temperature','Relative Humidity','Zonal Wind','Meridional Wind','Wind Speed','Wind Direction','Dropping']
    df = DataFrame(columns=columns)

    for row in root.findall("./Row"):
      df2 = {}
      for var,col in zip(varlist,columns):
        df2[col] = [row.get(var)]
      df = df.append(DataFrame(df2),ignore_index=True)

    return df


#***************************************************************


def convert2netcdf(data):

    import netCDF4 as nc

    return 0


#****************************************************************


def execute():
    
    import thermodynamics as tm
    from numpy import array as arr
    from soundingtools import Sounding

    # Input name of lowest-level folder where XML files live on S3 or locally.
    #date = '20210310_173235'       #Enter date (yyyymmdd).
    date = '20210125'       #Enter date (yyyymmdd).

    #station = ''            #Enter sonde launch site (1, 2, 3), including underscore before station number! (Future feature, ignore for now.)

    data = read(date)
    data = data.astype('float64')

    # Exclude data when the sonde is descending.
    data = data[data['Dropping']==0]
    
    # Compute the dewpoint.
    data['Dewpoint'] = tm.RHtodewpoint(arr(data['Temperature']),0.01*arr(data['Relative Humidity'])) 

    sounding = Sounding(arr(data['Pressure']),arr(data['Temperature']),Td=arr(data['Dewpoint']),u=arr(data['Zonal Wind']),v=arr(data['Meridional Wind']))

    # Convert the data to a NetCDF file.
    convert2netcdf(data)

    # Write a sounding input into CM1.
    sounding.makeCM1sounding(arr(data['Height']),'input_sounding_'+date)

    # Plot a sounding.
    #plotsounding(arr(data['Pressure']),arr(data['Temperature']),Td=arr(data['Dewpoint']),qv=None,u=arr(data['Zonal Wind']),v=arr(data['Meridional Wind']),savename=date+'.pdf')


#****************************************************************

execute()
