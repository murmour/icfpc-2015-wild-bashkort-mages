
open Batteries


type t =
  {
    board: Board.t;
    width: int;
    height: int;
    score: int;
  }

type unit_ = Game_t.unit_

type focus =
  {
    ctx: t;
    unit: unit_;
    rot: int;
    max_rot: int;
  }

type command =
  | MoveE
  | MoveW
  | MoveSE
  | MoveSW
  | TurnCW
  | TurnCCW


let make ~width ~height ~filled =
  let board = Board.make ~width ~height in
  filled |> List.iter (fun c -> Board.set_filled board c true);
  {
    board;
    width;
    height;
    score = 0;
  }

let add_unit (ctx: t) (u: unit_) ~max_rot : [ `Focus of focus | `End ] =
  let min_y = ref max_int in
  let min_x = ref max_int in
  let max_x = ref min_int in
  u.members |> List.iter (fun (c: Board.cell) ->
    if c.y < !min_y then min_y := c.y;
    if c.x < !min_x then min_x := c.x;
    if c.x > !max_x then max_x := c.x);

  let offset_y = !min_y in
  let offset_x = (ctx.width - (!max_x - !min_x + 1)) / 2 - !min_x in

  let move_cell (c: Board.cell) : Board.cell =
    let c' = Board.move c LU ~len:offset_y in
    Board.move c R ~len:(offset_x + (c.x - c'.x))
  in

  Return.label (fun lab ->
    let members = u.members |> List.map (fun (c: Board.cell) ->
      let c = move_cell c in
      if Board.is_empty_cell ctx.board c then
        c
      else
        Return.return lab `End)
    in
    let unit: unit_ = { members; pivot = move_cell u.pivot } in
    `Focus { ctx; unit; rot = 0; max_rot })

let command focus command : [ `Focus of focus | `Ready of t | `End ] =
  failwith "todo"

let get_score board =
  board.score
