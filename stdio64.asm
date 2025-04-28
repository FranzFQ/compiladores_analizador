; ----------------------int srtLen(cadena)---------------------------
strLen:
    push rsi ; resguardar en la pila rsi
    mov rsi, rax
 sigChar:
    cmp byte[rax], 0
    jz finStrLen
    inc rax 
    jmp sigChar

finStrLen:
    sub rax, rsi
    pop rsi ; restauro el contenido previo de rsi
    ret

; ----------------------printStr(cadena)-----------------------------
printStr:
    ; resguardar registros en pila
    push rdx 
    push rsi
    push rdi
    push rax 

    ; ------------llamada a longituda de cadena (cadena en rax)
    call strLen

    ; ------------la longitud se devuelve en rax
    mov rdx, rax ; longitud de cadena
    pop rax
    mov rsi, rax ; apunta a direccion base de la cadena
    mov rdi, 1 ; stdout
    mov rax, 1
    syscall
    ; -----------------devolver el contenido a los registros
    pop rdi
    pop rsi
    pop rdx
    ret

; ---------------void salir()-------------------
salir:
    mov rax, 60
    xor rdi, rdi
    syscall
    ret

