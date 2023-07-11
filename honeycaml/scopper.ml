
open Batteries
open Utils


(* CLI
   -------------------------------------------------------------------------- *)

let problems_path = ref "../qualifier-problems/"
let solutions_path = ref "../solutions/"
let power_phrases = ref []

let () =
  Arg.parse (Arg.align
    [
      ("-problems", Arg.String (fun s -> problems_path := s),
       " <path>");
      ("-solutions", Arg.String (fun s -> solutions_path := s),
       " <path>");
      ("-power", Arg.String (fun s -> power_phrases := s :: !power_phrases),
       " <string> Phrase of power");
    ])
    (fun _ -> ())
    ("Usage: " ^ Sys.argv.(0) ^ " [options]")


(* Scores
   -------------------------------------------------------------------------- *)

type solver_info =
  {
    name: string;
    revision: int;
  }

type game_score =
  {
    solver: solver_info;
    seed: int;
    score: int;
  }

type problem_score =
  {
    solver: solver_info;
    id: int;
    games: game_score list;
    score: int;
  }

type set_score =
  {
    solver: solver_info;
    problems: problem_score list;
    score: int;
  }


let parse_filename name : solver_info =
  match Filename.basename name with
    | RE "solution_" (digit+ as _problem_id: int)
         "_" (alpha+ as name)
         "_" (digit+ as revision: int)
         ".json" ->
        { name; revision }
    | _ ->
        assert false

let read_filenames dir =
  dir |> Sys.readdir |> Array.to_list

let games: Js_Game_t.t list =
  read_filenames !problems_path |> List.map (fun path ->
    Js_Game_j.t_of_string (File.with_file_in path IO.read_all))

let solutions: (solver_info * Js_Solution_t.t) list =
  read_filenames !solutions_path |> List.map (fun path ->
    (parse_filename path,
     Js_Solution_j.t_of_string (File.with_file_in path IO.read_all)))
