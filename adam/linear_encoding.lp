%%%%%%%%%%%%
% helpers, everything static

% overall cube size, aka number of voxels/ virtual servers
cube_size(0,S) :- dim(0,S).
cube_size(D,SS*S) :- cube_size(D-1,SS), dim(D,S).
cube_size(CS) :- cube_size(n-1,CS).

% virtual server, aka voxel
virt(V) :- V = 0..CS-1, cube_size(CS).

% create voxels
vox_tmp(0,1).
vox_tmp(D,B*BB) :- vox_tmp(D-1,B), dim(D-1,BB), D != 0.
voxel(V,D,C) :- C = (V \ BB) / B, vox_tmp(D,B), vox_tmp(D+1,BB), virt(V).

% physical servers
phys(0..p-1).

% relations
rel(R) :- rel(R,_,_).

% numbers of dimensions for relations
num_dims(R,N) :- rel(R), N = { rel(R,_,D) }.

% number of parts for lower dimensional cubes for a relation,
% also helper for getting the index of subcube cell
num_parts(R,1,N) :- num_dims(R,N), rel(R), rel(R,N-1,D).
num_parts(R,L*LL,M) :- num_parts(R,LL,M+1), dim(D,L), rel(R,M,D).
num_parts(R,NP) :- num_parts(R,NP,0).

% subcube cell/ subcube voxel
sc_voxel(V,R,VV) :- VV = #sum{C*L : voxel(V,D,C), num_parts(R,_,M), rel(R,M,D), num_parts(R,L,M+1)}, rel(R), virt(V).

% normalized relation size, size of a subcube cell
cell_size(R,S) :- S = SS*CS/NP, size(R,SS), cube_size(CS), num_parts(R,NP).

%%%%%%%%%%%%
% generate

% assign voxel to physical servers
assign(V,RS) : phys(RS) :- virt(V).
1 { assign(V,RS) : phys(RS) } 1 :- virt(V).

%%%%%%%%%%%%
% define

% subcube cells that are used because of the assignments
work_element(P,S,(R,VV)) :- sc_voxel(V,R,VV), assign(V,P), cell_size(R,S).

dominates_first(Q) :-
  phys(Q),
  Q != 0,
  #sum { S,E: work_element(Q,S,E);
        -S,E: work_element(0,S,E) } > 0.

:- dominates_first(Q).

%%%%%%%%%%%%
% optimize

:~ work_element(0,S,E). [S,E]

#show assign/2.
