class barramento:
    def __init__(self, memoria, saida):
        self.memoria = memoria
        self.saida = saida

    def leia(self, endereco, tamanho=32):
        num_bytes = tamanho // 8
        if endereco <= self.memoria.RAM_LIMITE:
            return self.memoria.leia(endereco, num_bytes)
        
        elif self.memoria.VRAM <= endereco <= self.memoria.VRAM_LIMITE:
            return self.memoria.leia(endereco, num_bytes)
        
        return 0 

    def escreva(self, endereco, valor, tamanho=32):
        num_bytes = tamanho // 8
        if endereco <= self.memoria.RAM_LIMITE: #RAM
            self.memoria.escreva(endereco, valor, num_bytes)
        elif self.memoria.VRAM <= endereco <= self.memoria.VRAM_LIMITE: #VRAM
            self.memoria.escreva(endereco, valor, num_bytes)

    def imprimir(self):
        self.saida.atualizar_monitor(self.memoria)


class monitor:
    def atualizar_monitor(self, memoria):
        output = ""
        inicio = memoria.VRAM
        fim = memoria.VRAM_LIMITE + 1
        video = memoria.dados[inicio:fim]
        for byte in video:
            if byte == 0: 
                continue
            if 32 <= byte <= 126:
                output += chr(byte)
            elif byte == 10:
                output += '\n'
            else:
                output += '.' 
        
        if output:
            print(output)
        else:
            print("[ Sem Sinal de Vídeo ]")


class ram:
    tamanho_total = 0xA0000 
    RAM_LIMITE = 0x7FFFF
    
    VRAM        = 0x80000
    VRAM_LIMITE = 0x8FFFF

    E_S = 0x9FC00 

    def __init__(self):
        self.dados = bytearray(self.tamanho_total)

    def leia(self, endereco, num_bytes):
        if endereco + num_bytes > self.tamanho_total: return 0
        return int.from_bytes(self.dados[endereco : endereco + num_bytes], 'little')

    def escreva(self, endereco, val, num_bytes):
        if endereco + num_bytes > self.tamanho_total: return
        mascara = (1 << (num_bytes * 8)) - 1
        self.dados[endereco : endereco + num_bytes] = (val & mascara).to_bytes(num_bytes, 'little')