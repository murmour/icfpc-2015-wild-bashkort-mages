GEN_DIR := generated
ATDGEN := atdgen -j-std -j-strict-fields
OBUILD_FLAGS := $(CORES) -I $(GEN_DIR) -use-ocamlfind -cflags -w,-30-40

atd: game.atd solution.atd
	-mkdir $(GEN_DIR) 2>/dev/null
	$(ATDGEN) -t game.atd -o $(GEN_DIR)/game
	$(ATDGEN) -j game.atd -o $(GEN_DIR)/game
	$(ATDGEN) -t solution.atd -o $(GEN_DIR)/solution
	$(ATDGEN) -j solution.atd -o $(GEN_DIR)/solution

honey: atd
	ocamlbuild $(OBUILD_FLAGS) honey.native
