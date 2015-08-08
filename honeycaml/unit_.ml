
open Batteries


type t = Game_t.unit_


let rotate (u: t) dir : t =
  let members = u.members |> List.map (fun (c: Board.cell) ->
    Board.rotate ~pivot:u.pivot c dir)
  in
  { u with members }

let isomorphic (u1: t) (u2: t) =
  if u1.pivot <> u2.pivot then
    false
  else
    Set.equal (Set.of_list u1.members) (Set.of_list u2.members)

let calc_max_rot (u: t) =
  let rec iter u' count =
    if isomorphic u u' then
      count
    else
      iter (rotate u' CW) (count + 1)
  in
  iter (rotate u CW) 1
