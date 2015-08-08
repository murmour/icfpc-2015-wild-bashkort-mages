
open Batteries


type t = char list

type command =
  | MoveE
  | MoveW
  | MoveSE
  | MoveSW
  | TurnCW
  | TurnCCW


let decode_command c =
  match Char.lowercase c with
    | 'p' | '\'' | '!' | '.' | '0' | '3' -> MoveW
    | 'b' | 'c' | 'e' | 'f' | 'y' | '2' -> MoveE
    | 'a' | 'g' | 'h' | 'i' | 'j' | '4' -> MoveSW
    | 'l' | 'm' | 'n' | 'o' | ' ' | '5' -> MoveSE
    | 'd' | 'q' | 'r' | 'v' | 'z' | '1' -> TurnCW
    | 'k' | 's' | 't' | 'u' | 'w' | 'x' -> TurnCCW
    | _ -> assert false


let encode_command c =
  match c with
    | MoveE -> 'b'
    | MoveW -> 'p'
    | MoveSW -> 'a'
    | MoveSE -> 'l'
    | TurnCW -> 'd'
    | TurnCCW -> 'k'


let to_string l =
  String.of_list l
