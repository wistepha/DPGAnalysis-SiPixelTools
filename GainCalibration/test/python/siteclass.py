#!/bin/env python
import subprocess,os,re

#place holder for future, more specific error handling
class RunError(Exception):
    def __init__(self, message):
        self.message = message

class siteHelper:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class site(object):
    #class containing all the information of the sites involved
    #can perform all needed operations on those sites
    def __init__(self,args):
        self.runNumber = args.RUNNUMBER
        self.siteName = args.ON_SITE
        self.indir = args.INDIR
        self.outdir = args.OUTDIR                    

        #magic strings related to site (initialisation here)
        self.remoteDir = None
        self.copyStr = None
        self.rmStr = None
        self.mkdirStr = None
        self.lsStr = None
        self.submitCall = None
        self.prefix = None
        self.fileAccessStr = None
        self.xrootStr = None
        self.haddcpStr = None
        # self.mountStr = None
        # self.umountStr = None
        # self.mountPrefix = None
        
        #mkdirStr not needed?
        if self.siteName == "T3":
            self.copyStr = "gfal-copy"
            self.rmStr = "gfal-rm"
            self.mkdirStr = "srmmkdir"
            self.lsStr = "gfal-ls"
            self.remoteDir = "/scratch/"+os.environ['USER']
            self.prefix = 'file:////'
            self.submitCall = "qsub OPTIONS -q long.q -j y -N NAME -o LOG FILE"
            self.fileAccessStr = "dcap://t3se01.psi.ch:22125/pnfs"
            self.xrootStr = "root://t3se01.psi.ch//"
            self.haddcpStr = "file:////`pwd`/GainCalibration.root "+self.outdir+"/."
            # self.mountStr = "gfalFS -s FOLDER "+self.indir
            # self.umountStr = "gfalFS_umount -z FOLDER"
            # self.mountPrefix = ''
      
        if self.siteName == "lxplusEOS":
            self.copyStr = "eos cp"
            self.rmStr = "eos rm"
            self.mkdirStr = "eos mkdir"
            self.lsStr = "eos ls"
            self.remoteDir = "/tmp/"+os.environ['USER']
            self.prefix = ''
            self.submitCall = "bsub -q cmscaf1nw -J NAME -eo LOG < FILE"
            self.fileAccessStr = "root://eoscms//eos/cms/store"            
            self.xrootStr = "root://eoscms.cern.ch//eos/cms/"
            self.haddcpStr = "GainCalibration.root root://eoscms//eos/cms/"+self.outdir+"/."
            # self.mounStr = "eos -b fuse mount FOLDER"
            # self.umountStr = "eos -b fuse umount FOLDER"
            # self.mountPrefix = "/eos/cms/"

    @classmethod
    def empty(cls):
        emptySite = siteHelper(RUNNUMBER = None, ON_SITE = None, INDIR = None, OUTDIR = None)
        return cls(emptySite)
        

    def isValid(self):
        if self.runNumber != None and self.indir != None and self.outdir != None:
            return True
        else:
            return False

    def printInfo(self):
        print "Site Information:"
        print "  site:          ",self.siteName
        print "  indir:         ",self.indir
        print "  outdir:        ",self.outdir
        print "  copy string:   ",self.copyStr
        print "  prefix:        ",self.prefix
        print "  remove string: ",self.rmStr
        print "  mkdir string:  ",self.mkdirStr
        print "  ls string:     ",self.lsStr
        print "  remote dir:    ",self.remoteDir
        print "  submission:    ",self.submitCall
        print "  file access:   ",self.fileAccessStr
        print "  xroot magic:   ",self.xrootStr
        print

    def clean_outDir(self):
        print "Recreating output directory."
        dirString = "-r"
        DEVNULL = open(os.devnull, 'r+b', 0)
        subprocess.call([self.rmStr,dirString,self.outdir],stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        DEVNULL.close()
        if subprocess.call([self.mkdirStr,self.outdir]):
            raise RunError("Failed to create outdir.")

    def resetSite(self,args):
        print "Editing the source and destination settings."
        self.siteName = args.ON_SITE
        self.indir = args.INDIR
        self.outdir = args.OUTDIR

