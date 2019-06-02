run600="/home/sachando/CSC766/CPU/600.perlbench_s/run/run_base_test_pintooltest-m64.0000"
run602="/home/sachando/CSC766/CPU/602.gcc_s/run/run_base_test_pintooltest-m64.0000"
run605="/home/sachando/CSC766/CPU/605.mcf_s/run/run_base_test_pintooltest-m64.0000"
run619="/home/sachando/CSC766/CPU/619.lbm_s/run/run_base_test_pintooltest-m64.0000"
run638="/home/sachando/CSC766/CPU/638.imagick_s/run/run_base_test_pintooltest-m64.0000"
run641="/home/sachando/CSC766/CPU/641.leela_s/run/run_base_test_pintooltest-m64.0000"
run644="/home/sachando/CSC766/CPU/644.nab_s/run/run_base_test_pintooltest-m64.0000"
outfunc="/home/sachando/CSC766/data/func/"
outbranch="/home/sachando/CSC766/data/branch/"
pin="/home/sachando/pin-3.7-97619-g0d0c92f4f-gcc-linux"
tool="/home/sachando/pin-3.7-97619-g0d0c92f4f-gcc-linux/source/tools/ManualExamples/obj-intel64"

source ../shrc
runcpu --config=onlybin.cfg --size=test --noreportable --tune=base --iterations=1 605.mcf_s 641.leela_s 619.lbm_s 638.imagick_s 644.nab_s 600.perlbench_s 602.gcc_s

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run600/perlbench_s_base.pintooltest-m64 $run600/mr2.pl; done

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run602/sgcc_base.pintooltest-m64 $run602/t3.c -O3 -finline-limit=24000; done

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run605/mcf_s_base.pintooltest-m64 $run605/inp.in; done

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run619/lbm_s_base.pintooltest-m64 1 temp.txt 0 1 $run619/200_200_260_ldc.of; done

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run638/imagick_s_base.pintooltest-m64 $run638/test_input.tga -rotate $((i*2)) -shear $((i*5)) -alpha off $run638/output.tga; done

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run641/leela_s_base.pintooltest-m64 $run641/test.sgf; done

for i in {1..100}; do $pin/pin -t $tool/sachando.so -o $i -p $i -- $run644/nab_s_base.pintooltest-m64 $run644/hkrdenq 5000 20; done

sed -i '50001,$ d' *

mv perlbench_s_base.pintooltest-m64_* ../../new_data/600.perlbench_s/
mv sgcc_base.pintooltest-m64_* ../../new_data/602.gcc_s/
mv nab_s_base.pintooltest-m64_* ../../new_data/644.nab_s/
mv lbm_s_base.pintooltest-m64_* ../../new_data/619.lbm_s/
mv leela_s_base.pintooltest-m64_* ../../new_data/641.leela_s/
mv imagick_s_base.pintooltest-m64_* ../../new_data/638.imagick_s/
mv mcf* ../../new_data/605.mcf_s/


