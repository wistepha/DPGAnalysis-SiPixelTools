#!/bin/env python

from functions import *
from siteclass import *

if __name__ == "__main__":

    try:
        args = argparsing()
        #print "args:\n",args,"\n"
        sites = getSites(args)

        if args.COMMAND == 'create':
            #currentSite = site(args)
            print "currentSite:"
            sites['currentSite'].printInfo()
            print "sourceSite:"
            sites['sourceSite'].printInfo()
            print "destSite:"
            sites['destSite'].printInfo()

            create(sites)

        elif args.COMMAND == 'submit':
            #currentSite = readFromConfig(args.RUNNUMBER)
            submit(sites['currentSite'])
            
        elif args.COMMAND == 'resubmit':
            #currentSite = readFromConfig(args.RUNNUMBER)
            resubmit(sites['currentSite'],args.JOBID)

        elif args.COMMAND == 'hadd':
            #currentSite = readFromConfig(args.RUNNUMBER)
            hadd(sites['currentSite'])

        elif args.COMMAND == 'summary':
            #currentSite = readFromConfig(args.RUNNUMBER)
            write_summary(sites['currentSite'])

        elif args.COMMAND == 'payload':
            #currentSite = readFromConfig(args.RUNNUMBER)
            create_payload(sites,args.YEAR,args.VERSION,"offline")
            create_payload(sites,args.YEAR,args.VERSION,"HLT")

        elif args.COMMAND == 'copy':
            #currentSite = readFromConfig(args.RUNNUMBER)
            copySD(sites,args)

        else:
            raise RunError("Invalid command: {}".format(args.COMMAND))

    except RunError as e:
        print "EXCEPTION OCCURRED:"
        print "  ",e.message

