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
    parser_create.add_argument("ON_SITE", default=None, help="The site you are working on.")

    parser_create.add_argument("--source", dest="SOURCEDIR", default=None, help="The location from where the files shall be copied into the INDIR. Must be set together with --sourceSite.")
    parser_create.add_argument("--sourceSite", dest="SOURCESITE", default=None, help="The site of the source. Must be set together with --source.")

    parser_create.add_argument("--dest", dest="DESTDIR", default=None, help="The location to where the files shall be copied from the OUTDIR. Must be set together with --destSite.")
    parser_create.add_argument("--destSite", dest="DESTSITE", default=None, help="The site of the destination. Must be set together with --dest.")
    
    parser_create.add_argument("INDIR", default='unknown', help="Path to the input files.")
    parser_create.add_argument("OUTDIR", default='unknown', help="Path to the output files.")

    parser_submit = subparsers.add_parser("submit", help="Submits the (batch) jobs previously prepared using the 'create' command.")

    parser_resubmit = subparsers.add_parser("resubmit", help="Resubmits jobs. Choose either a specific job to resubmit (--jobID) or resubmit all jobs whose output file cannot be found in the output directory.")
    parser_resubmit.add_argument("--jobID", "-j",dest="JOBID", default=None, help="The jobID of the job to be resubmitted.")

    parser_summary = subparsers.add_parser("summary", help="Creates the summary pdf and the related content.")

    parser_summary = subparsers.add_parser("hadd", help="Merges the output files to GainCalibration.root")

    parser_payload = subparsers.add_parser("payload", help="Creates the payload.")   
    parser_payload.add_argument("YEAR", help="The year the calibration was performed in.")
    parser_payload.add_argument("VERSION", help="The version (in the current year) of the calibration.")

    parser_copy = subparsers.add_parser("copy", help="Copies files to and from the local site. It has the power to overwrite the config (from 'create').")
    parser_copy.add_argument("--source", dest="SOURCEDIR", default=None, help="The location from where the files shall be copied into the INDIR. Must be set together with --sourceSite.")
    parser_copy.add_argument("--sourceSite", dest="SOURCESITE", default=None, help="The site of the source. Must be set together with --source.")
    parser_copy.add_argument("--dest", dest="DESTDIR", default=None, help="The location to where the files shall be copied from the OUTDIR. Must be set together with --destSite.")
    parser_copy.add_argument("--destSite", dest="DESTSITE", default=None, help="The site of the destination. Must be set together with --dest.")
    
    #parser_submission = subparsers.add_parser("submission", help="Creates a full submission combining the create and submit command.") 


    args = parser.parse_args()

    if args.COMMAND == "create" or args.COMMAND == "copy":
        if len([x for x in (args.SOURCEDIR,args.SOURCESITE) if x is not None]) == 1:
            parser.error('--source and --sourceSite must be given together.')
        if len([x for x in (args.DESTDIR,args.DESTSITE) if x is not None]) == 1:
            parser.error('--dest and --destSite must be given together.')
        
    return args

def getSites(args):
    #creates the site objects. First attempt is to create them from the 
    #input arguments in the 'create' step. 
    #Otherwise they are created with the information contained in the
    #config file
    if args.COMMAND == 'create':
        current = siteHelper(RUNNUMBER = args.RUNNUMBER, ON_SITE = args.ON_SITE, INDIR = args.INDIR, OUTDIR = args.OUTDIR)
        source = siteHelper(RUNNUMBER = args.RUNNUMBER, ON_SITE = args.SOURCESITE, INDIR = args.SOURCEDIR, OUTDIR = args.INDIR)
        dest = siteHelper(RUNNUMBER = args.RUNNUMBER, ON_SITE = args.DESTSITE, INDIR = args.OUTDIR, OUTDIR = args.DESTDIR)
        
        currentSite = site.empty()
        sourceSite = site.empty()
        destSite = site.empty()
        if args.ON_SITE != None:
            currentSite = site(current)
        if args.SOURCESITE != None:
            sourceSite = site(source)
        if args.DESTSITE != None:
            destSite = site(dest)
        sites = {'currentSite':currentSite,'sourceSite':sourceSite,'destSite':destSite}
        return sites

    else:
        return readFromConfig(args.RUNNUMBER)

