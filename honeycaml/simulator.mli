
type t
type focus

type command =
  | MoveE
  | MoveW
  | MoveSE
  | MoveSW
  | TurnCW
  | TurnCCW


val make: width: int -> height: int -> filled: Cell_t.t list -> t

val add_unit: t -> Unit_t.t -> [ `Focus of focus | `End ]

val command: focus -> command -> [ `Focus of focus | `Ready of t | `End ]

val get_score: t -> int
