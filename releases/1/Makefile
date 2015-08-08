CC = g++
CFLAGS = -O2 -Wall


steak: jsoncpp.o main.o system.o
	g++ jsoncpp.o main.o system.o -o steak

.cpp.o:
	$(CC) $(CFLAGS) -o $@ -c $<

clean:
	rm -rf *.o
