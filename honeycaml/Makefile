GEN_DIR := _generated
ATDGEN := atdgen -j-std -j-strict-fields
OBUILD_FLAGS := $(CORES) -I $(GEN_DIR) -use-ocamlfind -cflags -w,-30-40


$(GEN_DIR):
	mkdir $(GEN_DIR)

atd: game.atd solution.atd $(GEN_DIR)
	$(ATDGEN) -t game.atd -o $(GEN_DIR)/js_Game
	$(ATDGEN) -j game.atd -o $(GEN_DIR)/js_Game
	$(ATDGEN) -t solution.atd -o $(GEN_DIR)/js_Solution
	$(ATDGEN) -j solution.atd -o $(GEN_DIR)/js_Solution

honey: atd
	ocamlbuild $(OBUILD_FLAGS) honey.native

scopper: atd
	ocamlbuild $(OBUILD_FLAGS) scopper.native

scop:
	find ../solutions/ -type f | xargs ./scopper.native

clean:
	ocamlbuild -clean
