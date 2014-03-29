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
1 { assign(V,P) : phys(P) } 1 :- voxel(V,D,C).

%%%%%%%%%%%%
% test

% for testing purposes: each phys server should be used
%:- phys(P), not assign(_,P).

%%%%%%%%%%%%
% helper

% cost of assignment for relations
matching_voxel(P,R,VV) :- sc_voxel(V,R,VV), assign(V,P).
cost(P,R,C) :- C = CC*S, CC = { matching_voxel(P,R,VV) }, cell_size(R,S), phys(P), rel(R).
cost(P,C) :- C = #sum { CC,cost(P,R,CC) : cost(P,R,CC) }, phys(P).

maxcost(MC) :- MC = #max { C : cost(P,C) }.

%%%%%%%%%%%%
% constraints that help the solver

% we need at least the number of parts subcube voxels or otherwise data got lost
%:- num_parts(R, NP), NP < #sum { N : count(P,R,N) }, rel(R).

% fix one server to break symmetry
:- not assign(0,0).
:- assign(1,P), P > 1, phys(P).

%%%%%%%%%%%%
% optimize

#minimize { MC : maxcost(MC) }.

%%%%%%%%%%%%
% print

#show assign/2.
