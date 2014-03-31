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
num_parts(R,D+1,1,N) :- num_dims(R,N), rel(R), rel(R,N-1,D).
num_parts(R,D,L*LL,M) :- num_parts(R,_,LL,M+1), dim(D,L), rel(R,M,D).
num_parts(R,NP) :- num_parts(R,_,NP,0).

% subcube cell/ subcube voxel
sc_voxel(V,R,VV) :- VV = #sum{ C*L : voxel(V,D,C), num_parts(R,D,_,M), num_parts(R,_,L,M+1)}, rel(R), virt(V).

% normalized relation size, size of a subcube cell
cell_size(R,S) :- S = SS*CS/NP, size(R,SS), cube_size(CS), num_parts(R,NP).

%%%%%%%%%%%%
% generate

% assign voxel to physical servers
1 { assign(V,RS) : phys(RS) } 1 :- virt(V).


%%%%%%%%%%%%
% define

% subcube cells that are used because of the assignments
matching_voxel(P,R,VV) :- sc_voxel(V,R,VV), assign(V,P).
work_element(P,S,R,VV) :- matching_voxel(P,R,VV), rel(R), cell_size(R,S).

dominates(P,Q) :-
  phys(P),
  phys(Q),
  P != Q,
  #sum { S,R,VV: work_element(P,S,R,VV);
        -S,R,VV: work_element(Q,S,R,VV) } >= 1.


dominant(P) :- phys(P); not dominates(Q,P):Q!=P,phys(Q).
bottleneck(P) :- phys(P), P = #min { Pi:dominant(Pi) }.

bottleneck_workload(S,R,VV) :- bottleneck(P), work_element(P,S,R,VV).


%%%%%%%%%%%%
% symmetry breaking
:- phys(P;Q), P < Q, dominates(Q,P).


%%%%%%%%%%%%
% optimize

:~ bottleneck_workload(S,R,VV). [S,R,VV]

#show assign/2.
#show dominates/2.
#show dominant/1.
#show bottleneck/1.
