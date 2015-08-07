
type t =
  {
    arr: bool array;
    width: int;
    height: int;
  }

type dir = L | R | LD | RD | LU | RU


let reverse_dir = function
  | L -> R
  | R -> L
  | LD -> RU
  | RD -> LU
  | LU -> RD
  | RU -> LD

let make ~width ~height =
  let arr = Array.make (width * height) false in
  { arr; width; height }

let get (b: t) (c: Cell_t.t) =
  if c.x < b.width && c.y < b.height then
    Some (b.arr.(c.y * b.width + c.x))
  else
    None

let set (b: t) (c: Cell_t.t) (v: bool) =
  if c.x < b.width && c.y < b.height then
    b.arr.(c.y * b.width + c.x) <- v

let rec move (b: t) (c: Cell_t.t) dir ~len : Cell_t.t =
  if len < 0 then
    move b c (reverse_dir dir) (-len)
  else if (c.y land 1) = 0 then
    match dir with
      | L  -> { c with x = c.x - len }
      | R  -> { c with x = c.x + len }
      | LD -> { x = c.x - ((len+1) / 2); y = c.y + len }
      | RD -> { x = c.x - (len / 2); y = c.y + len }
      | LU -> { x = c.x - ((len+1) / 2); y = c.y - len }
      | RU -> { x = c.x - (len / 2); y = c.y - len }
  else
    match dir with
      | L  -> { c with x = c.x - len }
      | R  -> { c with x = c.x + len }
      | LD -> { x = c.x - (len / 2); y = c.y + len }
      | RD -> { x = c.x - ((len+1) / 2); y = c.y + len }
      | LU -> { x = c.x - (len / 2); y = c.y - len }
      | RU -> { x = c.x - ((len+1) / 2); y = c.y - len }

let copy (b: t) =
  { b with arr = Array.copy b.arr }
