
type t =
  {
    board: Board.t;
    width: int;
    height: int;
    score: int;
  }

type focus =
  {
    board: t;
    unit: Unit_t.t;
    pos_x: int;
    pos_y: int;
  }

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


let make ~width ~height ~filled =
  let board = Board.make ~width ~height in
  filled |> List.iter (fun c -> Board.set board c true);
  {
    board;
    width;
    height;
    score = 0;
  }

let add_unit board u =
  failwith "todo"

let command focus command =
  failwith "todo"

let get_score board =
  board.score
