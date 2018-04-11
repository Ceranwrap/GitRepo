# Name: Update SDE Connection Files
# Purpose: This script will update SDE connection files found in a specified folder.
# Author:   Ceranwrap
# Date Created: 02/12/2016
# Last Modified:    05/10/2016
# ArcGIS Version    10.1
# Python Version:   2.7
#------------------------------------------------------------------------------------------------
## Import modules
import arceditor
import os, arcpy, datetime, sys,time, os.path, glob, logging, traceback, shutil, csv
from arcpy import env, mapping
from datetime import date, timedelta, datetime
from time import ctime,gmtime,strftime
from os import listdir
from os.path import isfile, join

# Set date time and timer
datetime107 = time.strftime ("%a %b %d %Y")
datetime120 = time.strftime("%Y%m%d_%H%M%S")
time108 = time.strftime("%H:%M:%S")
arcpy.env.overwriteOutput = True
start = time.strftime('%X %x %Z')

class Timer:
  def __init__(self):
    self.start = time.time()

  def restart(self):
    self.start = time.time()

  def get_time_hhmmss(self):
    end = time.time()
    m, s = divmod(end - self.start, 60)
    h, m = divmod(m, 60)
    time_str = "%02d:%02d:%02d" % (h, m, s)
    return time_str

my_timer = Timer()
time_hhmmss = my_timer.get_time_hhmmss()

# Set  output directories on user desktop
#userhome = os.path.expanduser('~') #hard coded output location to write to user's desktop
#desktop = userhome+"//Desktop//" #hard coded output location to write to user's desktop
desktop = arcpy.GetParameterAsText(1) #open as parameter allowing user to select output

outdir = desktop+"//SDEConnectionFileBU//"
if not os.path.exists(outdir):
        os.makedirs(outdir)
oldsdedir = outdir+"OldConnections"
if not os.path.exists(oldsdedir):
        os.makedirs(oldsdedir)

# Create output file
LogFile = open(outdir+"/SDEConnectionsUpdate.log","w")
ConnPropDB = open(outdir+"/SDEConnectionsProperties_DB.csv","w")
ConnPropDBhist = open(outdir+"/SDEConnectionsProperties_DBhist.csv","w")
ConnPropOSA = open(outdir+"/SDEConnectionsProperties_OSA.csv","w")
ConnPropOSAhist = open(outdir+"/SDEConnectionsProperties_OSAhist.csv","w")

# Set  home directories on user desktop
#userhome = os.path.expanduser('~') #hard coded database connection folder location
#install = (arcpy.GetInstallInfo()['Version']) #hard coded database connection folder location

#esrihome = userhome+"//AppData//Roaming//ESRI//Desktop"+install+"//ArcCatalog" #hard coded database connection folder location
esrihome = arcpy.GetParameterAsText(0) #open as parameter allowing user to select connection file folder
arcpy.env.workspace = esrihome

LogFile.write('Started: '+(start)+'\n\n')
sdelist = arcpy.ListFiles("*.sde")
arcpy.AddMessage('Testing connections...')
LogFile.write('Connection test results:\n')

