#!/bin/env python

import functions as f

#TODO: try to add default values for the parsers
if __name__ == "__main__":

    args = f.argparsing()

    print "args:\n",args
    #print "command: ",args.COMMAND

    if args.COMMAND == "create":
        f.create(args)

        
