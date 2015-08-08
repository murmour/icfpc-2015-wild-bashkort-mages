
type t =
  {
    arr: int array;
    width: int;
    height: int;
  }

type dir = L | R | LD | RD | LU | RU

type rot_dir = CW | CCW

type cell = Game_t.cell


let get_cell_bit (b: t) (c: cell) (i: int) : bool =
  let n = b.arr.(c.y * b.width + c.x) in
  (i lsr n) land 1 = 1

let set_cell_bit (b: t) (c: cell) (i: int) (v: bool) : unit =
  let idx = c.y * b.width + c.x in
  if v then
    b.arr.(idx) <- i lor (1 lsl b.arr.(idx))
  else
    b.arr.(idx) <- i land (lnot (1 lsl b.arr.(idx)))

let reverse_dir = function
  | L -> R
  | R -> L
  | LD -> RU
  | RD -> LU
  | LU -> RD
  | RU -> LD

let make ~width ~height =
  let arr = Array.make (width * height) 0 in
  { arr; width; height }

let is_filled (b: t) (c: cell) =
  if c.x < b.width && c.y < b.height then
    Some (get_cell_bit b c 0)
  else
    None

let set_filled (b: t) (c: cell) (v: bool) =
  if c.x < b.width && c.y < b.height then
    set_cell_bit b c 0 v

let rec move (c: cell) dir ~len : cell =
  if len < 0 then
    move c (reverse_dir dir) (-len)
  else if (c.y land 1) = 0 then
    match dir with
      | L -> { c with x = c.x - len }
      | R -> { c with x = c.x + len }
      | LD -> { x = c.x - ((len+1) / 2); y = c.y + len }
      | RD -> { x = c.x - (len / 2); y = c.y + len }
      | LU -> { x = c.x - ((len+1) / 2); y = c.y - len }
      | RU -> { x = c.x - (len / 2); y = c.y - len }
  else
    match dir with
      | L -> { c with x = c.x - len }
      | R -> { c with x = c.x + len }
      | LD -> { x = c.x - (len / 2); y = c.y + len }
      | RD -> { x = c.x - ((len+1) / 2); y = c.y + len }
      | LU -> { x = c.x - (len / 2); y = c.y - len }
      | RU -> { x = c.x - ((len+1) / 2); y = c.y - len }

let rotate ~(pivot: cell) (p: cell) dir : cell =
  let ydiff = pivot.y - p.y in
  let temp = move pivot LU ~len:ydiff in
  let xdiff = temp.x - p.x in
  match dir with
    | CW ->
        move (move pivot RU ~len:ydiff) LU ~len:xdiff
    | CCW ->
        move (move pivot L ~len:ydiff) LD ~len:xdiff

let copy (b: t) =
  { b with arr = Array.copy b.arr }

let is_valid_cell (b: t) (c: cell) =
  c.x < b.width && c.y < b.height

let is_empty_cell (b: t) (c: cell) =
  is_valid_cell b c && (get_cell_bit b c 0)

let has_rot (b: t) (c: cell) rot =
  if c.x < b.width && c.y < b.height then
    Some (get_cell_bit b c (rot + 1))
  else
    None

let set_rot (b: t) (c: cell) rot =
  if c.x < b.width && c.y < b.height then
    set_cell_bit b c (rot + 1) true

let reset_rot (b: t) =
  for i = 0 to Array.length b.arr - 1 do
    b.arr.(i) <- b.arr.(i) land 1
  done
