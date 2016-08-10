#!/bin/env python

from functions import *
from siteclass import *

if __name__ == "__main__":

    try:
        args = argparsing()
        #print "args:\n",args,"\n"

        if args.COMMAND == 'create':
            currentSite = site(args)
            currentSite.printInfo()
            create(currentSite)

        elif args.COMMAND == 'submit':
            currentSite = readFromConfig(args.RUNNUMBER)
            submit(currentSite)

        elif args.COMMAND == 'hadd':
            currentSite = readFromConfig(args.RUNNUMBER)
            hadd(currentSite)

        elif args.COMMAND == 'summary':
            currentSite = readFromConfig(args.RUNNUMBER)
            write_summary(currentSite)

        elif args.COMMAND == 'payload':
            currentSite = readFromConfig(args.RUNNUMBER)
            create_payload(currentSite,args.YEAR,args.VERSION,"offline")
            create_payload(currentSite,args.YEAR,args.VERSION,"HLT")

        else:
            raise RunError("Invalid command: {}".format(args.COMMAND))

    except RunError as e:
        print "EXCEPTION OCCURRED:"
        print "  ",e.message

