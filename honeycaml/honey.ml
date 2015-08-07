
open Batteries


let game: Game_t.t =
  File.with_file_in Sys.argv.(1) IO.read_all |> Game_j.t_of_string

let () =
  let { width; height; filled }: Game_t.t = game in
  let board = Board.create ~width ~height ~filled in
  let score = Board.get_score board in
  ()
