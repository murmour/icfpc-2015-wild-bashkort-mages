
open Batteries
open Utils


let input_files = ref []
let time_limit = ref None
let mem_limit = ref None
let cpu_cores = ref 1
let power_phrases = ref []

let _ =
  Arg.parse (Arg.align
    [
      ("-f", Arg.String (fun f -> input_files := f :: !input_files),
       " <path> File containing JSON encoded input");

      ("-t", Arg.Int (fun i -> assert (i > 0); time_limit := Some i),
       " <int> Time limit, in seconds, to produce output");

      ("-m", Arg.Int (fun i -> assert (i > 0); mem_limit := Some i),
       " <int> Memory limit, in megabytes, to produce output");

      ("-c", Arg.Int (fun i -> assert (i > 0); cpu_cores := i),
       " <int> Number of processor cores available");

      ("-p", Arg.String (fun s -> power_phrases := s :: !power_phrases),
       " <string> Phrase of power");
    ])
    (fun _ -> ())
    ("Usage: " ^ Sys.argv.(0) ^ " [options]")


let games: Js_Game_t.t list =
  !input_files |> List.rev |> List.map (fun path ->
    Js_Game_j.t_of_string (File.with_file_in path IO.read_all))

let solutions: Js_Solution_t.problem list =
  RefList.collecting (fun list ->
    games |> List.iter (fun (g: Js_Game_t.t) ->
      g.sourceSeeds |> List.iter (fun seed ->
        let sim = Simulator.make
            ~width:g.width
            ~height:g.height
            ~filled:g.filled
        in
        let source = Unit_.gen_source g.units ~seed ~len:g.sourceLength in
        let sol = Solver.solve sim source in
        RefList.push list
          Js_Solution_t.{
             problemId = g.id;
             seed;
             tag = Solver.tag;
             solution = Solution.to_string sol;
           })))

let () =
  Printf.printf "%s\n" (Js_Solution_j.string_of_t solutions)
