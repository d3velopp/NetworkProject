#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/select.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <ifaddrs.h>
#include <netinet/in.h>
#include <netdb.h>
#include <errno.h>

struct test
{
    uint8_t first;
    uint32_t second;
    uint32_t third;
    

};

int main(){
    printf("%ld",sizeof(struct test));
}