def create_config(sites):
    #Creates the config file
    print "Creating the config file."
    enterDir("Run_"+sites['currentSite'].runNumber)
    f = open("config","w+")
    f.write("run = {}\n".format(sites['currentSite'].runNumber))
    f.write("indir = {}\n".format(sites['currentSite'].indir))
    f.write("outdir = {}\n".format(sites['currentSite'].outdir))
    f.write("site = {}\n".format(sites['currentSite'].siteName))
    f.write("source = {}\n".format(sites['sourceSite'].indir))
    f.write("sourceSite = {}\n".format(sites['sourceSite'].siteName))
    f.write("dest = {}\n".format(sites['destSite'].outdir))
    f.write("destSite = {}\n".format(sites['destSite'].siteName))
    f.write("\nCreated on: "+subprocess.check_output(["date"]))

def readFromConfig(RUNNUMBER):
    #Reads the necessary information to create the site objects from the config
    #file which is created during the 'create' step.
    try:
        f = open("Run_{}/config".format(RUNNUMBER))
    except:
        raise RunError("Could not open config file.")
    runNumber = None
    indir = None
    outdir = None
    siteName = None
    sourceDir = None
    sourceSiteName = None
    destDir = None
    destSiteName = None
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
            sourceSiteName = line.split()[2]
        elif "dest" in line:
            destDir = line.split()[2]
        elif "destSite" in line:
            destSiteName = line.split()[2]
    try:
        current = siteHelper(RUNNUMBER = runNumber, ON_SITE = siteName, INDIR = indir, OUTDIR = outdir)
        source = siteHelper(RUNNUMBER = runNumber, ON_SITE = sourceSiteName, INDIR = sourceDir, OUTDIR = indir)
        dest = siteHelper(RUNNUMBER = runNumber, ON_SITE = destSiteName, INDIR = outdir, OUTDIR = destDir)

        if siteName != None:
            currentSite = site(current)
        else:
            currentSite = site.empty()
        if sourceSiteName != None:
            sourceSite = site(source)
        else:
            sourceSite = site.empty()
        if destSiteName != None:
            destSite = site(dest)
        else:
            destSite = site.empty()
        sites = {'currentSite':currentSite,'sourceSite':sourceSite,'destSite':destSite}
    except UnboundLocalError:
        raise RunError("Could not find all variables in the config.")
    return sites

def createJobFiles(currentSite):
    #assumes to be in the run dir
    #creates the python config and the submission file if the 
    #necessary input file is present
    print "Creating the python config files and the job scripts."

    #DEVNULL allows to eliminate subprocess output
    DEVNULL = open(os.devnull, 'r+b', 0) 
    for fileNumber in range(40): #40 FEDs
        dmpFileName = "GainCalibration_"+str(fileNumber)+"_"+str(currentSite.runNumber)+".dmp"
        if subprocess.call([currentSite.lsStr,currentSite.indir+"/"+dmpFileName],stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL):
            print "WARNING: Could not find file "+dmpFileName+" in "+currentSite.indir+"!"
            #raise RunError("Could not find file "+dmpFileName+" in "+currentSite.indir+"!")
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
    #merges all the root files in the output directory into
    enterDir("Run_"+currentSite.runNumber)

    command = "hadd -f GainCalibration.root"
    path = currentSite.outdir
    path = re.sub(r".*{}".format(currentSite.fileAccessStr.split("/")[-1]),currentSite.fileAccessStr,path)
    DEVNULL = open(os.devnull, 'r+b', 0) 
    for i in range(40):
        checkFile = currentSite.lsStr+" "+currentSite.outdir+"/{}.root".format(i)
        if not subprocess.call(checkFile.split(),stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL):
            command += " {}/{}.root".format(path,i)
        else:
            raise RunError("File {}.root is missing.".format(i))
    DEVNULL.close()
    print command.split()
    subprocess.call(command.split())
    print (currentSite.copyStr+" "+currentSite.haddcpStr).split()
    subprocess.call((currentSite.copyStr+" -f "+currentSite.haddcpStr),shell=True)
    subprocess.call("rm GainCalibration.root",shell=True)

    # command = "hadd GainCalibration.root"
    # mount = currentSite.mountStr+" "+currentSite.mountPrefix+" "+currentSite.indir
    # mount = mount.replace('FOLDER',"MOUNT/")  
    # umount = currentSite.umountStr
    # umount = umount.replace('FOLDER',"MOUNT/")
    # subprocess.call("mkdir MOUNT",shell=True)
    # subprocess.call(mount.split())
    # enterDir(
    # enterDir("Run_"+currentSite.runNumber)
    # subprocess.call(umount.split)
    # subprocess.call("rm -r MOUNT/",shell=True)

