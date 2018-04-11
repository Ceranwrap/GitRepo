# Name: Raster Extents to Polygons
# Purpose: This script will create a polygon for each raster file extent in a directory.
# Author:   Nicole Ceranek
# Date Created: 02/03/2016
# Last Modified:    07/06/2016
# ArcGIS Version    10.1 - 10.4
# Python Version:   2.7
#------------------------------------------------------------------------------------------------
## Import modules
import arceditor
import os, arcpy, datetime, sys,time, os.path, glob, shutil, logging, platform, traceback
from arcpy import env
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

## Input parameters
rasterdir = arcpy.GetParameterAsText(0)

def main():
    InFolder = rasterdir
    #Dest=arcpy.GetParameterAsText(1)
    
    arcpy.env.workspace=InFolder
    #The raster datasets in the input workspace
    in_raster_datasets = arcpy.ListRasters()
    
    # User Desktop
    #userhome = os.path.expanduser('~')
    #desktop = userhome+"/Desktop/"
    # User output
    desktop = arcpy.GetParameterAsText(1)
    # Create output dir
    outdir = desktop+"\RasterExtents"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    # Create output gdb, fc, and fields
    gdbname = "RasterExtents"+datetime120
    outgdb = arcpy.CreateFileGDB_management (outdir,gdbname)
    arcpy.AddMessage("\tCreating output GDB "+str(outgdb))
    #print "Output GDB location and name: "+str(outgdb)
    fcout = "ExtentsOutput_"+datetime120
    arcpy.CreateFeatureclass_management (outgdb,fcout,"POLYGON")
    gdbfc = str(outgdb)+'/'+fcout
    arcpy.AddField_management (gdbfc,"RasterName","String","","",100)
    arcpy.AddField_management (gdbfc,"RasterPath","String","","",250)
    arcpy.AddField_management (gdbfc,"CompressionType","String","","",50)
    arcpy.AddField_management (gdbfc,"CellHeight","Double","38","8","")
    arcpy.AddField_management (gdbfc,"CellWidth","Double","38","8","")
    arcpy.AddField_management (gdbfc,"Format","String","","",50)
    arcpy.AddField_management (gdbfc,"BandCount","Long","","","")
    arcpy.AddField_management (gdbfc,"NoDataValue","Double","38","8","")
    arcpy.AddField_management (gdbfc,"PixelType","String","","","50")
    arcpy.AddField_management (gdbfc,"FileSize","Double","38","8","")
    arcpy.AddMessage("\tCreating polygons and populating attributes...")
    #print "Creating polygons and populating attributes..."
    cursor = arcpy.InsertCursor(gdbfc)
    point = arcpy.Point()
    array = arcpy.Array()
    corners = ["lowerLeft", "lowerRight", "upperRight", "upperLeft"]
    for Ras in in_raster_datasets:
        feat = cursor.newRow()  
        r = arcpy.Raster(Ras)
        for corner in corners:    
            point.X = getattr(r.extent, "%s" % corner).X
            point.Y = getattr(r.extent, "%s" % corner).Y
            array.add(point)
        array.add(array.getObject(0))
        polygon = arcpy.Polygon(array)
        feat.shape = polygon
        feat.setValue("RasterName", Ras)
        feat.setValue("RasterPath", InFolder)
        feat.setValue("CompressionType",r.compressionType)
        feat.setValue("CellHeight",r.meanCellHeight)
        feat.setValue("CellWidth",r.meanCellWidth)
        feat.setValue("Format",r.format)
        feat.setValue("BandCount",r.bandCount)
        feat.setValue("NoDataValue",r.noDataValue)
        feat.setValue("PixelType",r.pixelType)
        feat.setValue("FileSize",r.uncompressedSize)
        cursor.insertRow(feat)
        array.removeAll()
    del feat
    del cursor    
  
if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        import traceback
        map(arcpy.AddError, traceback.format_exc().split("\n"))
        arcpy.AddError(str(e))
exit()
