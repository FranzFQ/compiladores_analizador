; hola mundo version 64 bits
; nasm -f elf64 print_nasn_64.asm -o print_nasn_64.o
; ld -o print_nasn_64 print_nasn_64.o

section .data
    msg db 'hola mundo!', 10

section .text
    global_start

_start: 
    mov     rdx, 12 ; Cantidad de caracteres en la cadena
    mov     rsi, msg ; Apunta a direccion base de la cadena
    mov     rdi, 1 ; stdout (Salida estandar del computador que es el monitor)
    mov     rax, 1, 
    syscall 

    mov     rax, 60
    xor     rdi, rdi
    syscall



