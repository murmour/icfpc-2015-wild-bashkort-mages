
type t =
  {
    arr: bool array;
    width: int;
    height: int;
  }


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
  else
    ()

let copy (b: t) =
  { b with arr = Array.copy b.arr }
