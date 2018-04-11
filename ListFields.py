# Name: Batch List Fields
# Purpose: This script will list fields and properties of features found in a dataset.
# Author:   Ceranwrap
# Date Created: 02/12/2016
# Last Modified:    02/29/2016
# ArcGIS Version    10.1
# Python Version:   2.7
#------------------------------------------------------------------------------------------------
## Import modules
import arceditor
import os, arcpy, datetime, sys,time, os.path, logging, csv
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

# Set input and output
inputfc = arcpy.GetParameterAsText(0)
outdir = arcpy.GetParameterAsText(1)
LogFile= open(outdir+'//ListFieldsLog_'+datetime120+'.csv','w')

def log_results(message):
    arcpy.AddMessage(message)
    LogFile.write(message)
    LogFile.flush()
    return

def main():
    try:
        wk = arcpy.env.workspace = inputfc
        fcList = arcpy.ListFeatureClasses("*")
        fcList.sort()

        if not arcpy.Exists(wk):
            log_results("\n\tWarning: Connection does not exist.!\n")
        else:
            fcCnt = 0
            fldCnt = 0
            log_results ('Category,FC Name,Name,Type,Has M,Has Z,Has Spatial Index,Length,Precision,Scale,Domain\n')
            for fc in fcList:
                fcCnt += 1
                desc = arcpy.Describe(fc)
                log_results (
                    'Feature Class,'+
                    str(desc.name)+',,'+
                    str(desc.shapeType)+' '+str(desc.featureType)+','+
                    str(desc.hasM)+','+
                    str(desc.hasZ)+','+
                    str(desc.hasSpatialIndex)+'\n')
                fields = arcpy.ListFields(fc)
                fldCnt = 0
                for field in fields:
                    log_results (
                        'Field,'+
                        str(desc.name)+','+
                        str(field.name)+','+
                        str(field.type)+','+
                        ',,,'+
                        str(field.length)+','+
                        str(field.precision)+','+
                        str(field.scale)+','+
                        str(field.domain)+'\n')
                    fldCnt += 1
                #log_results ('Field Count,'+str(fldCnt)+'\n')
        LogFile.close()

    except arcpy.ExecuteError:
        log_results (arcpy.GetMessages(2))
        LogFile.close()

    except Exception as e:
        log_results (e[0])
        LogFile.close()
if __name__ == '__main__':
    main()

exit()
