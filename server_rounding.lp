%-----------------------generate virtual server ------------------------
cube_size (CS) :- vs_size_temp(MAXD, CS), d_n(MAXD).
% virtual server
vs_size_temp(0,1).
vs_size_temp(I, J*S) :- vs_size_temp(I-1, J), d_size(I-1,S), I != 0.
% id of virtual server
vs_id(0..N-1) :- vs_size_temp(K,N), d_n(K).
% coordinate of virtual server, in the format of V: virtual server id,
% D: dimension, C: coornidate
vs_co(V, D, C):- 
    C = ( V \ P) / B,
    vs_id(V), d_size(D, _ ), 
    vs_size_temp(D, B), vs_size_temp(D+1, P).

% (only for test) vs_real_co(V,X1,X2,X3) 
%     :- vs_co(V, 0, X1), vs_co(V, 1, X2), vs_co(V, 2, X3).


%-------------------- map virtual server to real server-----------------
% generate an assignment
map_r_v(RS, V):rs(RS) :- vs_id(V).


%-------------------- compute sub-cube size ----------------------------
% sub-cube size of each relation
col_num(X, N) :- N = #count { r(X, K, Y): r(X, K, Y) }, r(X, _, _).
prod(X, 0, 1) :- r(X, _, _).
prod(X, Y, P*S) :- 
    prod(X, Y-1, P), r(X, Y, Z), d_size(Z, S), 
    Y <= N, col_num(X, N).
sub_cube_size(R, S) :- prod(R, MAXF, S), col_num(R, MAXF). 
sub_cube_share(R, (C * CS) / S) :- sub_cube_size(R, S), ts(R, C), cube_size(CS). 


%-------------------- compute workload per relation --------------------
% get the work load that each real server gets from a relation
% projection on sub_cube
subc_dim_base(R, N, 1) :- r(R, _, _), col_num(R, N).
subc_dim_base(R, F-1, DS*S ) :- 
    subc_dim_base(R, F, DS), r(R, F, D), d_size(D, S).

proj_vs_subc(V, R, F, D, C) :- r(R, F, D), vs_co(V, D, C).

subc_temp(V, R, N+1, 0) :- vs_id(V), r(R, _, _), col_num(R, N). 
subc_temp(V, R, F, LC + (C * DBASE) ) :- 
    proj_vs_subc(V, R, F, D, C),
    subc_dim_base(R, F, DBASE),
    subc_temp(V, R, F+1, LC).
map_v_subcid(V, R, SUBCID) :- 
    subc_temp(V, R, 1, SUBCID). 

map_s_subcid(RS, R, SUBCID) :- map_r_v(RS, V), map_v_subcid(V ,R ,SUBCID).
sub_cube_cover(RS, R, N) :-  
    N = #count { map_s_subcid(RS, R, SUBC):map_s_subcid(RS, R, SUBC) }, 
    rs(RS), r(R, _, _).
wl_on_relation(RS, R, N * SHARE) :- 
    sub_cube_cover(RS, R, N), sub_cube_share(R, SHARE).
wl_per_server_tmp(RS, 0, 0) :- rs(RS).
wl_per_server_tmp(RS, R, WL+W) :-
    wl_on_relation(RS, R, W), 
    rs(RS), 
    wl_per_server_tmp(RS, R-1, WL).
wl_per_server(RS, WL) :- wl_per_server_tmp(RS, N, WL),rnum(N).
max(N) :- 
    N = #max{ WL: wl_per_server(_, WL) }.

% break symmetry
:- not map_r_v(1, 0).

#minimize {  N: max(N) }.

% ------------------------- get the workload ---------------------------
#show map_r_v/2.