def enterDir(dirName):
    #enters a directory
    #can go forwards as well as backwards
    currentDir = subprocess.check_output(["pwd"])
    if dirName not in currentDir:
        try:
            os.chdir(dirName)
        except OSError:
            raise RunError("Could not enter folder: "+dirName)
    else:
        if subprocess.check_output("pwd").split("/")[-1] != dirName:
            os.chdir("..")
            enterDir(dirName)

def sendJob(currentSite,jobNumber):
    #sends a job to the queue after filling the command (in site object)
    #with the needed information
    subFileName = "submit_"+str(jobNumber)+".sh"
    if not os.path.isfile(subFileName):
        raise RunError(subFileName+" is missing.")
    pwdStr = subprocess.check_output("pwd")
    pwdStr = pwdStr.rstrip("\n")
    jobDir = pwdStr+"/JOB_"+str(jobNumber)
    recreateDir(jobDir)
    jobName = "GC_"+str(currentSite.runNumber)+"_"+str(jobNumber)
    callString = currentSite.submitCall
    callString = callString.replace('OPTIONS','')
    callString = callString.replace('NAME',jobName)
    callString = callString.replace('LOG',jobDir+"/stdout")
    callString = callString.replace('FILE',subFileName)
    #print "Sending job {} ({})".format(jobName,subFileName)
    #print callString
    subprocess.call(callString.split())

def copyFromSource(currentSite,sourceSite):
    #copies the .dmp files from the source site to the input directory
    #on the working site
    #ATTENTION: The name of the .dmp files is hard coded!
    sourceDir = sourceSite.indir
    sourceDir = re.sub(r".*store","store",sourceDir)
    #print sourceDir
    indir = sourceSite.outdir
    indir = re.sub(r".*store","store",indir)
    #print indir
        
    for i in range(40):
        fileName = "GainCalibration_"+str(i)+"_"+sourceSite.runNumber+".dmp"
        print "Copying: ",fileName
        command = "xrdcp -f "+sourceSite.xrootStr+sourceDir+"/"+fileName+" "+currentSite.xrootStr+indir+"/."
        #print "copy command: ",command
        #print "splitted: ",command.split()
        subprocess.call(command.split())

def copyToDest(currentSite,destSite):
    #Copies all the files in the output directory of the working site into
    #the destination diectory.
    outdir = destSite.indir
    outdir = re.sub(r".*store","store",outdir)
    #print outdir
    destDir = destDir.outdir
    destDir = re.sub(r".*store","store",destDir)
    #print destDir
    fileList = outdir.split()
    if fileList == []:
        print "Output directory is empty."
        return
        
    for i in fileList:
        print "Copying: ",i
        command = "xrdcp -f "+currentSite.xrootStr+outdir+"/"+i+" "+destSite.xrootStr+destDir+"/."
        #print "copy command: ",command
        #print "splitted: ",command.split()
        subprocess.call(command.split())
    
def create(sites):
    #Recreates a new folder for the run.
    #Fills it with the python config and submission files.
    print "Preparing the submission with the following parameters:"
    print "run number:        ",sites['currentSite'].runNumber
    print "input directory:   ",sites['currentSite'].indir
    print "output directory:  ",sites['currentSite'].outdir
    if sites['sourceSite'] != None:
        print "source directory:  ",sites['sourceSite'].indir
        print "source site:       ",sites['sourceSite'].siteName
    if sites['destSite'] != None:
        print "dest. directory:   ",sites['destSite'].outdir
        print "dest. site:        ",sites['destSite'].siteName
    print "\n"
    
    #if sites['sourceSite'].isValid():
        #copyFromSource(sites['currentSite'],sites['sourceSite'])
        
    #recreating the run directory and switch to it
    enterDir(recreateDir("./Run_{}".format(sites['currentSite'].runNumber)))
    
    #create the "config" file
    create_config(sites)
    
    #creating the python config files
    createJobFiles(sites['currentSite'])
    

def submit(currentSite):
    #submits the jobs based on the files produces in the 'create' step
    print "Submitting the GainCalibration for run: ",currentSite.runNumber
    currentSite.clean_outDir()
    enterDir("Run_"+str(currentSite.runNumber))
    clean_RunDir()

    for jobNumber in range(40):
        sendJob(currentSite,jobNumber)

