% number of dimensions
d_n(3).

% size of each dimension
d_size(0,2).
d_size(1,2).
d_size(2,3).

% real servers - generate by python
rs(1..4).

%% joins - generate by python
rnum(3).
% r1
r(1,1,0). 
r(1,2,1).

%r2 
r(2,1,1). 
r(2,2,2).

%r3
r(3,1,0). 
r(3,2,2).

% size of tables - generate by python
ts(1, 500).
ts(2, 100).
ts(3, 1000).