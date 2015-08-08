
type t
type focus


val make: width: int -> height: int -> filled: Board.cell list -> t

val add_unit: t -> Unit_.t -> max_rot: int -> [ `Focus of focus | `End ]

val act: focus -> Solution.command -> [ `Focus of focus | `Ready of t | `End ]

val get_score: t -> int