def resubmit(currentSite,jobID):
    #Resubmits the job specified by jobID or all the jobs whose output root
    #file is missing in the output directory
    print "Starting job resubmission."
    enterDir("Run_"+str(currentSite.runNumber))
    missingJob = []
    if jobID != None:
        missingJob.append(jobID)
    else:
        temp_cmd = currentSite.lsStr+" "+currentSite.outdir
        temp = subprocess.check_output(temp_cmd.split())
        for i in range(40):
            fileName = str(i)+".root"
            if fileName not in temp.split():
                missingJob.append(fileName)
    print "Rerunning the job(s):"
    for entry in missingJob:
        print entry
    print
        
    for entry in missingJob:
        jobNumber = ''
        for char in entry:
            if char.isdigit():
                jobNumber += char
        sendJob(currentSite,jobNumber)

def write_summary(currentSite):
    #Recreates the summary folders in the run folder.
    #Fills it with the analysis plots and the final pdf.
    
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


def create_payload(sites,year,version,Type):
    #Recreates the payload (offline and HLT) which is stored in the 
    #output directory. To this and a folder is recreated inside the run folder
    #and is filled with the python config and submission file.

    print "Creating the ",Type," payload."
    if Type != "HLT" and Type != "offline":
        raise RunError("Invalid payload type.")

    tag = "SiPixelGainCalibration_"+year+"_v"+version+"_"+Type
    rootFileName = "Summary_payload_Run"+sites['currentSite'].runNumber+"_"+year+"_v"+version+"_"+Type+".root"

    print "The tag: ",tag
    print "The summary root file: ", rootFileName

    enterDir("Run_{}".format(sites['currentSite'].runNumber))
    enterDir(recreateDir("payload_"+Type))
    currentDir = subprocess.check_output("pwd")
    currentDir = currentDir.rstrip("\n")

    remoteDir = str(sites['currentSite'].remoteDir)+"/gain_calib_payload_"+Type+"/"

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
        line = line.replace('OUTDIR',sites['currentSite'].outdir)
        line = line.replace('TYPE',Type)
        line = line.replace('CFGFILE',DBcfg)
        line = line.replace('REMOTEDIR',remoteDir)
        line = line.replace('COPYSTRING',sites['currentSite'].copyStr+" -f ")
        line = line.replace('PREFIX',sites['currentSite'].prefix)
        line = line.replace('PAYLOAD',tag+".db")
        line = line.replace('ROOTFILE',rootFileName)
        line = line.rstrip("\n")
        print line
    f.close()

    #the submission command
    jobName = "payload_"+Type
    callString = sites['currentSite'].submitCall
    callString = callString.replace('OPTIONS','-l h_vmem=4.5G')
    callString = callString.replace('NAME',jobName)
    callString = callString.replace('LOG',currentDir+"/stdout")
    callString = callString.replace('FILE',DBsub)
    print "Sending the job: {} (script: {})".format(jobName,DBsub)
    #print "Sending the job with: \n",callString,"\n"
    subprocess.call(callString.split())
    print "\n"

    if sites['destSite'].isValid():
        print "Not yet implemented!"
        #print "Copying all the files to the destination directory."
        #copyToDest() sites missing


def copySD(sites,args):
    #Copies files from/to the source/destination directory.
    #This method overwrites the config file. Therefore, it allows to
    #copy the files outsite the 'create' step.

    # enterDir("Run_{}".format(sites['currentSite'].runNumber))
    if args.SOURCESITE != None:
        newSource = siteHelper(RUNNUMNER = sites['currentSite'].runNumber, ON_SITE = args.SOURCESITE, INDIR = args.SOURCEDIR, OUTDIR = sites['currentSite'].indir)
        sites['sourceSite'].resetSite(newSource)
    if args.DESTSITE != None:
        newDest = siteHelper(RUNNUMNER = sites['currentSite'].runNumber, ON_SITE = args.DESTSITE, INDIR = sites['currentSite'].outdir, OUTDIR = args.DESTDIR)
        sites['destSite'].resetSite(newDest)

    create_config(sites)
    if not sites['currentSite'].isValid():
        raise("Invalid main site.")
    if sites['sourceSite'].isValid():
        copyFromSource(sites['currentSite'],sites['sourceSite'])
    if sites['destSite'].isValid():
        copyToDest(sites['currentSite'],sites['destSite'])

    

