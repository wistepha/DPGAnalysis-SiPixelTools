import Run,argparse,os,subprocess,shutil,fileinput,re
from siteclass import *

# global_supportedsitesonT3 = ['T3']
# global_supportedsitesonLXPLUS = ['CASTOR','EOS']
# global_sitekeys = [['srm','T3'],['eos','EOS']]


def argparsing():
    parser = argparse.ArgumentParser()
    parser._actions[0].help='Show this help message and exit. Use this command after the argument to see its particular usage.'
    parser.add_argument("RUNNUMBER", help="Specifies the run number.")

    subparsers = parser.add_subparsers(dest="COMMAND")#dest="INDIR"
    parser_create = subparsers.add_parser("create", help="Creates a running-directory and prepares the files to submit.")
    parser_create.add_argument("ON_SITE", default='unknown', help="The site you are working on.")

    parser_create.add_argument("--source", dest="SOURCEDIR", default=None, help="The location from where the files shall be copied into the INDIR.")
    parser_create.add_argument("--sourceSite", dest="SOURCESITE", default=None, help="The site of the source.")

    parser_create.add_argument("--dest", dest="DESTDIR", default=None, help="The location to where the files shall be copied from the OUTDIR.")
    parser_create.add_argument("--destSite", dest="DESTSITE", default=None, help="The site of the destination.")
    
    parser_create.add_argument("INDIR", default='unknown', help="Path to the input files.")
    parser_create.add_argument("OUTDIR", default='unknown', help="Path to the output files.")

    parser_submit = subparsers.add_parser("submit", help="Submits the (batch) jobs previously prepared using the 'create' command.")
    #parser_submit.add_argument(

    parser_summary = subparsers.add_parser("summary", help="Creates the summary pdf and the related content.")

    parser_summary = subparsers.add_parser("hadd", help="Merges the output files to GainCalibration.root")

    parser_payload = subparsers.add_parser("payload", help="Creates the payload.")   
    parser_payload.add_argument("YEAR", help="The year the calibration was performed in.")
    parser_payload.add_argument("VERSION", help="The version (in the current year) of the calibration.")
    
    parser_submission = subparsers.add_parser("submission", help="Creates a full submission combining the create and submit command.") 

    # parser.add_argument("--indir", 
    #                   action="store", dest="INDIR", default="",
    #                   help="Specifies the directory containing the data used as input.")
    # parser.add_argument("--outdir", 
    #                   action="store", dest="OUTDIR", default="",
    #                   help="Specifies the directory to store the output data in.")
    # parser.add_argument("--run", 
    #                   action="store", dest="RUN", default="",
    #                   help="Specifies the run number. ")

    args = parser.parse_args()

    if args.COMMAND == "create":
        if len([x for x in (args.SOURCEDIR,args.SOURCESITE) if x is not None]) == 1:
            parser.error('--source and --sourceSite must be given together.')
        if len([x for x in (args.DESTDIR,args.DESTSITE) if x is not None]) == 1:
            parser.error('--dest and --destSite must be given together.')
        
    return args

#def set_commands(args):
    # global global_sitekeys
    # for entry in global_sitekeys:
    #     if args.INDIR.find(entry[0]) != -1:
    #         print args.INDIR.find(entry[0])
    #         print "found site: ",entry[1]    
    

    # wc = subprocess.check_output('uname -a | grep t3 | wc -l', shell=True)
    # #print wc
    # if wc == '1\n':
    #    print "yes"
    # #subprocess.call(["uname","-a","|","grep" "t3","|","wc","-l"])

