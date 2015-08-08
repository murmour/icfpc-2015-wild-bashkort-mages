
open Batteries


type t


val make: seed: int -> t

val get_next: t -> (int * t)

val enum: seed: int -> int Enum.t
