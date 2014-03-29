% physical machines
#const p = 4.

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
size(1,500).
size(2,100).
size(3,1000).

% dimensions of relations with the information which dimension it is
% rel(R,N,D)
rel(1,0,0). rel(1,1,1).
rel(2,0,1). rel(2,1,2).
rel(3,0,0). rel(3,1,2).
