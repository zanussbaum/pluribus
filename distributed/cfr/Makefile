OBJECTS = State.o InfoNode.o Pluribus.o main.o 

CC = clang++

CXXFLAGS = -g -std=c++17 

main: $(OBJECTS)
	$(CC) $(CXXFLAGS) -lboost_iostreams -lboost_serialization -o main $(OBJECTS) -I.


%.o: %.cpp
	$(CC) $(CXXFLAGS) -c -o $@ -I. $<

clean:
	rm -rf *.o main