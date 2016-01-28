#!/bin/bash

usage(){

echo -e "usage:
copy-from-eos RUN [-source SOURCE] DESTINATION [-verbose]

SOURCE: e.g.: /store/group/dpg_tracker_pixel/comm_pixel/GainCalibrations/Run_1085
DESTINATION: e.g. /store/user/swiederk/GC/1085"
}
if [ $# -eq 0 ] ; then usage ; exit;fi
for arg in $* ; do
  case $arg in
    -help) usage;exit; ;;
    -verbose) verbose=1 ;;
    -source) run=$1;source=$2;dest=$3 ;;	  
	  *) run=$1;dest=$2 ;;
  esac
done

if [ -z "$run" ] || [ -z "$dest" ]; then usage;exit;fi
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


