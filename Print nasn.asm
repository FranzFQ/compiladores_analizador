#Codigo de print en ensamblador NASM

%include '#nombre_del_archivo.asm'

SECCION .DATA
	msg db 'Hola mundo!', 0AH, 0

SECCION .TEXT
global _start 

_start:
; -----------Imprimir = printstr(msg)--------------
	mov eax, msg
	call printstr

;--------end----------------
	call quit


#Otro archivo
#nombre_del_archivo.asm
; -----------Calculo de longitud de cadena---------
strlen: 
	push ebx
	mov ebx, eax

nextChar:
	cmp byte [eax], 0
	jz finLen
	inc eax 
	jmp nextChar	

finLen:
	sub eax, ebx
	pop ebx
	ret	

; -----------Imprimir = printstr(msg)--------------
printstr:
	; guarda registros en la pila
	push edx
	push ecx
	push ebx
	push eax ; aca apunta a la cadena
	call strlen
	
	mov edx, eax ;Longitud de cadena
	
	pop eax 
	mov ecx, eax ; Cadena a imprimir

	mov ebx, 1 ; Tipo de salida 
	mov eax, 4 ; Invocación al SYS_WRITE (kernel opocode 4)
 	int 80h

	pop ebx
	pop ecx
	pop edx
	ret 

;--------end----------------
quit:
	mov ebx, 0 ; return 0 status on exit 
	mov eax, 1 : SYS-EXIT (kernel opcode 1)
	int 80h


	