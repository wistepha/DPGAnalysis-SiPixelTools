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
                     
        self.sourceDir = args.SOURCEDIR
        self.sourceSite = args.SOURCESITE
        self.destDir = args.DESTDIR
        self.destSite = args.DESTSITE

        #magic strings related to site (initialisation here)
        self.remoteDir = 'unknown'
        self.copyStr = 'unknown'
        self.rmStr = 'unknown'
        self.mkdirStr = 'unknown'
        self.lsStr = 'unknown'
        self.submitCall = 'unknown'
        # self.incopystr = 'unknown'
        # self.outcopystr = 'unknown'
        self.prefix = ''
        self.fileAccessStr = 'unknown'
        self.xrootStr = 'unknown'
        self.SxrootStr = 'unknown'
        self.DxrootStr = 'unknown'
        
        if self.siteName == "T3":
            self.copyStr = "gfal-copy"
            self.rmStr = "gfal-rm"
            self.mkdirStr = "srmmkdir"
            self.lsStr = "gfal-ls"
            self.remoteDir = "/scratch/"+os.environ['USER']
            self.prefix = 'file:////'
            self.submitCall = "qsub OPTIONS -q all.q -j y -N NAME -o LOG FILE"
            self.fileAccessStr = "dcap://t3se01.psi.ch:22125/pnfs"
            self.xrootStr = "root://t3se01.psi.ch//"
        if self.sourceSite == "T3":
            self.SxrootStr = "root://t3se01.psi.ch//"
        if self.sourceSite == "T3":
            self.DxrootStr = "root://t3se01.psi.ch//"
      
        if self.siteName == "lxplusEOS":
            self.copyStr = "put lxplus copy string here"

            self.fileAccessStr = "root://eoscms//eos/cms/store"
            
            self.xrootStr = "root://eoscms.cern.ch//eos/cms/"
        if self.sourceSite == "lxplusEOS":
            self.SxrootStr = "root://eoscms.cern.ch//eos/cms/"
        if self.destSite == "lxplusEOS":
            self.DxrootStr = "root://eoscms.cern.ch//eos/cms/"

    def printInfo(self):
        print "Site Information:"
        print "  site:          ",self.siteName
        print "  indir:         ",self.indir
        print "  outdir:        ",self.outdir
        print "  sourcedir:     ",self.sourceDir
        print "  destdir:       ",self.destDir
        print "  copy string:   ",self.copyStr
        print "  prefix:        ",self.prefix
        print "  remove string: ",self.rmStr
        print "  mkdir string:  ",self.mkdirStr
        print "  ls string:     ",self.lsStr
        print "  remote dir:    ",self.remoteDir
        print

    def create_config(self):
        f = open("config","w+")
        f.write("run = {}\n".format(self.runNumber))
        f.write("indir = {}\n".format(self.indir))
        f.write("outdir = {}\n".format(self.outdir))
        f.write("site = {}\n".format(self.siteName))
        f.write("source = {}\n".format(self.sourceDir))
        f.write("sourceSite = {}\n".format(self.sourceSite))
        f.write("dest = {}\n".format(self.destDir))
        f.write("destSite = {}\n".format(self.destSite))
        f.write("\nCreated on: "+subprocess.check_output(["date"]))

    def copyFromSource(self):
        sourceDir = self.sourceDir
        sourceDir = re.sub(r".*store","store",sourceDir)
        #print sourceDir
        indir = self.indir
        indir = re.sub(r".*store","store",indir)
        #print indir
        
        for i in range(40):
            fileName = "GainCalibration_"+str(i)+"_"+self.runNumber+".dmp"
            print "Copying: ",fileName
            command = "xrdcp -f "+self.SxrootStr+sourceDir+"/"+fileName+" "+self.xrootStr+indir+"/."
            #print "copy command: ",command
            #print "splitted: ",command.split()
            subprocess.call(command.split())

    def copyToDest(self):
        outdir = self.outdir
        outdir = re.sub(r".*store","store",outdir)
        #print outdir
        destDir = self.destDir
        destDir = re.sub(r".*store","store",destDir)
        #print destDir
        fileList = self.outdir.split()
        
        for i in fileList:
            print "Copying: ",i
            command = "xrdcp -f "+self.xrootStr+outdir+"/"+i+" "+self.DxrootStr+destDir+"/."
            #print "copy command: ",command
            #print "splitted: ",command.split()
            subprocess.call(command.split())

    def clean_outDir(self):
        print "Recreating output directory."
        dirString = "-r"
        DEVNULL = open(os.devnull, 'r+b', 0)
        subprocess.call([self.rmStr,dirString,self.outdir],stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
        DEVNULL.close()
        if subprocess.call([self.mkdirStr,self.outdir]):
            raise RunError("Failed to create outdir.")

