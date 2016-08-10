#!/bin/bash

usage(){

echo -e "usage:
copy-from-eos RUN [-source SOURCE] DESTINATION [-verbose]

SOURCE: e.g.: /store/group/dpg_tracker_pixel/comm_pixel/GainCalibrations/Run_1085\n
or root://t3se01.psi.ch//store/user/swiederk/GC/1085/GainRun_1085/GainCalibration.root
DESTINATION: e.g. /store/user/swiederk/GC/1085"
}

echo -e "This routine is massively deprecated. Use pure xrdcp instead. For example:\n
xrdcp root://eoscms.cern.ch//eos/cms/store/group/dpg_tracker_pixel/comm_pixel/swiederk/GainCalibrations/Run_1085/GainRun_1085/1.root root://t3se01.psi.ch//store/user/swiederk/GC/1085/GainRun_1085/GainCalibration.root\n
Good luck!"
exit

if [ $# -eq 0 ] ; then usage ; exit;fi
run=$1;shift;
for arg in $* ; do
  case $arg in
    -help) usage;exit; ;;
    -verbose) verbose=1 ;;
    #-source) run=$1;source=$2;dest=$3 ;;
    -source) source=$2 ; shift ; shift;;
	  *) dest=$1 ;;
  esac
done
if [ -z "$run" ] || [ -z "$dest" ]; then usage;exit;fi;
if [ -z "$source" ]; then echo -e "Assuming path = store/group/dpg_tracker_pixel/comm_pixel/GainCalibrations/Run_$1\n";
source=store/group/dpg_tracker_pixel/comm_pixel/GainCalibrations/Run_$run;fi
if [ -z "$PSI" ]; then echo "The PSI variable is not defined. Set your environment properly!";exit;fi

mkdir /scratch/$USER/eos_tmp
for i in `seq 0 39`;do
    if [ $verbose -eq 1 ]; 
	then echo "xrdcp root://eoscms.cern.ch//eos/cms/$source/GainCalibration_${i}_$run.dmp /scratch/$USER/eos_tmp/.";fi
    xrdcp root://eoscms.cern.ch//eos/cms/$source/GainCalibration_${i}_$run.dmp /scratch/$USER/eos_tmp/.
done
echo -e "ls /scratch/$USER/eos_tmp :"
ls /scratch/$USER/eos_tmp

for i in `seq 0 39`;do
    if [ $verbose -eq 1 ];
	then echo "env --unset=LD_LIBRARY_PATH gfal-copy /scratch/$USER/eos_tmp/GainCalibration_${i}_$run.dmp $PSI/$dest/.";fi
    echo -e "\n Transferring file ${i}:"
    if env --unset=LD_LIBRARY_PATH gfal-copy file:////scratch/$USER/eos_tmp/GainCalibration_${i}_$run.dmp $PSI/$dest/. ;then echo "Done.\n"; else echo "Error while transferring files from scratch to destination. Aborting... Clean up manually!";exit;fi
done

echo "Cleaning up scratch."
rm -r /scratch/$USER/eos_tmp

echo -e "nFile transfer completed."


