%%%%%%%%%%%%
% helpers, everything static

% real servers
rs(1..p).

% generate virtual server

% cell cordinate base
% the coordinate base at I th dimension is: d_0 * d_1 * ... d_I
cell_co_base(0,1).
cell_co_base(I, J*S) :- cell_co_base(I-1, J), d_size(I-1,S).

cube_size (CS) :- cell_co_base(d, CS).

% id of virtual server
vs_id(0..N-1) :- cell_co_base(d,N).

% coordinate of virtual server, in the format of V: virtual server id,
% D: dimension, C: coordinate
vs_co(V, D, C):- 
    C = ( V \ P) / B, vs_id(V),  
    cell_co_base(D, B), cell_co_base(D+1, P).


%compute sub-cube size
% number of columns for each relation
col_num(R, N) :- N = #count { r(R, F, D): r(R, F, D) }, r(R, _, _).
% compute sub-cube size using induction
prod(R, 0, 1) :- r(R, _, _).
prod(R, F, P*S) :-
    prod(R, F-1, P), r(R, F, D), d_size(D, S), 
    F <= N, col_num(R, N).
subc_size(R, S) :- prod(R, MAXF, S), col_num(R, MAXF). 
subc_cell_size(R, (C * CS) / S) :- subc_size(R, S), ts(R, C), cube_size(CS).


%%%%%%%%%%%%
% generate

% map virtual server to real server
% generate an assignment
assign(V,RS) : rs(RS) :- vs_id(V).
:- not assign(_, RS), rs(RS).


%%%%%%%%%%%%
% helper

% compute workload per relation

% get the work load that each real server gets from a relation
% projection on sub_cube
subc_dim_base(R, N, 1) :- r(R, _, _), col_num(R, N).
subc_dim_base(R, F-1, DS*S ) :- 
    subc_dim_base(R, F, DS), r(R, F, D), d_size(D, S).
% coordinate of virtual server on sub-cube
vs_subc_co(V, R, F, D, C) :- r(R, F, D), vs_co(V, D, C).
% compute sub-cube cell id
subcid(V, R, N+1, 0) :- vs_id(V), r(R, _, _), col_num(R, N). 
subcid(V, R, F, LC + (C * DBASE) ) :- 
    vs_subc_co(V, R, F, D, C),
    subc_dim_base(R, F, DBASE),
    subcid(V, R, F+1, LC).
% map virtual server to cell of a relation's sub-cube
map_vs_subcid(V, R, SUBCID) :- 
    subcid(V, R, 1, SUBCID). 
% map real server to cell of a relation's sub-cube
map_rs_subcid(RS, R, SUBCID) :- assign(V, RS), map_vs_subcid(V ,R ,SUBCID).
% the number of sub-cube cells a real server covers
sub_cube_cover(RS, R, N) :-  
    N = #count { map_rs_subcid(RS, R, SUBC):map_rs_subcid(RS, R, SUBC) }, 
    rs(RS), r(R, _, _).
% the work load of a server from a relation
wl_on_relation(RS, R, N * SHARE) :- 
    sub_cube_cover(RS, R, N), subc_cell_size(R, SHARE).
% the total work load of a server from all relations 
wl_per_server(RS, 0, 0) :- rs(RS).
wl_per_server(RS, R, WL+W) :-
    wl_on_relation(RS, R, W),
    rs(RS),
    wl_per_server(RS, R-1, WL).
wl_per_server(RS, WL) :- wl_per_server(RS, r, WL).
% break symmetry
:- not assign(0, 1).
% the max workload per server
max(N) :- 
    N = #max{ WL: wl_per_server(_, WL) }.

%%%%%%%%%%%%
% optimize

#minimize { N: max(N) }.

%%%%%%%%%%%%
% print

#show assign/2.
