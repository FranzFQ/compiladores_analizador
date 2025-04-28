; hola mundo version 64 bits
; nasm -f elf64 print_nasn_64_v2.asm -o print_nasn_64_v2.o
; ld -o print_nasn_64 print_nasn_64_v2.o

%include    'stdio64.asm'

section .data
    msg db 'Hola mundo!', 10, 0

section .text
    global_start

_start: 
    mov     rax, msg
    call    printStr

    call salir