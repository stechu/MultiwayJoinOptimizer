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
assign(V,RS) : phys(RS) :- virt(V).

%%%%%%%%%%%%
% test

% for testing purposes: each phys server should be used
%:- phys(P), not assign(_,P).

%%%%%%%%%%%%
% helper

% subcube cells that are used because of the assignments
matching_voxel(P,R,VV) :- sc_voxel(V,R,VV), assign(V,P).
% workload for relations
cost(P,R,C) :- C = N*S, N = { matching_voxel(P,R,VV) }, phys(P), rel(R), cell_size(R,S).

% sum up the costs
% workload(P,WL) :- WL = #sum { C,cost(P,R,C) : cost(P,R,C) }, phys(P).
workload(P,-1,0) :- phys(P).
workload(P,R,WL+C) :- cost(P,R,C), phys(P), workload(P,R-1,WL).
workload(P,WL) :- workload(P,r-1,WL).

maxwl(MWL) :- MWL = #max { WL : workload(_,WL) }.
%% maxwl(0,MWL) :- workload(0,MWL).
%% maxwl(P,MWL) :- workload(P,WL), maxwl(P-1,MWL), MWL >= WL.
%% maxwl(P,WL) :- workload(P,WL), maxwl(P-1,MWL), MWL < WL.
%% maxwl(MWL) :- maxwl(p-1,MWL).

%%%%%%%%%%%%
% constraints that help the solver

% fix one server to break symmetry
:- not assign(0,0).
%:- assign(1,P), P > 1, phys(P).

%%%%%%%%%%%%
% optimize

#minimize { MC : maxwl(MC) }.

%%%%%%%%%%%%
% print

#show assign/2.
