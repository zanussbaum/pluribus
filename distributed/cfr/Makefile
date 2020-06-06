OBJECTS = Node.o main.o State.o Trainer.o

CC = clang++

CXXFLAGS = -g -std=c++17



main: $(OBJECTS)
	$(CC) $(CXXFLAGS) -o main $(OBJECTS) -I.


%.o: %.cpp
	$(CC) $(CXXFLAGS) -c -o $@ -I. $<

clean:
	rm -rf *.o main