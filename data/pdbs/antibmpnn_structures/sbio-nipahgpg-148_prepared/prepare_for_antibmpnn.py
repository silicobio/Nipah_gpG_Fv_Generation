## PyMOL Script to prepare antibody structures for AntiBMPNN design

# load ...

## Remove residues 123-138 in B chain (GGGS linker)
remove chain B and resi 123-138

## Move residues 1-122 to chain H (heavy chain)
# alter chain B and resi 1-122, chain='H'

## Move residues 138-245 to chain L (light chain)
# alter chain B and resi 138-245, chain='L'


## H CDR Residues: 31-35, 50-66, 99-111
## L CDR Residues: 162-172, 188-194, 227-235