% physical machines
#const p = 6.

% dimensions
#const n = 3.

% length of cube in dimension
% d(D,L)
dim(0,2).
dim(1,2).
dim(2,3).

% relations
#const r = 3.

% sizes of relations
% size(R,S)
size(0,500).
size(1,100).
size(2,1000).

% dimensions of relations with the information which dimension it is
% rel(R,N,D)
rel(0,0,0). rel(0,1,1).
rel(1,0,1). rel(1,1,2).
rel(2,0,0). rel(2,1,2).
