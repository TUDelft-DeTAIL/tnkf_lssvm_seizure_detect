METHOD='tnkf'
VAL='eval'
SIMS=2

for ((i=1; i<SIMS+1; i++))
do
    python nedc_eval_eeg/nedc_eval_eeg.py -o ${VAL}_output_${METHOD}/sim_$i ${VAL}_ref.list ${VAL}_hyp_${METHOD}_$i.list
done
