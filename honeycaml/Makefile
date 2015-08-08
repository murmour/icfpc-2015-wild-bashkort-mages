GEN_DIR := generated
ATDGEN := atdgen -j-std -j-strict-fields
OBUILD_FLAGS := $(CORES) -I $(GEN_DIR) -use-ocamlfind -cflags -w,-30-40

atd: game.atd solution.atd
	-mkdir $(GEN_DIR) 2>/dev/null
	$(ATDGEN) -t game.atd -o $(GEN_DIR)/js_Game
	$(ATDGEN) -j game.atd -o $(GEN_DIR)/js_Game
	$(ATDGEN) -t solution.atd -o $(GEN_DIR)/js_Solution
	$(ATDGEN) -j solution.atd -o $(GEN_DIR)/js_Solution

honey: atd
	ocamlbuild $(OBUILD_FLAGS) honey.native

clean:
	ocamlbuild -clean
