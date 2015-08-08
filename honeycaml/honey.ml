
open Batteries


let game: Game_t.t =
  File.with_file_in Sys.argv.(1) IO.read_all |> Game_j.t_of_string

let sim =
  Simulator.make
    ~width:game.width
    ~height:game.height
    ~filled:game.filled

let () =
  let score = Simulator.get_score sim in
  ()
