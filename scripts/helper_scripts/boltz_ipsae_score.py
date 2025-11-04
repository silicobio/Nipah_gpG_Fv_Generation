#!/usr/bin/env python3
"""
boltz_ipsae_score.py
Compute an overall 'ipsae' structural confidence score
from Boltz-2 output files (PAE, PDE, pLDDT, and CIF).
"""

import os
import sys
import numpy as np

def load_npz(path, key=None):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    data = np.load(path, allow_pickle=True)
    if key and key in data:
        return np.array(data[key])
    # otherwise use the first array
    first_key = list(data.keys())[0]
    return np.array(data[first_key])

def parse_plddt_from_cif(cif_path):
    """Extract per-residue pLDDT values from a Boltz-2 CIF if no npz is given."""
    vals = []
    try:
        with open(cif_path) as f:
            for line in f:
                if "ma_qa_metric_local" in line.lower() and re.match(r"^\\d+", line.strip()):
                    parts = line.split()
                    if len(parts) >= 7:
                        vals.append(float(parts[6]))
    except Exception:
        pass
    return np.array(vals)

def compute_ipsae(pae, pde, plddt):
    """
    Combine confidence metrics into a single IPSAE-style score.
    """
    ## Normalize everything roughly 0–1
    pae_score = 1.0 - np.clip(np.mean(pae) / 30.0, 0, 1)
    pde_score = 1.0 - np.clip(np.mean(pde) / 30.0, 0, 1)
    plddt_score = np.mean(plddt) / 100.0

    ipsae = (pae_score * 0.4) + (pde_score * 0.3) + (plddt_score * 0.3)
    return ipsae, pae_score, pde_score, plddt_score

def main():
    if len(sys.argv) < 3:
        print("Usage: python boltz_ipsae_score.py <base_dir> <stem_base>")
        print("Example: python boltz_ipsae_score.py structures/my_structure_001 my_structure_001_model_0")
        sys.exit(1)

    # stem = sys.argv[1]
    # base_dir = os.path.dirname(stem)
    # stem_base = os.path.basename(stem)

    base_dir = sys.argv[1]
    stem_base = sys.argv[2]

    pae_path = os.path.join(base_dir, f"pae_{stem_base}.npz")
    pde_path = os.path.join(base_dir, f"pde_{stem_base}.npz")
    plddt_path = os.path.join(base_dir, f"plddt_{stem_base}.npz")
    cif_path = os.path.join(base_dir, f"{stem_base}.cif")

    ## Load arrays
    pae = load_npz(pae_path)
    pde = load_npz(pde_path)
    if os.path.exists(plddt_path):
        plddt = load_npz(plddt_path)
    else:
        print("No pLDDT NPZ found, attempting to parse from CIF...")
        plddt = parse_plddt_from_cif(cif_path)

    ipsae, pae_s, pde_s, plddt_s = compute_ipsae(pae, pde, plddt)

    output_dict = {
        "average_pae": np.mean(pae),
        "average_pde": np.mean(pde),
        "average_plddt": np.mean(plddt),
        "ipsae_score": ipsae,
        "pae_score": pae_s,
        "pde_score": pde_s,
        "plddt_score": plddt_s
    }

    # print("\n=== Boltz-2 IPSAE Summary ===")
    # print(f"Average pLDDT: {np.mean(plddt):.2f}")
    # print(f"Average PAE:   {np.mean(pae):.2f} Å")
    # print(f"Average PDE:   {np.mean(pde):.2f} Å")
    # print(f"PAE score:     {pae_s:.3f}")
    # print(f"PDE score:     {pde_s:.3f}")
    # print(f"pLDDT score:   {plddt_s:.3f}")
    # print(f"\n> Overall IPSAE score: {ipsae:.3f}\n")

    print(output_dict)

if __name__ == "__main__":
    main()