def readFromConfig(RUNNUMBER):
    try:
        f = open("Run_{}/config".format(RUNNUMBER))
    except:
        raise RunError("Could not open config file.")
    runNumber = ''
    indir = ''
    outdir = ''
    siteName = ''
    sourceDir = ''
    sourceSite = ''
    destDir = ''
    destSite = ''
    for line in f:
        if "run" in line:
            runNumber = line.split()[2]
        elif "indir" in line:
            indir = line.split()[2]
        elif "outdir" in line:
            outdir = line.split()[2]
        elif "site" in line:
            siteName = line.split()[2]
        elif "source" in line:
            sourceDir = line.split()[2]
        elif "sourceSite" in line:
            sourceSite = line.split()[2]
        elif "dest" in line:
            destDir = line.split()[2]
        elif "destSite" in line:
            destSite = line.split()[2]
    try:
        args = siteHelper(RUNNUMBER = runNumber, ON_SITE = siteName, INDIR = indir, OUTDIR = outdir, SOURCEDIR = sourceDir, SOURCESITE = sourceSite, DESTDIR = destDir, DESTSITE = destSite)
        currentSite = site(args)
    except UnboundLocalError:
        raise RunError("Could not find all variables in the config.")
    return currentSite

def createJobFiles(currentSite):
    #assumes to be in the run dir
    #creates the python config and the submission file if the 
    #necessary input file is present

    #DEVNULL allows to eliminate subprocess output
    DEVNULL = open(os.devnull, 'r+b', 0) 
    for fileNumber in range(40): #40 FEDs
        dmpFileName = "GainCalibration_"+str(fileNumber)+"_"+str(currentSite.runNumber)+".dmp"
        if subprocess.call([currentSite.lsStr,currentSite.indir+"/"+dmpFileName],stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL):
            raise RunError("Could not find file "+dmpFileName+" in "+currentSite.indir+"!")
        else:
            #python cfg
            configFileName = "gain_calib_"+str(fileNumber)+"_cfg.py"
            shutil.copy('../gain_calib_template_cfg.py',configFileName)
            f = fileinput.input(configFileName,inplace=1)
            for line in f:
                line = line.replace('FILENAME',dmpFileName)
                line = line.rstrip("\n")
                print line
            f.close()

            #submission file
            currentDir = subprocess.check_output(["pwd"])
            currentDir = currentDir.rstrip("\n")
            subFileName = "submit_"+str(fileNumber)+".sh"
            shutil.copy('../submit_template.sh',subFileName)
            f = fileinput.input(subFileName,inplace=1)
            for line in f:
                line = line.replace('CFGDIR',currentDir)
                line = line.replace('INDIR',currentSite.indir)
                line = line.replace('OUTDIR',currentSite.outdir)
                line = line.replace('REMOTEDIR',currentSite.remoteDir)
                line = line.replace('COPYSTRING',currentSite.copyStr)
                line = line.replace('NUM',str(fileNumber))
                line = line.replace('PREFIX',currentSite.prefix)
                line = line.replace('RUN',currentSite.runNumber)
                line = line.rstrip("\n")
                print line
            f.close()
    DEVNULL.close()

def recreateDir(path):
    #recreates the irectory and returns its name
    print "\nRecreating directory: ",path,
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)
        os.makedirs(path)
    print " Done."
    return path

def clean_RunDir():
    print "Removing the JOB folders."
    for i in range(40):
        dirName = "JOB_"+str(i)
        if os.path.isdir(dirName):
            shutil.rmtree(dirName)

def hadd(currentSite):
    command = "hadd GainCalibration.root"
    path = currentSite.outdir
    path = re.sub(r".*{}".format(currentSite.fileAccessStr.split("/")[-1]),currentSite.fileAccessStr,path)
    print path
    DEVNULL = open(os.devnull, 'r+b', 0) 
    for i in range(40):
        checkFile = currentSite.lsStr+" "+currentSite.outdir+" {}/{}.root".format(path,i)
        if not subprocess.call(checkFile.split(),stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL):
            command += " {}/{}.root".format(path,i)
        else:
            raise RunError("File {}.root is missing.".format(i))
    DEVNULL.close()
    subprocess.call(command.split())


def enterDir(dirName):
    currentDir = subprocess.check_output(["pwd"])
    #The validity of runDir is guaranted by reading the config file in it during the initialisation of currentSite
    if dirName not in currentDir:
        try:
            os.chdir(dirName)
        except OSError:
            raise RunError("Could not enter folder: "+dirName)
    else:
        if subprocess.check_output("pwd").split("/")[-1] != dirName:
            os.chdir("..")
            enterDir(dirName)

    
