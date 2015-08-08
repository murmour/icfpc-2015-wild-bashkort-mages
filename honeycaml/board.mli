
type t

type dir = L | R | LD | RD | LU | RU

type rot_dir = CW | CCW

type cell = Game_t.cell


val make: width: int -> height: int -> t

val is_filled: t -> cell -> bool option

val set_filled: t -> cell -> bool -> unit

val copy: t -> t

val move: cell -> dir -> len: int -> cell

val rotate: pivot: cell -> cell -> rot_dir -> cell

val is_valid_cell: t -> cell -> bool

val is_empty_cell: t -> cell -> bool

val has_rot: t -> cell -> int -> bool option

val set_rot: t -> cell -> int -> unit

val reset_rot: t -> unit
