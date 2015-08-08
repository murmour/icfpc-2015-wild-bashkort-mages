
open Batteries


module RefList = struct
  include RefList

  let collecting action =
    let list = empty () in
    action list;
    list |> to_list |> List.rev

end