def create(currentSite):
    print "Preparing the submission with the following parameters:"
    print "run number:        ",currentSite.runNumber
    print "input directory:   ",currentSite.indir
    print "output directory:  ",currentSite.outdir
    if currentSite.sourceDir != None and currentSite.sourceSite != None:
        print "source directory:  ",currentSite.sourceDir
        print "source site:       ",currentSite.sourceSite
    if currentSite.destDir != None and currentSite.destSite != None:
        print "dest. directory:   ",currentSite.destDir
        print "dest. site:        ",currentSite.destSite
    print "\n"
    
    if currentSite.sourceDir != None:
        currentSite.copyFromSource()
        
    #recreating the run directory and switch to it
    os.chdir(recreateDir("./Run_{}".format(currentSite.runNumber)))
    
    #create the "config" file
    currentSite.create_config()
    
    #creating the python config files
    createJobFiles(currentSite)
    

def submit(currentSite):
    
    print "Submitting the GainCalibration for run: ",currentSite.runNumber
    currentSite.clean_outDir()
    enterDir("Run_"+str(currentSite.runNumber))
    clean_RunDir()

    for jobNumber in range(40):
        subFileName = "submit_"+str(jobNumber)+".sh"
        jobName = "GC_"+str(currentSite.runNumber)+"_"+str(jobNumber)
        if not os.path.isfile(subFileName):
            raise RunError(subFileName+" is missing.")
        pwdStr = subprocess.check_output("pwd")
        pwdStr = pwdStr.rstrip("\n")
        jobDir = pwdStr+"/JOB_"+str(jobNumber)
        print jobDir
        os.makedirs(jobDir)
        callString = currentSite.submitCall
        callString = callString.replace('OPTIONS','')
        callString = callString.replace('NAME',jobName)
        callString = callString.replace('LOG',jobDir+"/stdout")
        callString = callString.replace('FILE',subFileName)
        #print "Sending job {} ({})".format(jobName,subFileName)
        #print callString
        subprocess.call(callString.split())


def write_summary(currentSite):
    
    print "Writing the summary for run: ",currentSite.runNumber
    enterDir("Run_"+str(currentSite.runNumber))

    #Recreate dirs
    textDir = "TEXToutput"
    summaryDir = "Summary_Run{}".format(currentSite.runNumber)
    recreateDir("TEXToutput")
    recreateDir("Summary_Run{}".format(currentSite.runNumber))
    
    #Copy the necessary scripts from the scripts folder
    p = summaryDir+"/."
    shutil.copy("../scripts/make_ComparisonPlots.cc",p)
    shutil.copy("../scripts/TMean.cc",p)
    shutil.copy("../scripts/TMean.h",p)
    shutil.copy("../scripts/PixelNameTranslator.cc",p)
    shutil.copy("../scripts/PixelNameTranslator.hh",p)
    shutil.copy("../scripts/header.h",p)
    shutil.copy("../scripts/functions.C",p)
    shutil.copy("../scripts/containers.h",p)
    shutil.copy("../scripts/hist_declarations.C",p)
    shutil.copy("../scripts/gain_summary.txt",summaryDir+"/gain_summary.tex")

    enterDir(summaryDir)
    print "Currently in ",subprocess.check_output("pwd")

    #create histos and tex file
    pathBase = currentSite.outdir
    pathBase = re.sub(r".*{}".format(currentSite.fileAccessStr.split("/")[-1]),currentSite.fileAccessStr,pathBase)
    pathFile = pathBase+"/"+"GainCalibration.root"
    rootCMD = "root -l -b -x make_ComparisonPlots.cc+'(\""+pathFile+"\",\""+currentSite.runNumber+"\")' -q"
    print "RootCommand: ",rootCMD
    print "logfile: root.log"
    f = open("root.log","w")
    if subprocess.call(rootCMD,shell=True,stdout=f,stderr=f):
        f.close()
        raise RunError("The root job failed. Check root.log.")
    f.close()

    #using the created file: texSummary_RunXY.tex
    #to create the final tex file
    f = open("texSummary_Run"+str(currentSite.runNumber)+".tex","r")
    texSummary = f.readlines()
    f.close()
    texName = "gain_summary.tex"
    finalTexName = "gain_summary_final_run_"+str(currentSite.runNumber)+".tex"
    shutil.copy(texName,finalTexName)
    tex = fileinput.input(finalTexName,inplace=1)
    for line in tex:
        if "TOREPLACE" in line:
            line = "".join(texSummary)
        line = line.replace("RUNNUMBER",str(currentSite.runNumber))
        line = line.replace("DIFF_TO_REPLACE","0")
        line = line.rstrip("\n")
        print line
    tex.close()
    
    #creating the pdf
    #print subprocess.call("pwd")
    pdfCall = "pdflatex "+finalTexName
    f = open("latex.log","w")
    print "Creating pdf: ",pdfCall
    subprocess.call(pdfCall,shell=True,stdout=f,stderr=f)
    f.close()
    if not os.path.isfile("gain_summary_final_run_"+str(currentSite.runNumber)+".pdf"):
        raise RunError("The summary pdf is missing!")


