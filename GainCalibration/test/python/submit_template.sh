#!/bin/bash
source /afs/cern.ch/cms/cmsset_default.sh

mydir=CFGDIR
indir=INDIR
storedir=OUTDIR
startdir=REMOTEDIR/gain_calib_NUM
echo "Creating $startdir"
mkdir -p $startdir
cd $mydir

echo "Setting the environment ..."
eval `scramv1 runtime -sh`

cp gain_calib_NUM_cfg.py $startdir/
cd $startdir
echo -e "************************"
echo -e "  => ls: \n`ls`"
echo -e "************************\n\n"

echo -e "Copying file from storage to local ..."
file=GainCalibration_NUM_RUN.dmp
echo "(COPYSTRING PREFIX_REMOTE$indir/$file PREFIX_LOC$startdir/$file)"
COPYSTRING PREFIX_REMOTE$indir/$file PREFIX_LOC$startdir/$file
echo -e "************************"
echo -e "  => ls: \n`ls`"
echo -e "************************\n\n"

echo -e "\n\n Running CMSSW job:"
cmsRun gain_calib_NUM_cfg.py
cat *.log

echo "I'm at:"
echo `pwd`
echo -e "************************"
echo -e "  => ls: \n`ls`"
echo -e "************************\n\n"

echo -e "Copying output to pnfs:"
echo "(COPYSTRING PREFIX_LOC/$startdir/GainCalibration.root PREFIX_REMOTE${storedir}/NUM.root)"
COPYSTRING PREFIX_LOC$startdir/GainCalibration.root PREFIX_REMOTE${storedir}/NUM.root

echo -e "end ... \n\n\n"

cp *.log ${mydir}/JOB_NUM/
cp *.txt ${mydir}/JOB_NUM/
cd $mydir
rm -fr $startdir
