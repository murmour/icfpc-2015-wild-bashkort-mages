CC = g++
CFLAGS = -O2 -Wall


play_icfp2015: jsoncpp.o main.o system.o
	g++ jsoncpp.o main.o system.o -o play_icfp2015

.cpp.o:
	$(CC) $(CFLAGS) -o $@ -c $<

clean:
	rm -rf *.o
