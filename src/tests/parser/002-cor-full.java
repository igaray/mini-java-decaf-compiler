/* este caso es un ejemplo correcto completo que cubre la mayoria de las estructuras validas. */
classDef id { 
    // constructor with no formal arguments
    id();
    // constructor with one formal argument
    id(int id);
    id(char id);
    id(boolean id);
    id(String id);
    id(id id);
    // constructor with more than one formal arguments
    id(int id, id id, int id);
    // methods with no formal arguments
    void id();
    int id();
    char id();
    boolean id();
    String id();
    id id();
    // methods with one formal argument
    void id(int id);
    int id(int id);
    char id(int id);
    boolean id(int id);
    String id(int id);
    id id(int id);
    // methods with more than one formal arguments
    void id(int id, id id, int id);
    int id(int id, id id, int id);
    char id(int id, id id, int id);
    boolean id(int id, id id, int id);
    String id(int id, id id, int id);
    id id(int id, id id, int id);
}

// another classDef
classDef id { 
    id();
}

class id {
    // single fields
    int id;
    char id;
    boolean id;
    String id;
    id id;
    // multiple fields of the same type
    int id, id, id;
    char id, id, id;
    boolean id, id, id;
    String id, id, id;
    id id, id, id;
    // constructor with no formal arguments
    id() {}
    // constructor with one formal argument
    id(int id) {}
    id(char id) {}
    id(boolean id) {}
    id(String id) {}
    id(id id) {}
    // constructor with more than one formal arguments
    id(int id, id id, int id) {}
    // methods with no formal arguments
    void id() {}
    int id() {}
    char id() {}
    boolean id() {}
    String id() {}
    id id() {}
    // methods with one formal argument
    void id(int id) {}
    int id(int id) {}
    char id(int id) {}
    boolean id(int id) {}
    String id(int id) {}
    id id(int id) {}
    // methods with more than one formal arguments
    void id(int id, id id, int id) {}
    int id(int id, id id, int id) {}
    char id(int id, id id, int id) {}
    boolean id(int id, id id, int id) {}
    String id(int id, id id, int id) {}
    id id(int id, id id, int id) {}

    // methods with statements
    void method() {
        return;
    }
    int method() {
        id = id;
        // arithmetic expressions
        id = 1 + 2;
        id = 1 - 2;
        id = 1 * 2;
        id = 1 / 2;
        id = 1 % 2;
        id = (1 + 2) * 3;
        id = (id + (id - (id * (id / (id % (id))))));
        // logical expressions
        id = ! true;
        id = ! id;
        id = -id;
        id = id < id;
        id = id > id;
        id = id <= id;
        id = id >= id;
        id = id == id;
        id = id != id;
        // primary expressions
        id = new id(); 
        id = new id(id, 2, true);
        id = super.id();
        id = super.id(1, id, true);
        id = this;
        id = this.id();
        id = this.id(1, id, true);
        id = this.id().id(1, id, true);
        id = id();
        id = id(1, id, true);
        id = id.id();
        id = id.id(1, id, true);

        return 0;
    }
}

class id {
    id() { }
}

