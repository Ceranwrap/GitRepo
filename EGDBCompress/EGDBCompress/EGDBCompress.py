## Import modules
import os, arcpy, datetime, sys,time, os.path, glob, logging, traceback, smtplib, mimetypes, fnmatch, pydoc_data, zipfile, csv, itertools
from arcpy import env, mapping
from datetime import date, timedelta, datetime
from time import ctime
from os import listdir
from os.path import isfile, join
from nt import close

# Set date time and timer
datetime100 = time.strftime("%m%d%Y %H%M%S") #09082007 210000
datetime107 = time.strftime ("%a, %b %d, %Y") #Mon, Sep 08, 2007
datetime112 = time.strftime ("%Y%m%d") #20070908
datetimeMY = time.strftime ("%B %Y") #September 2007
datetime120 = time.strftime("%Y%m%d_%H%M%S") #20070908_210000
time108 = time.strftime("%H:%M:%S") #21:00:00
time100 = time.strftime("%I:%M %p") #9:00 PM
yesterday = str(date.today()-timedelta(days=1))
today = str(date.today())

import xml.dom.minidom as DOM

arcpy.env.overwriteOutput = True

## Set script parameters
# Owner directory
OwnerFileDir = "F:/GIS_Data/Tools/SDEConnections/Owner/"
LogFile = open("F:/GIS_Data/Tools/MCTXVSCode/EGDBCompress/ExecutionLogs/EGDBcompress_"+datetime120+".csv","w")
# Set script timer
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)
start_time = time.time()
LogFile.write("This is the enterprise GDB maintenance log.\nThe maintenance script will compress a list of enterprise GDBs.\n")
ErrorCount = 0
PythonError = []

## Begin script
# Compress EGDBs for each connection file found in the owner directory
ownerDB = os.listdir(OwnerFileDir)
for DB in ownerDB:
    try:
        arcpy.env.workspace = OwnerFileDir
        print "Disconnecting users from "+DB+"\n"
        LogFile.write("Disconnecting users from,"+DB+"\n")
        arcpy.AcceptConnections(DB, False)
        arcpy.DisconnectUser(DB, "ALL")
        print "Compressing "+DB+"\n"
        LogFile.write("Compressing,"+DB+"\n")
        arcpy.Compress_management(DB)
        print "Allowing connections to "+DB+"\n"
        LogFile.write("Allowing connections to,"+DB+"\n")
        arcpy.AcceptConnections(DB, True)
    except arcpy.ExecuteError:
        msgs = arcpy.GetMessages(2)
        arcpy.AddError(msgs)
        print msgs
        LogFile.write(msgs)
        ErrorCount=ErrorCount+1
        print "Allowing connections to "+DB+"\n"
        LogFile.write("Allowing connections to,"+DB+"\n")
        arcpy.AcceptConnections(DB, True)
    except Exception, e:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = arcpy.GetMessages(2) + "\n"
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        print(pymsg)
        LogFile.write(pymsg)
        print(msgs)
        LogFile.write(msgs)
        ErrorCount=ErrorCount+1
        print "Allowing connections to "+DB+"\n"
        LogFile.write("Allowing connections to,"+DB+"\n")
        arcpy.AcceptConnections(DB, True)
    finally:
        print "Allowing connections to "+DB+"\n"
        LogFile.write("Allowing connections to,"+DB+"\n")
        arcpy.AcceptConnections(DB, True)
        pass
#Complete logging
import time
import datetime
end_time = time.time()
print "Compress complete.\nElapsed time: {}".format(hms_string(end_time-start_time))
LogFile.write("Compress complete.\nElapsed time: {}".format(hms_string(end_time-start_time)))
LogFile.close()

##Send Email
#arcpy.AddMessage("Sending email.")
#LogFile.close()
#import win32com.client
#olMailItem = 0x0
#obj = win32com.client.Dispatch("Outlook.Application")
#newMail = obj.CreateItem(olMailItem)
#newMail.Subject = "EGDB Compress "+datetime107
#newMail.HTMLBody = """\
#<html>
#    <head></head>
#    <body><font face="Calibri">
#        <p>The production geodatabase has compressed successfully. See attached log file for details.</p>
#        <p>Thank you,</p>
#        <p>Nicole Ceranek, GISP | GIS Manager<br />
#        <strong>Montgomery County, Texas<br />
#        </strong>301 N. Thompson Street, Suite 101 | Conroe, Texas 77301<br />
#        Office 936-788-8338 | <a href="mailto:Nicole.Ceranek@mctx.org">Nicole.Ceranek@mctx.org<br />
#        </a><a href="http://gis.mctx.org/">GIS.MCTX.ORG</a></font></p>
#    </font></body>
#</html>
#"""
#newMail.To = "Nicole.Ceranek@MCTX.org"
#attachment1 = "F:/GIS_Data/Tools/MCTXVSCode/EGDBCompress/ExecutionLogs/EGDBcompress_"+datetime120+".csv"
#newMail.Attachments.Add(attachment1)
#newMail.Send()
arcpy.AddMessage("Process complete.")
exit()