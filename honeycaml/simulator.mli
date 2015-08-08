
type t
type focus

type command =
  | MoveE
  | MoveW
  | MoveSE
  | MoveSW
  | TurnCW
  | TurnCCW


val make: width: int -> height: int -> filled: Board.cell list -> t

val add_unit: t -> Unit.t -> max_rot: int -> [ `Focus of focus | `End ]

val command: focus -> command -> [ `Focus of focus | `Ready of t | `End ]

val get_score: t -> int
