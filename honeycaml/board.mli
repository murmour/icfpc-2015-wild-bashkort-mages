
type t

type dir = L | R | LD | RD | LU | RU

type rot_dir = CW | CCW


val make: width: int -> height: int -> t

val set: t -> Cell_t.t -> bool -> unit

val get: t -> Cell_t.t -> bool option

val copy: t -> t

val move: Cell_t.t -> dir -> len: int -> Cell_t.t

val rotate: pivot: Cell_t.t -> Cell_t.t -> rot_dir -> Cell_t.t
