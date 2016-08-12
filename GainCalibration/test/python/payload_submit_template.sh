#!/bin/bash
source /afs/cern.ch/cms/cmsset_default.sh

mydir=CFGDIR
storedir=OUTDIR
startdir=REMOTEDIR
echo "Creating $startdir"
mkdir -p $startdir
cd $mydir

echo "Setting the environment ..."
eval `scramv1 runtime -sh`

cp CFGFILE $startdir/
cd $startdir
echo `pwd`
echo -e "************************"
echo -e "  => ls: \n`ls`"
echo -e "************************\n\n"

echo -e "Copying file from storage to local ..."
file=GainCalibration.root
echo "(COPYSTRING $storedir/$file PREFIX$startdir/$file)"
COPYSTRING PREFIX_REMOTE$storedir/$file PREFIX_LOC$startdir/$file
echo `pwd`
echo -e "************************"
echo -e "  => ls: \n`ls`"
echo -e "************************\n\n"

echo -e "\n\n Running CMSSW job:"
cmsRun CFGFILE
cat *.log

echo "Current position:"
echo `pwd`
echo -e "************************"
echo -e "  => ls: \n`ls`"
echo -e "************************\n\n"

echo -e "Copying output to pnfs:"
echo "(COPYSTRING PREFIX_LOC/$startdir/PAYLOAD PREFIX_REMOTE${storedir}/PAYLOAD)"
COPYSTRING PREFIX_LOC/$startdir/PAYLOAD PREFIX_REMOTE${storedir}/PAYLOAD
echo "(COPYSTRING PREFIX_LOC/$startdir/ROOTFILE PREFIX_REMOTE${storedir}/ROOTFILE)"
COPYSTRING PREFIX_LOC/$startdir/ROOTFILE PREFIX_REMOTE${storedir}/ROOTFILE
echo -e "end ... \n\n\n"

cp *.log ${mydir}/payload/
cp *.txt ${mydir}/payload/
cd $mydir
rm -fr $startdir
