import Run,argparse,os,subprocess
from siteclass import site

global_supportedsitesonT3 = ['T3']
global_supportedsitesonLXPLUS = ['CASTOR','EOS']
global_sitekeys = [['srm','T3'],['eos','EOS']]

def argparsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("RUNNUMBER", help="Specifies the run number.")
    #parser.add_argument("command", help="Specifies the action for Run to perform.")
    subparsers = parser.add_subparsers(dest="COMMAND")#dest="INDIR"
    parser_create = subparsers.add_parser("create", help="Creates a running-directory and prepares the files to submit.")
    parser_create.add_argument("--source", dest="SOURCEDIR", help="Path to the files to be copied to INDIR.")
    parser_create.add_argument("--on_site", dest="ON_SITE", default="T3",help="Site on which the code is performed on.")
    #parser_create = subparsers.add_parser("indir")
    parser_create.add_argument("INDIR", help="Path to the input files.")
    #parser_create = subparsers.add_parser("outdir")
    parser_create.add_argument("OUTDIR", help="Path to the output files.")

    parser_submit = subparsers.add_parser("submit", help="Submits the (batch) jobs previously prepared using the 'create' command.")
    #parser_submit.add_argument(

    parser_summary = subparsers.add_parser("summary", help="Creates the summary pdf and the related content.")

    parser_payload = subparsers.add_parser("payload", help="Creates the payload.")   
    
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

def create(args):
    print "Preparing the submission with the following parameters:"
    print "run number:        ",args.RUNNUMBER
    print "input directory:   ",args.INDIR
    print "output directory:  ",args.OUTDIR
    
    print "\nCleaning up existing directory ./Run_{} or creating it...".format(args.RUNNUMBER),
    if not os.path.exists('Run_{}'.format(args.RUNNUMBER)):
        os.makedirs('Run_{}'.format(args.RUNNUMBER))
    else:
        folder = './Run_{}'.format(args.RUNNUMBER)
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception, e:
                print e
    os.chdir('./Run_{}'.format(args.RUNNUMBER))
    print " Done."

    print "\nCreating 'config' file...",
    config = open("config",'w')
    config.write('run = {}\n'.format(args.RUNNUMBER))
    config.write('indir = {}\n'.format(args.INDIR))
    config.write('outdir = {}\n'.format(args.OUTDIR))
    config.close()
    print " Done."

    current_site = site(args)
    current_site.getName()
    current_site.cp_in_loc("0.root")

    #set_commands(args)
    #'srm://t3se01.psi.ch:8443/srm/managerv2?SFN=/pnfs/psi.ch/cms/trivcat/store/user/swiederk/GC/test'
