
type t = Js_Game_t.unit_


val rotate: t -> Board.rot_dir -> t

val isomorphic: t -> t -> bool

val gen_source: t list -> seed: int -> len: int -> t list
