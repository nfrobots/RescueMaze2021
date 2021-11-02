#include <windows.h>
#include <stdio.h>
#include <stdint.h>

int main()
{
    HANDLE serial;

    serial = CreateFile(
        "COM7",
        GENERIC_READ | GENERIC_WRITE,
        0,
        0,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        0
    );

    DCB serialParams = {0};

    serialParams.DCBlength = sizeof(serialParams);

    if(!GetCommState(serial, &serialParams))
    {
        CloseHandle(serial);
        return 1;
    }

    serialParams.BaudRate    = CBR_256000;
    serialParams.ByteSize    = 8;
    serialParams.StopBits    = ONESTOPBIT;
    serialParams.Parity      = NOPARITY;

    if(!SetCommState(serial, &serialParams))
    {
        CloseHandle(serial);
        return 2;
    }

    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 10;
    timeouts.ReadTotalTimeoutConstant = 500;
    timeouts.ReadTotalTimeoutMultiplier = 1;
    timeouts.WriteTotalTimeoutConstant = 50;
    timeouts.WriteTotalTimeoutMultiplier = 10;

    if(!SetCommTimeouts(serial, &timeouts))
    {
        CloseHandle(serial);
        return 3;
    }


    char write = 'a';
    unsigned char rBuff[100001] = {0};

    for(int rpt = 0; rpt < 10; rpt++)
    {
        if(!WriteFile(serial, &write, 1, NULL, NULL))
        {
            CloseHandle(serial);
            return 4;
        }

        memset(rBuff, 0, sizeof(rBuff));

        DWORD dwBytesRead = 0;

        if(!ReadFile(serial, rBuff, 100000, &dwBytesRead, NULL))
        {
            CloseHandle(serial);
            return 5;
        }

        printf(
            "############\n" \
            "Requested Image\n" \
            "Read %ld bytes\n" \
            "############\n",
            dwBytesRead - 255
        );

        // for(unsigned long i = 255; i < dwBytesRead; )
        // {
        //     for(int j = 0; j < 20; j++)
        //     {
        //         printf("0x%x   ", rBuff[i]);
        //         if (i < dwBytesRead)
        //             i++;
        //         else
        //             break;
        //     }
        //     printf("\n");
        // }

        FILE* f = fopen("C:\\Robo\\EspCamProject\\image.jpeg", "wb");
        size_t count = fwrite(rBuff + 255, 1, dwBytesRead - 255, f);
        fclose(f);

        printf("Wrote %d bytes to file", count);
    }

    CloseHandle(serial);
    return 0;
}

/*
const char* ssid = "FRITZ!Box 7530 OG";
const char* password = "80979652308404875218";
*/