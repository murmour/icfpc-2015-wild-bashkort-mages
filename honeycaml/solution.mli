
type t = char list

type command =
  | MoveE
  | MoveW
  | MoveSE
  | MoveSW
  | TurnCW
  | TurnCCW


val to_string: t -> string

val decode_command: char -> command

val encode_command: command -> char
