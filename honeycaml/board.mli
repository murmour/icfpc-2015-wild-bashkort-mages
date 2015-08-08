
type t

type dir = L | R | LD | RD | LU | RU

type rot_dir = CW | CCW

type cell = Game_t.cell


val make: width: int -> height: int -> t

val set: t -> cell -> bool -> unit

val get: t -> cell -> bool option

val copy: t -> t

val move: cell -> dir -> len: int -> cell

val rotate: pivot: cell -> cell -> rot_dir -> cell

val is_valid_cell: t -> cell -> bool

val is_empty_cell: t -> cell -> bool
