
open Batteries


type t =
  {
    board: Board.t;
    width: int;
    height: int;
    score: int;
  }

type focus =
  {
    ctx: t;
    unit: Unit_t.t;
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

let add_unit (ctx: t) (u: Unit_t.t) : [ `Focus of focus | `End ] =
  let min_y = ref max_int in
  let min_x = ref max_int in
  let max_x = ref min_int in
  u.members |> List.iter (fun (c: Cell_t.t) ->
    if c.y < !min_y then min_y := c.y;
    if c.x < !min_x then min_x := c.x;
    if c.x > !max_x then max_x := c.x);

  let offset_y = !min_y in
  let offset_x = (ctx.width - (!max_x - !min_x + 1)) / 2 - !min_x in

  let move_cell (c: Cell_t.t) : Cell_t.t =
    let c' = Board.move c LU ~len:offset_y in
    Board.move c R ~len:(offset_x + (c.x - c'.x))
  in

  Return.label (fun lab ->
    let members = u.members |> List.map (fun (c: Cell_t.t) ->
      let c = move_cell c in
      if Board.is_empty_cell ctx.board c then
        c
      else
        Return.return lab `End)
    in
    let unit: Unit_t.t = { members; pivot = move_cell u.pivot } in
    `Focus { ctx; unit })

let command focus command : [ `Focus of focus | `Ready of t | `End ] =
  failwith "todo"

let get_score board =
  board.score
