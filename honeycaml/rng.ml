
open Batteries


type t = Int64.t


let make ~seed =
  Int64.of_int seed

let modulus =
  Int64.of_int (1 lsl 32)

let multiplier =
  Int64.of_int 1_103_515_245

let increment =
  Int64.of_int 12345

let mask15 =
  Int64.of_int ((1 lsl 15) - 1)

let get_next state =
  let open Int64 in
  let n = logand (shift_right state 16) mask15 in
  let state' = modulo (multiplier * state + increment) modulus in
  (Int64.to_int n, state')

let enum ~seed =
  Enum.from_loop (make ~seed) get_next
