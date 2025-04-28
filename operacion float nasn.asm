; Manejo de valores de coma flotante
; creador: abemen
; fecha: 21 abr 2025
; para compilar: nasm -f elf64 flotante.asm -l flotante.lst
; link: gcc -m64 flotante.o -o flotante -no-pie

extern printf

section .data
	pi: dq 3.14159
	diámetro: dq 5.0
	format db "C = ¶*d = %f * %f = %f", 10, 0

section .bss
	c:	resq	1	

sectio .text
	global main 

main:
	push	rbp
	fld	qword [diametro]	; carga el radio al registro STO
	fmul	qword [pi]		; diámetro * pi
	fstp	qword [c]		; guarda el resultado de STO en c
	;------------------ Llamada a print f----------------------
	mov	rdi, format		; carga la cadena formateada
	movq	xmm0, [pi]
	movq	xmml, qword [diamtro]
	movq	xmm2, qword [c]
	mov	rax, 3
	call	printf
	
	pop 	rbq
	
	mov 	rax, 1
	xor	rbx, rbx
	int	80h

		