def create_payload(currentSite,year,version,Type):

    print "Creating the ",Type," payload."
    if Type != "HLT" and Type != "offline":
        raise RunError("Invalid payload type.")

    tag = "SiPixelGainCalibration_2016_v2_"+Type
    rootFileName = "Summary_payload_Run"+currentSite.runNumber+"_"+year+"_v"+version+"_"+Type+".root"

    print "The tag: ",tag
    print "The summary root file: ", rootFileName

    enterDir("Run_{}".format(currentSite.runNumber))
    enterDir(recreateDir("payload_"+Type))
    currentDir = subprocess.check_output("pwd")

    remoteDir = str(currentSite.remoteDir)+"/gain_calib_payload_"+Type+"/"

    #the python config file
    DBcfg = "SiPixelGainCalibrationDBUploader_"+Type+".py"
    shutil.copy("../../SiPixelGainCalibrationDBUploader_template.py",DBcfg)
    f = fileinput.input(DBcfg,inplace=1)
    for line in f:
        line = line.replace('OUTPUT',remoteDir+rootFileName)
        #line = line.replace('INFILE',remoteDir+"GainCalibration.root")
        line = line.replace('INFILE','file:GainCalibration.root')
        line = line.replace('THETAG',tag)
        line = line.replace('SQLITE',remoteDir+"/"+tag+".db")
        line = line.rstrip("\n")
        print line
    f.close()

    #the submission file
    DBsub = "payload_"+Type+"_submit.sh"
    shutil.copy("../../payload_submit_template.sh",DBsub)
    f = fileinput.input(DBsub,inplace=1)
    for line in f:
        line = line.replace('CFGDIR',currentDir)
        line = line.replace('OUTDIR',currentSite.outdir)
        line = line.replace('TYPE',Type)
        line = line.replace('CFGFILE',DBcfg)
        line = line.replace('REMOTEDIR',remoteDir)
        line = line.replace('COPYSTRING',currentSite.copyStr+" -f ")
        line = line.replace('PREFIX',currentSite.prefix)
        line = line.replace('PAYLOAD',tag+".db")
        line = line.replace('ROOTFILE',rootFileName)
        line = line.rstrip("\n")
        print line
    f.close()

    #the submission command
    pwdStr = subprocess.check_output("pwd")
    pwdStr = pwdStr.rstrip("\n")
    jobName = "payload_"+Type
    callString = currentSite.submitCall
    callString = callString.replace('OPTIONS','-l h_vmem=4.5G')
    callString = callString.replace('NAME',jobName)
    callString = callString.replace('LOG',pwdStr+"/stdout")
    callString = callString.replace('FILE',DBsub)
    print "Sending the job: {} (script: {})".format(jobName,DBsub)
    #print "Sending the job with: \n",callString,"\n"
    subprocess.call(callString.split())
    print "\n"

    if currentSite.destDir != None:
        print "Copying all the files to the destination directory."
        currentSite.copyToDest()
