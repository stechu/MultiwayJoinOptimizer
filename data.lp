% physical servers
#const p = 4.

% number of dimensions
#const d = 3.

% size of each dimension
d_size(0,2).
d_size(1,2).
d_size(2,3).

% joins
#const r = 3.

r(1,1,0). r(1,2,1).
r(2,1,1). r(2,2,2).
r(3,1,0). r(3,2,2).

% size of tables
ts(1, 500).
ts(2, 100).
ts(3, 1000).
