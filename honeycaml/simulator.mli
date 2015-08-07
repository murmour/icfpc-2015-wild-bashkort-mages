
type t
type focus

type command =
  | MoveE
  | MoveW
  | MoveSE
  | MoveSW
  | TurnCW
  | TurnCCW

type outcome =
  | Focus of focus
  | Board of t
  | Finish


val make: width: int -> height: int -> filled: Cell_t.t list -> t

val add_unit: t -> Unit_t.t -> outcome

val command: focus -> command -> outcome

val get_score: t -> int
