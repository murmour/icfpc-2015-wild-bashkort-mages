
type t

type dir = L | R | LD | RD | LU | RU


val make: width: int -> height: int -> t

val set: t -> Cell_t.t -> bool -> unit

val get: t -> Cell_t.t -> bool option

val copy: t -> t

val move: t -> Cell_t.t -> dir -> len: int -> Cell_t.t
