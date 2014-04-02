%%%%%%%%%%%%
% helpers, everything static

% real servers
rs(1..p).

% relations
r(R) :- r(R, _, _).

% generate virtual server

% cell coordinate base
% the coordinate base at I th dimension is: d_0 * d_1 * ... d_I
cell_co_base(0, 1).
cell_co_base(I, J*S) :- cell_co_base(I-1, J), d_size(I-1,S).

cube_size(CS) :- cell_co_base(d, CS).

% id of virtual server
virt(V) :- V = 0..CS-1, cube_size(CS).

% coordinate of virtual server, in the format of V: virtual server id,
% D: dimension, C: coordinate
vs_co(V, D, C):-
    C = ( V \ P) / B, virt(V),
    cell_co_base(D, B), cell_co_base(D+1, P).


%compute sub-cube size
% number of columns for each relation
col_num(R, N) :- N ={ r(R, F, D) }, r(R).

% compute sub-cube size using induction
prod(R, 0, 1) :- r(R).
prod(R, F, P*S) :-
    prod(R, F-1, P), r(R, F, D), d_size(D, S),
    F <= N, col_num(R, N).
subc_size(R, S) :- prod(R, MAXF, S), col_num(R, MAXF).
cell_size(R, C * CS / S) :- subc_size(R, S), ts(R, C), cube_size(CS).

% get the work load that each real server gets from a relation
% projection on sub_cube
subc_dim_base(R, N, 1) :- r(R), col_num(R, N).
subc_dim_base(R, F-1, DS*S ) :- subc_dim_base(R, F, DS), r(R, F, D), d_size(D, S).

% coordinate of virtual server on sub-cube
vs_subc_co(V, R, F, D, C) :- r(R, F, D), vs_co(V, D, C).

% compute sub-cube cell id
subcid(V, R, N+1, 0) :- virt(V), r(R), col_num(R, N).
subcid(V, R, F, LC + (C * DBASE) ) :-
    vs_subc_co(V, R, F, D, C),
    subc_dim_base(R, F, DBASE),
    subcid(V, R, F+1, LC).

%%%%%%%%%%%%
% generate

% map virtual server to real server
% generate an assignment
assign(V,RS) : rs(RS) :- virt(V).
1 { assign(V,RS) : rs(RS) } 1 :- virt(V).

% map virtual server to cell of a relation's sub-cube
sc_voxel(V, R, SUBCID) :- subcid(V, R, 1, SUBCID).

% assign voxel to physical servers
assign(V,RS) : rs(RS) :- virt(V).

%%%%%%%%%%%%
% define

% subcube cells that are used because of the assignments
work_element(RS,S,(R,VV)) :- sc_voxel(V,R,VV), assign(V,RS), cell_size(R,S).

dominates_first(Q) :-
  rs(Q),
  Q != 0,
  #sum { S,E: work_element(Q,S,E);
        -S,E: work_element(1,S,E) } > 0.

:- dominates_first(Q).

%%%%%%%%%%%%
% optimize

:~ work_element(1,S,E). [S,E]

%%%%%%%%%%%%
% print

#show assign/2.