for sde in sdelist:
    sdefile =  esrihome+"//"+sde
    shutil.copy(sdefile,oldsdedir)
    sdedesc = arcpy.Describe(sdefile)
    boo_good = True;
    try:
        arcpy.env.workspace = sdefile;
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2));
    try:
        desc = arcpy.Describe(sdefile);
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2));
    if desc is not None   \
        and hasattr(desc,"connectionProperties"):
        cp = desc.connectionProperties;
    else:
        arcpy.AddMessage('\tWarning: Unable to connect to '+sde+'.\n\t\t This connection file will not be recreated. See script log for details.');
        LogFile.write('\tWarning: Unable to connect to '+sde+'.\n\t\t This connection file will not be recreated.\n\t\t Causes may include one or more of the following:\n\t\t 1. Database has been archived.\n\t\t 2. Database is offline.\n\t\t 3. User does not have permission to access database.\n\t\t 4. Database version does not exist.\n');
        os.remove(sdefile)
        boo_good = False;
        int_bad =+ 1;
    if boo_good:
        try:
            #Look for DBMS connections
            if cp.authentication_mode == "DBMS":
                DBlist = []
                try:
                    if cp.historical_name is not None:
                        #Look for GISAdmin connections with historical markers
                        if cp.user =="GISAdmin":
                            ConnPropDBhist.write(
                                esrihome+','
                                +str(sde)+','
                                +'SQL_SERVER'+','
                                +'GISDB\\'+(str(cp.instance)[-6:])+','
                                +'DATABASE_AUTH,'
                                +str(cp.user)+','
                                +'apdm_admin,'
                                +'SAVE_USERNAME,'
                                +str(cp.database)+','
                                +'HISTORICAL,'
                                +str(cp.historical_name)+'\n');
                            LogFile.write('\tConnection to '+sde+' is good.\n')
                            arcpy.AddMessage('\tConnection to '+sde+' is good.')
                            os.remove(sdefile)
                            pass
                        elif cp.user =="sde":
                            #Look for sde connections with historical markers
                            ConnPropDBhist.write(
                                esrihome+','
                                +str(sde)+','
                                +'SQL_SERVER,'
                                +'GISDB\\'+(str(cp.instance)[-6:])+','
                                +'DATABASE_AUTH,'
                                +str(cp.user)+','
                                +'SD30wner,'
                                +'SAVE_USERNAME,'
                                +str(cp.database)+','
                                +'HISTORICAL,'
                                +str(cp.historical_name)+'\n');
                            LogFile.write('\tConnection to '+sde+' is good.\n')
                            arcpy.AddMessage('\tConnection to '+sde+' is good.')
                            os.remove(sdefile)
                            pass
                        else:
                            #Look for all other DBMS connections with historical markers
                            ConnPropDBhist.write(
                                            esrihome+','
                                            +str(sde)+','
                                            +'SQL_SERVER,'
                                            +'GISDB\\'+(str(cp.instance)[-6:])+','
                                            +str(cp.user)+','
                                            +str(cp.user)+','
                                            +'SAVE_USERNAME,'
                                            +str(cp.database)+','
                                            +'HISTORICAL,'
                                            +str(cp.historical_name)+'\n');
                            LogFile.write('\tConnection to '+sde+' is good.\n')
                            arcpy.AddMessage('\tConnection to '+sde+' is good.')
                            os.remove(sdefile)
                            pass
                    else:
                        pass
                except:
                    pass
                try:
                    #Look for GISAdmin connections with historical times
                    if cp.historical_timestamp is not None:
                        if cp.user =="GISAdmin":
                            ConnPropDBhist.write(
                                esrihome+','
                                +str(sde)+','
                                +'SQL_SERVER'
                                +'GISDB\\'+(str(cp.instance)[-6:])+','
                                +'DATABASE_AUTH,'
                                +str(cp.user)+','
                                +'apdm_admin,'
                                +'SAVE_USERNAME,'
                                +str(cp.database)+','
                                +'POINT_IN_TIME,'
                                +str(cp.historical_timestamp)+'\n');
                            LogFile.write('\tConnection to '+sde+' is good.\n')
                            arcpy.AddMessage('\tConnection to '+sde+' is good.')
                            os.remove(sdefile)
                            pass
                        elif cp.user =="sde":
                            #Look for sde connections with historical times
                            ConnPropDBhist.write(
                                esrihome+','
                                +str(sde)+','
                                +'SQL_SERVER,'
                                +'GISDB\\'+(str(cp.instance)[-6:])+','
                                +'DATABASE_AUTH,'
                                +str(cp.user)+','
                                +'SD30wner,'
                                +'SAVE_USERNAME,'
                                +str(cp.database)+','
                                +'POINT_IN_TIME,'
                                +str(cp.historical_timestamp)+'\n');
                            LogFile.write('\tConnection to '+sde+' is good.\n')
                            arcpy.AddMessage('\tConnection to '+sde+' is good.')
                            os.remove(sdefile)
                            pass
                        else:
                            #Look for other DBMS connections with historical times
                            ConnPropDBhist.write(
                                esrihome+','
                                +str(sde)+','
                                +'SQL_SERVER'+','
                                +'GISDB\\'+(str(cp.instance)[-6:])+','
                                +'DATABASE_AUTH,'
                                +str(cp.user)+','
                                +str(cp.user)+','
                                +'SAVE_USERNAME,'
                                +str(cp.database)+','
                                +'POINT_IN_TIME,'
                                +str(cp.historical_timestamp)+'\n');
                            LogFile.write('\tConnection to '+sde+' is good.\n')
                            arcpy.AddMessage('\tConnection to '+sde+' is good.')
                            os.remove(sdefile)
                            pass
                    else:
                        pass
                except:
                    pass
                try:
                    #Look for GISAdmin connections with no historical markers or times
                    if cp.user =="GISAdmin":
                        ConnPropDB.write(
                            esrihome+','
                            +str(sde)+','
                            +'SQL_SERVER,'
                            +'GISDB\\'+(str(cp.instance)[-6:])+','
                            +'DATABASE_AUTH,'
                            +str(cp.user)+','
                            +'apdm_admin,'
                            +'SAVE_USERNAME,'
                            +str(cp.database)+','
                            +'TRANSACTIONAL,'
                            +str(cp.version)+'\n');
                        LogFile.write('\tConnection to '+sde+' is good.\n')
                        arcpy.AddMessage('\tConnection to '+sde+' is good.')
                        os.remove(sdefile)
                        pass
                    elif cp.user =="sde":
                        #Look for sde connections with no historical markers or times
                        ConnPropDB.write(
                            esrihome+','
                            +str(sde)+','
                            +'SQL_SERVER,'
                            +'GISDB\\'+(str(cp.instance)[-6:])+','
                            +'DATABASE_AUTH,'
                            +str(cp.user)+','
                            +'SD30wner,'
                            +'SAVE_USERNAME,'
                            +str(cp.database)+','
                            +'TRANSACTIONAL,'
                            +str(cp.version)+'\n');
                        LogFile.write('\tConnection to '+sde+' is good.\n')
                        arcpy.AddMessage('\tConnection to '+sde+' is good.')
                        os.remove(sdefile)
                        pass
                    else:
                        #Look for all other DBMS connections with no historical markers or times
                        ConnPropDB.write(
                            esrihome+','
                            +str(sde)+','
                            +'SQL_SERVER'+','
                            +'GISDB\\'+(str(cp.instance)[-6:])+','
                            +'DATABASE_AUTH'+','
                            +str(cp.user)+','
                            +str(cp.user)+','
                            +'SAVE_USERNAME'+','
                            +str(cp.database)+','
                            +'TRANSACTIONAL,'
                            +str(cp.version)+'\n');
                        LogFile.write('\tConnection to '+sde+' is good.\n')
                        arcpy.AddMessage('\tConnection to '+sde+' is good.')
                        os.remove(sdefile)
                        pass
                except:
                    pass
            elif cp.authentication_mode == "OSA":
                #Look for OSA connections
                OSAlist = []
                try:
                    if cp.historical_name is not None:
                        #Look for OSA connections with historical markers
                        ConnPropOSAhist.write(
                            esrihome+','
                            +str(sde)+','
                            +'SQL_SERVER'+','
                            +'GISDB\\'+(str(cp.instance)[-6:])+','
                            +'OPERATING_SYSTEM_AUTH'+','
                            +'SAVE_USERNAME'+','
                            +'#'+','
                            +'#'+','
                            +str(cp.database)+','
                            +'HISTORICAL'+','
                            +str(cp.historical_name)+'\n');
                        LogFile.write('\tConnection to '+sde+' is good.\n')
                        arcpy.AddMessage('\tConnection to '+sde+' is good.')
                        os.remove(sdefile)
                        pass
                    else:
                        pass
                except:
                    pass
                try:
                    if cp.historical_timestamp is not None:
                        #Look for OSA connections with historical time
                        ConnPropOSAhist.write(
                            esrihome+','
                            +str(sde)+','
                            +'SQL_SERVER'+','
                            +'GISDB\\'+(str(cp.instance)[-6:])+','
                            +'OPERATING_SYSTEM_AUTH'+','
                            +'SAVE_USERNAME'+','
                            +'#'+','
                            +'#'+','
                            +str(cp.database)+','
                            +'POINT_IN_TIME'+','
                            +str(cp.historical_timestamp)+'\n');
                        LogFile.write('\tConnection to '+sde+' is good.\n')
                        arcpy.AddMessage('\tConnection to '+sde+' is good.')
                        os.remove(sdefile)
                        pass
                    else:
                        pass
                except:
                    pass
                try:
                    #Look for other OSA connections with no historical markers or times
                    ConnPropOSA.write(
                        esrihome+','
                        +str(sde)+','
                        +'SQL_SERVER'+','
                        +'GISDB\\'+(str(cp.instance)[-6:])+','                        
                        +'OPERATING_SYSTEM_AUTH'+','
                        +'SAVE_USERNAME'+','
                        +'#'+','
                        +'#'+','
                        +str(cp.database)+','
                        +str(cp.version)+'\n');
                    LogFile.write('\tConnection to '+sde+' is good.\n')
                    arcpy.AddMessage('\tConnection to '+sde+' is good.')
                    os.remove(sdefile)
                    pass
                except:
                    pass
            else:
                pass
        except arcpy.ExecuteError:
            print (arcpy.GetMessages(2));

