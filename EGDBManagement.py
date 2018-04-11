#------------------------------------------------------------------------------------------------
# Name: Enterprise GDB Maintenance
# Purpose: This script will compress a list of enterprise GDBs, update statistics, and  rebuild table indexes.
# Author:   Ceranwrap
# ArcGIS Version    10.4
# Python Version:   2.7.10
# Created: 6/22/2016
#------------------------------------------------------------------------------------------------
## Import modules
import arceditor
import os, arcpy, datetime, sys,time, os.path, glob, shutil, logging, zipfile, smtplib, mimetypes, operator, collections, fnmatch, traceback
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

## Set script parameters
# Owner directory
OwnerFileDir = arcpy.GetParameterAsText(0)
AdminFileDir = arcpy.GetParameterAsText(1)
OutLog = arcpy.GetParameterAsText(3)
# Admin directory
LogFile = open(OutLog+"//GDBMgtLog_"+datetime120+".csv","w")
# Set script timer
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)
start_time = time.time()
LogFile.write("This is the enterprise GDB maintenance log.\nThe maintenance script will compress a list of enterprise GDBs\nupdate statistics and rebuild table indexes.\n\nStarting maintenance.\n")
ErrorCount = 0
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
# Rebuild indexes and analyze the states and states_lineages system tables for each EGDB connection file found in the admin directory
adminDB = os.listdir(AdminFileDir)
for DB in adminDB:
    try:
        arcpy.env.workspace = AdminFileDir+DB
        userName = arcpy.Describe(arcpy.env.workspace).connectionProperties.user
        oDataList = arcpy.ListTables('*.' + userName + '.*') + arcpy.ListFeatureClasses('*.' + userName + '.*') + arcpy.ListRasters('*.' + userName + '.*')
        for dataset in arcpy.ListDatasets('*.' + userName + '.*'):
            oDataList += arcpy.ListFeatureClasses(feature_dataset=dataset)
        LogFile.write("Tables owned by "+userName+":,"+str(oDataList)+",\n")
        print "Rebuilding indexes for "+DB+"\n"
        LogFile.write("Rebuilding indexes for,"+DB+"\n")
        arcpy.RebuildIndexes_management(arcpy.env.workspace, "NO_SYSTEM", oDataList, "ALL")
        print "Analyzing data for "+DB+"\n"
        LogFile.write("Analyzing data for,"+DB+"\n")
        arcpy.AnalyzeDatasets_management(arcpy.env.workspace, "NO_SYSTEM", oDataList, "ANALYZE_BASE", "ANALYZE_DELTA", "ANALYZE_ARCHIVE")
    except arcpy.ExecuteError:
        msgs = arcpy.GetMessages(2)
        arcpy.AddError(msgs)
        print msgs
        LogFile.write(msgs)
        ErrorCount=ErrorCount+1
    except:
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
    finally:
        pass
#Complete logging
import time
import datetime
end_time = time.time()
print "Maintenance complete.\nElapsed time: {}".format(hms_string(end_time-start_time))
LogFile.write("Maintenance complete.\nElapsed time: {}".format(hms_string(end_time-start_time)))
LogFile.close()
#Resulting Emails

if ErrorCount > 0:
    import smtplib, email,email.encoders,email.mime.text,email.mime.base
    from email.mime.text import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.Utils import COMMASPACE, formatdate
    from email import Encoders

    COMMASPACE = ', '       
    recips = ["email@domain.com","email2@domain.com"]
    server = "email.server.com"
    text = ""
    subject = "EGDB Maintenance: ERROR"
    me = "noreply@domain.com"

    ##send the email using html, allows you to add a message in the email
    html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
    html +='"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">'
    html +='<body style="font-size:12px;font-family:Arial"><p></p>'
    html += "</body><p>The EGDB maintenance script encountered an ERROR as of "+ today5+".</p>\
    <p>Please see attached log file for details.</html></p>"
    emailMsg = email.MIMEMultipart.MIMEMultipart('mixed')
    emailMsg['Subject'] = subject
    emailMsg['From'] = me
    emailMsg['To'] = COMMASPACE.join(recips)
    emailMsg.attach(email.mime.text.MIMEText(html,'html'))

    fileMsg = email.mime.base.MIMEBase('mixed','')
    ##format,enc = mimetypes.guess_type(text)
    ##main, sub = format.split('/')
    fileMsg.set_payload(file(text).read())
    email.encoders.encode_base64(fileMsg)
    ##fileMsg.add_header('Content-Disposition','attachment;filename=<log file name>.log')
    fileMsg.add_header('Content-Disposition',"attachment;filename=E:/Scripts/EGDBMaintenance/logs/EGDBmaintenance_"+datetime107+".csv")
    emailMsg.attach(fileMsg)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(me, recips, emailMsg.as_string())
    smtp.quit()
else:
    import smtplib, email,email.encoders,email.mime.text,email.mime.base
    from email.mime.text import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.Utils import COMMASPACE, formatdate
    from email import Encoders

    COMMASPACE = ', '       
    recips = ["email@domain.com","email2@domain.com"]
    server = "email.server.com"
    text = ""
    subject = "EGDB Maintenance: SUCCESS"
    me = "noreply@domain.com"

    ##send the email using html, allows you to add a message in the email
    html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
    html +='"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">'
    html +='<body style="font-size:12px;font-family:Arial"><p></p>'
    html += "</body><p>The EGDB maintenance script has completed successfully as of "+ datetime107+".</p>\
    <p>Please see attached log file for details.</html></p>"
    emailMsg = email.MIMEMultipart.MIMEMultipart('mixed')
    emailMsg['Subject'] = subject
    emailMsg['From'] = me
    emailMsg['To'] = COMMASPACE.join(recips)
    emailMsg.attach(email.mime.text.MIMEText(html,'html'))

    fileMsg = email.mime.base.MIMEBase('mixed','')
    ##format,enc = mimetypes.guess_type(text)
    ##main, sub = format.split('/')
    fileMsg.set_payload(file(text).read())
    email.encoders.encode_base64(fileMsg)
    ##fileMsg.add_header('Content-Disposition','attachment;filename=<log file name>.log')
    fileMsg.add_header('Content-Disposition',"attachment;filename=E:/Scripts/EGDBMaintenance/logs/EGDBmaintenance_"+datetime120+".csv")
    emailMsg.attach(fileMsg)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(me, recips, emailMsg.as_string())
    smtp.quit()

##End script
exit()
