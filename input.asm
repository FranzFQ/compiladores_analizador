; lectura de datos desde teclado y almacenamiento en memoria
; fecha 20250428

%include 'stdio.asm'

section .data
    msg1 db 'Ingrese se nombre:', 0
    msg2 db 'hola   ', 0

section .bss
    nombre resb 20

section .bss
    nombre resb 20

section .text
    global _start 

_start:
    mov eax, msg1
    call printStr

    mov edx, 20     ; edx = espacio total para lectura
    mov ecx, nombre     ; ecx = dir.de memoria para almacenar el dato
    mov ebx, 0      ; lee desde STDIN
    mov eax, 3      ; servicio de SYS_DEAD
    int 80h

    mov eax, msg2
    call printStr
    
    mov eax, nombre
    call, printStr

    call quit 