arcpy.AddMessage('\nRecreating connection files...')
LogFile.write('\nNOTE:\tAll connection files have been archived, for your reference.\n\tArchive folder: '+oldsdedir+'\n\nRecreate connection results:\n')

ConnPropDB = (outdir+'/SDEConnectionsProperties_DB.csv')
with open (ConnPropDB,'rb') as csvfile:
    rowread = csv.reader(csvfile,delimiter=',')
    for row in rowread:
        try:
            arcpy.CreateDatabaseConnection_management(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9])
            LogFile.write('\t'+row[1]+' recreated.\n')
            arcpy.AddMessage('\t'+row[1]+' recreated.')
            pass
        except arcpy.ExecuteError:
            LogFile.write('\tERROR:\t'+row[1]+'\n')
            arcpy.AddMessage('\tERROR:\t'+row[1]+'\n')
            print(arcpy.GetMessages(2))
            pass;

ConnPropOSA = (outdir+'/SDEConnectionsProperties_OSA.csv')
with open (ConnPropOSA,'rb') as csvfile:
    rowread = csv.reader(csvfile,delimiter=',')
    for row in rowread:
        try:
            arcpy.CreateDatabaseConnection_management(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8])
            LogFile.write('\t'+row[1]+' recreated.\n')
            arcpy.AddMessage('\t'+row[1]+' recreated.')
            pass
        except arcpy.ExecuteError:
            LogFile.write('\tERROR:\t'+row[1]+'\n')
            arcpy.AddMessage('\tERROR:\t'+row[1]+'\n')
            print(arcpy.GetMessages(2))
            pass;
#arcpy.AddMessage('\nNOTE:\tConnections have been created and point to the DEFAULT version.\n\tRefer to CSV files for old connection information.\n')
LogFile.write('\nNOTE:\tConnections have been created and point to the DEFAULT version.\n\tRefer to CSV files for historical marker, timestamp, or child version settings.\n\tCSV folder:\t\t\t'+outdir+'\n')
arcpy.AddMessage('Warning: Connection files connect to the DEFAULT version. Check output log for details.\n\nNOTE: The SDEConnectionFileBU output folder and contents can be found: '+outdir+'\n')

ConnPropDBhist.close()
ConnPropOSAhist.close()

# Get time:
end = time.strftime('%X %x %Z')
#arcpy.AddMessage('\nCompleted: '+(end)+'\n')
LogFile.write('\nCompleted: '+(end)+'\n')
time_hhmmss = my_timer.get_time_hhmmss()
#arcpy.AddMessage('Time elapsed: %s' % time_hhmmss)
LogFile.write('Time elapsed: %s' % time_hhmmss)
LogFile.close()
exit()
