#!/bin/bash

# set up
# set -euxo pipefail
set -e
program_dir=$(pwd)
re_sim="Simulation done in ([0-9]+\.[0-9]+)"
re_sim5="Simulation done in ([0-9]+\.[0-9]+).*Simulation done in ([0-9]+\.[0-9]+).*Simulation done in ([0-9]+\.[0-9]+).*Simulation done in ([0-9]+\.[0-9]+).*Simulation done in ([0-9]+\.[0-9]+).*"
re_all="All done in ([0-9]+\.[0-9]+)"
cur_branch=`git branch --show-current`

echo "------------------------------ Running Simulations ------------------------------"
echo
echo "Checking out reference implementation tag"
git checkout reference-implementation &> /dev/null

echo "--- Building reference implementation"
./compile.sh &> /dev/null

echo "--- Running DTNMQTT scenario"
cd scenario_dtnmqtt
rm -rf reports; mkdir reports
mqtt_ref_out=$(${program_dir}/one.sh -b 5 dtnmqtt_settings.txt | tee /dev/tty)

# rename so we can compare later
echo "--- Preparing reports"
cd reports
rm -rf ref; mkdir ref
mv *.txt ./ref/;

echo "--- Running Cities scenario"
cd "${program_dir}/scenario_cities"
rm -rf reports; mkdir reports
cities_ref_out=$(${program_dir}/one.sh -b 1 cities_settings.txt | tee /dev/tty)
echo "--- Preparing reports"
cd reports
rm -rf ref; mkdir ref
mv *.txt ./ref/;

# -----------------------------------------------

cd "${program_dir}"
echo "Checking out multicore branch"
git checkout multicore-clean &> /dev/null
echo "--- Building multicore implementation"
./compile.sh &> /dev/null

echo "--- Running DTNMQTT scenario"
cd scenario_dtnmqtt
mqtt_par_out=$(${program_dir}/one.sh -b 5 dtnmqtt_settings.txt | tee /dev/tty)
echo "--- Preparing reports"
cd reports
rm -rf par; mkdir par
mv *.txt ./par/;

echo "--- Running Cities scenario"
cd "${program_dir}/scenario_cities"
cities_par_out=$(${program_dir}/one.sh -b 1 cities_settings.txt | tee /dev/tty)
echo "--- Preparing reports"
cd reports
rm -rf par; mkdir par
mv *.txt ./par/;

echo
echo
echo
echo "------------------------------- Checking Speedups -------------------------------"
echo
[[ $mqtt_ref_out =~ $re_sim5 ]];
mqtt_ref_sim_time=`echo "scale=2; (${BASH_REMATCH[1]}+${BASH_REMATCH[2]}+${BASH_REMATCH[3]}+${BASH_REMATCH[4]}+${BASH_REMATCH[5]})/5" | bc -l`

[[ $mqtt_par_out =~ $re_sim5 ]];
mqtt_par_sim_time=`echo "scale=2; (${BASH_REMATCH[1]}+${BASH_REMATCH[2]}+${BASH_REMATCH[3]}+${BASH_REMATCH[4]}+${BASH_REMATCH[5]})/5" | bc -l`


[[ $mqtt_ref_out =~ $re_all ]]; mqtt_ref_all_time=${BASH_REMATCH[1]}
[[ $mqtt_par_out =~ $re_all ]]; mqtt_par_all_time=${BASH_REMATCH[1]}

[[ $cities_ref_out =~ $re_sim ]]; cities_ref_sim_time=${BASH_REMATCH[1]}
[[ $cities_ref_out =~ $re_all ]]; cities_ref_all_time=${BASH_REMATCH[1]}
[[ $cities_par_out =~ $re_sim ]]; cities_par_sim_time=${BASH_REMATCH[1]}
[[ $cities_par_out =~ $re_all ]]; cities_par_all_time=${BASH_REMATCH[1]}
mqtt_sim_speedup=`echo "scale=2; ${mqtt_ref_sim_time}/${mqtt_par_sim_time}" | bc -l`
mqtt_all_speedup=`echo "scale=2; ${mqtt_ref_all_time}/${mqtt_par_all_time}" | bc -l`
cities_sim_speedup=`echo "scale=2; ${cities_ref_sim_time}/${cities_par_sim_time}" | bc -l`
cities_all_speedup=`echo "scale=2; ${cities_ref_all_time}/${cities_par_all_time}" | bc -l`

echo   "+------------------------------------------------+"
echo   "| Scenario    | Reference | Multicore |  Speedup |"
echo   "+------------------------------------------------+"
printf "| DTNMQTT Sim | %8ss | %8ss | %7sx |\n" "${mqtt_ref_sim_time}"   "${mqtt_par_sim_time}"   "${mqtt_sim_speedup}"
printf "| DTNMQTT All | %8ss | %8ss | %7sx |\n" "${mqtt_ref_all_time}"   "${mqtt_par_all_time}"   "${mqtt_all_speedup}"
printf "| Cities Sim  | %8ss | %8ss | %7sx |\n" "${cities_ref_sim_time}" "${cities_par_sim_time}" "${cities_sim_speedup}"
printf "| Cities All  | %8ss | %8ss | %7sx |\n" "${cities_ref_all_time}" "${cities_par_all_time}" "${cities_all_speedup}"
echo   "+------------------------------------------------+"

echo
echo
echo "---------------------------- Checking Result Parity -----------------------------"
cd "${program_dir}"
if ! `diff -s scenario_dtnmqtt/reports/ref scenario_dtnmqtt/reports/par > /dev/null`;
then
    echo "ERROR: Results of DTNMQTT do not match!"
    exit 1
else
    echo "Results of DTNMQTT match!"
fi
if ! `diff -s scenario_cities/reports/ref scenario_cities/reports/par > /dev/null`;
then
    echo "ERROR: Results of Cities do not match!"
    exit 1
else
    echo "Results of Cities match!"
fi

echo "Congratulations, all tests for result correctness have passed"
echo

echo "Teleporting back to branch '${cur_branch}'"
git checkout "$cur_branch" &> /dev/null

