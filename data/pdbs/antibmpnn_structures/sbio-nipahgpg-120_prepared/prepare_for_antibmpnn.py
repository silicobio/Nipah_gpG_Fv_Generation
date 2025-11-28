## PyMOL Script to prepare antibody structures for AntiBMPNN design

# load ...

## Remove residues 123-134 in B chain (GGGS linker)
remove chain B and resi 123-134

## Move residues 1-122 to chain H (heavy chain)
alter chain B and resi 1-122, chain='H'

## Move residues 135-241 to chain L (light chain)
alter chain B and resi 135-241, chain='L'


## H CDR Residues: 31-35, 50-66, 99-111
## L CDR Residues: 158-168, 184-190, 223-231