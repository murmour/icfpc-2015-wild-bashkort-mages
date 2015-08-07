
type t


val make: width: int -> height: int -> t

val set: t -> Cell_t.t -> bool -> unit

val get: t -> Cell_t.t -> bool option

val copy: t -> t
