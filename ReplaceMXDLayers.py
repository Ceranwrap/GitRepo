# Name: Replace layers in MXD TOC
# Purpose: This script will copy all MXDs within the specified directory to a folder on your desktop.
#               Then it will scan each MXD in that desktop folder, looking for a layer name, per user input, 
#               and replace with an existing layer file, per user input.
# Author:   Ceranwrap
# Date Created: 02/11/2016
# Last Modified:    -
# ArcGIS Version    10.1
# Python Version:   2.7
#------------------------------------------------------------------------------------------------
## Import modules
import arceditor
import os, arcpy, datetime, sys,time, os.path, glob, logging, traceback
from arcpy import env, mapping
from datetime import date, timedelta, datetime
from time import ctime
from os import listdir
from os.path import isfile, join

## Set global variables
date101 = time.strftime("%m/%d/%Y")
date112 = time.strftime("%Y%m%d")
date1 = time.strftime("%m/%d/%y")	
datetime100 = time.strftime ("%b %d %Y %I:%M%p")
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

# Input
indir = arcpy.GetParameterAsText(0)
oldlyrname = arcpy.GetParameterAsText(1)
lyrfile = arcpy.GetParameterAsText(2)
newlyr = arcpy.mapping.Layer(lyrfile)
userout = arcpy.GetParameterAsText(3)

# Create output directories on user desktop
#userhome = os.path.expanduser('~')
#desktop = userhome+"/Desktop/"

outdir = userout+"/MXDcopy"
if not os.path.exists(outdir):
        os.makedirs(outdir)

removedir = outdir+"/MXDsWithReplacement"
if not os.path.exists(removedir):
        os.makedirs(removedir)
# Create output log file
LogFile = open(outdir+"/LayerReplacementLog_"+datetime120+".csv","w")

# Remove old layer from MXDs and save copy to removeddir
try:
    workspace = indir
    arcpy.env.workspace = workspace
    mxdList = arcpy.ListFiles("*.mxd")
    LogFile.write("Process,MXD,From-Old,To-New\n")
    for mapdoc in mxdList:
        filepath = os.path.join(workspace,mapdoc)
        mxd = arcpy.mapping.MapDocument(filepath)
        filename = mapdoc
        output = os.path.join(outdir,filename)
        arcpy.AddMessage("Copying MXD "+mapdoc)
        LogFile.write("Copying,"+mapdoc+","+indir+","+outdir+"\n")
        mxd.saveACopy(output)
        pass
except Exception, e:
  import traceback
  map(arcpy.AddError, traceback.format_exc().split("\n"))
  arcpy.AddError(str(e))

# Add new layer from MXDs and save copy to replaceddir
arcpy.env.overwriteOutput = True
try:
    workspace = outdir
    arcpy.env.workspace = workspace
    mxdList = arcpy.ListFiles("*.mxd")
    for mapdoc in mxdList:
        filepath = os.path.join(workspace,mapdoc)
        arcpy.AddMessage("Updating file: "+mapdoc)
        mxd = arcpy.mapping.MapDocument(filepath)
        filename = mapdoc
        output = os.path.join(removedir,filename)
        for df in arcpy.mapping.ListDataFrames(mxd):
            for lyr in arcpy.mapping.ListLayers(mxd,"",df):
                if lyr.name==oldlyrname:
                    arcpy.AddMessage("Replacing: "+str(lyr)+" with: "+str(newlyr))
                    LogFile.write("Replacing Layer,"+str(mapdoc)+","+str(lyr.name)+","+str(newlyr)+"\n")
                    arcpy.mapping.InsertLayer(df,lyr,newlyr,"BEFORE")
                    arcpy.mapping.RemoveLayer(df,lyr)
                    arcpy.RefreshActiveView()
                    arcpy.RefreshTOC()
                    mxd.saveACopy(output)
                else:
                    LogFile.write("Ignoring,"+mapdoc+","+str(lyr.name)+"\n")
                    pass
except Exception, e:
  import traceback
  map(arcpy.AddError, traceback.format_exc().split("\n"))
  arcpy.AddError(str(e))

# Get time:
end = time.strftime('%X %x %Z')
#arcpy.AddMessage('\nCompleted: '+(end)+'\n')
LogFile.write('\nCompleted: '+(end)+'\n')
time_hhmmss = my_timer.get_time_hhmmss()
#arcpy.AddMessage('Time elapsed: %s' % time_hhmmss)
LogFile.write('Time elapsed: %s' % time_hhmmss)
LogFile.close()
exit()
