#!/bin/bash

## Run in Docker
# docker run -it --rm --gpus all -v ./:/inputs antibmpnn:latest /bin/bash
# cd example/
# bash /inputs/scripts/helper_scripts/run_antibmpnn.sh

## Input job information
scripts_path="/software/antibmpnn"
inputs_path="/inputs/data/pdbs/antibmpnn_structures"

## sbio-nipahgpg-055 Derivative
# pdb_file_path="${inputs_path}/sbio-nipahgpg-055_prepared/sbio-nipahgpg-055_prepared.pdb"  
# CHAINS_TO_DESIGN="H L"
# DESIGN_ONLY_POSITIONS="30 31 32 33 34 35 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 99 100 101 102 103 104 105 106 107 108 109 110 111, 162 163 164 165 166 167 168 169 170 171 172 188 189 190 191 192 193 194 227 228 229 230 231 232 233 234 235"

## sbio-nipahgpg-114 Derivative
# pdb_file_path="${inputs_path}/sbio-nipahgpg-114_prepared/sbio-nipahgpg-114_prepared.pdb"  
# CHAINS_TO_DESIGN="H L"
# DESIGN_ONLY_POSITIONS="31 32 33 34 35 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 99 100 101 102 103 104 105, 156 157 158 159 160 161 162 163 164 165 166 182 183 184 185 186 187 188 221 222 223 224 225 226 227 228"


## sbio-nipahgpg-120 Derivative
# pdb_file_path="${inputs_path}/sbio-nipahgpg-120_prepared/sbio-nipahgpg-120_prepared.pdb"  
# CHAINS_TO_DESIGN="B"
# DESIGN_ONLY_POSITIONS="31 32 33 34 35 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 99 100 101 102 103 104 105 106 107 108 109 110 111 158 159 160 161 162 163 164 165 166 167 168 184 185 186 187 188 189 190 223 224 225 226 227 228 229 230 231"

## sbio-nipahgpg-148 Derivative
pdb_file_path="${inputs_path}/sbio-nipahgpg-148_prepared/sbio-nipahgpg-148_prepared.pdb"
CHAINS_TO_DESIGN="B"
DESIGN_ONLY_POSITIONS="31 32 33 34 35 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 99 100 101 102 103 104 105 106 107 108 109 110 111 162 163 164 165 166 167 168 169 170 171 172 188 189 190 191 192 193 194 227 228 229 230 231 232 233 234 235"



## Define input and output directories
THEME=$(date +"%m%d")_"fv_design_fixed_positions"
AB_NAME=$(basename "$pdb_file_path" .pdb)
INPUT_DIR="${inputs_path}/${AB_NAME}/"
OUTPUT_DIR="${inputs_path}/${AB_NAME}/${THEME}_${AB_NAME}"

# Create an output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
fi

## Define file paths
PATH_PARSED_CHAINS="$OUTPUT_DIR/parsed_pdbs.jsonl"
PATH_ASSIGNED_CHAINS="$OUTPUT_DIR/assigned_pdbs.jsonl"
PATH_FIXED_POSITIONS="$OUTPUT_DIR/fixed_pdbs.jsonl"

## Run preprocessing scripts
echo "Preprocessing..."
python ${scripts_path}/helper_scripts/parse_multiple_chains.py --input_path=$INPUT_DIR --output_path=$PATH_PARSED_CHAINS
python ${scripts_path}/helper_scripts/assign_fixed_chains.py --input_path=$PATH_PARSED_CHAINS --output_path=$PATH_ASSIGNED_CHAINS --chain_list "$CHAINS_TO_DESIGN"
python ${scripts_path}/helper_scripts/make_fixed_positions_dict.py --input_path=$PATH_PARSED_CHAINS --output_path=$PATH_FIXED_POSITIONS --chain_list "$CHAINS_TO_DESIGN" --position_list "$DESIGN_ONLY_POSITIONS" --specify_non_fixed

echo "Running AntiBMPNN..."
python ${scripts_path}/Running_AntiBMPNN_run.py \
    --jsonl_path $PATH_PARSED_CHAINS \
    --chain_id_jsonl $PATH_ASSIGNED_CHAINS \
    --fixed_positions_jsonl $PATH_FIXED_POSITIONS \
    --out_folder $OUTPUT_DIR \
    --model_name "antibmpnn_000" \
    --num_seq_per_target 10 \
    --sampling_temp "0.4" \
    --batch_size 10 \
    --backbone_noise 0


read -r -a positions <<< "$DESIGN_ONLY_POSITIONS"
first_value=${positions[0]}
last_value=${positions[-1]}
fa_file_dir="${OUTPUT_DIR}/seqs/"
echo ${fa_file_dir}
echo ${first_value}
echo ${last_value}
python ${scripts_path}/helper_scripts/parsing_design_result.py --dir ${fa_file_dir} --start ${first_value} --end ${last_value}

echo "Completed!"