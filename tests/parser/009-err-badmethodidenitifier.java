/* este caso muestra la deteccion de un identificador de metodo invalido en el classDef. */
classDef id { 
    id();
    id 123();
}

class id {
    id() { }
}

