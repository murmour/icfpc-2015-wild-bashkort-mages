
type t =
  {
    matrix: bool array array;
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


let create ~width ~height ~filled =
  let matrix = Array.make_matrix width height false in
  filled |> List.iter (fun (c: Cell_t.t) ->
    matrix.(c.x).(c.y) <- true);
  {
    matrix;
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
