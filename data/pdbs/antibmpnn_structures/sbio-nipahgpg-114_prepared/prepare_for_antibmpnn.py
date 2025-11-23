## PyMOL Script to prepare antibody structures for AntiBMPNN design

# load ...

## Remove residues 117-132 in B chain (GGGS linker)
remove chain B and resi 117-132

## Move residues 1-116 to chain H (heavy chain)
alter chain B and resi 1-116, chain='H'

## Move residues 133-238 to chain L (light chain)
alter chain B and resi 133-238, chain='L'


## H CDR Residues: 31-35, 50-66, 99-105
## L CDR Residues: 156-166, 182-188, 221-228