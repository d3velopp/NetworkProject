#include <stdio.h>
#include <stdlib.h>
#include "network.h"

int main(int argc, char**argv) {
    (void)argc;
    int my_port = atoi(argv[1]);
    int my_python = atoi(argv[2]);
    int other_C_port = atoi(argv[3]);
    int mode = atoi(argv[4]);
    char*message = listen_server(my_port);
    while (1)
    {

        if (mode == 0) //LE PROCHAIN MESSAGE VIEN DE PYTHON
        {
            printf("j'attend la trame venant de python\n");
            send_server(other_C_port, message);
        }
        else
        {
            printf("j'attend la trame venant de C\n");
            send_server(my_python, message);
        }
    }
}
