
open Batteries


module RefList: sig
  include module type of RefList

  val collecting: ('a t -> unit) -> 'a list

end
