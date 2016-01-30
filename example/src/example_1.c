#include <stdio.h>
#include <unistd.h>

#include "log_fsm.h"
#include "config.h"

#define BLOCK_SIZE      (10)

static write_block(FILE *fp)
{
    size_t block = BLOCK_SIZE;
    uint8_t tmp[BLOCK_SIZE];

    while(block == BLOCK_SIZE)
    {    
        block = log_fsm_get(tmp, BLOCK_SIZE);
        fwrite(tmp, 1, block, fp);
    }

    fflush(fp);
}

int main(int argc, char *argv[])
{
    printf("Starting %s version %s\n", argv[0], VERSION_STRING);

    FILE *fp;
    uint8_t i;

    fp = fopen("example_1.bin", "wb");
    if(fp)
    {
        log_fsm_machine_init();

        for(i=0; i < 100; i++)
        {
            log_fsm_state_entry(0x0001);
            log_fsm_error(0x04567, 23445);
            
            usleep(2000);
                
            log_fsm_state_exit(0x0001);

            log_fsm_state_entry(0x0002);
            log_fsm_error(0x1, 5);
            log_fsm_state_exit(0x0002);

            write_block(fp);
        }

        write_block(fp);


        for(i=0; i < 100; i++)
        {
            log_fsm_state_entry(0x0001);
            log_fsm_error(0x04567, 23445);
            
            usleep(2000);
                
            log_fsm_state_exit(0x0001);

            log_fsm_state_entry(0x0002);
            log_fsm_error(0x1, 5);
            log_fsm_state_exit(0x0002);
        }

        write_block(fp);

        log_fsm_machine_deinit();

        write_block(fp);
        fclose(fp);
    }
    else
    {
        perror(NULL);
        return 1;
    }

    return 0;
}
