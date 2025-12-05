class CPU:
    def __init__(self, barramento):
        self.barramento = barramento
        self.pc = 0x00000000
        self.regs = [0] * 32

    # Funcoes Auxiliares 
    def correcao_dsinal(self, entrada):
        entrada = entrada & 0xFFFFFFFF
        if (entrada & 0x80000000) == 0x80000000:
            return entrada - 0x100000000
        return entrada

    def correcao_dtamanho(self, entrada):
        return entrada & 0xFFFFFFFF

    def carregar_programa(self, lista_hex):
        addr = 0
        for inst in lista_hex:
            self.barramento.escreva(addr, inst, 32)
            addr += 4

    # Execucao 
    def run(self):
        ciclos = 0
        while True:
            if not self.Decoder():
                break 
            ciclos += 1
            if ciclos > 5000: 
                print("Aviso: Limite de ciclos atingido.")
                break
        self.barramento.imprimir()
        print("\n")
        print("CPU Halt (Fim do programa).")

    # Decodificador 
    def Decoder(self):
        self.regs[0] = 0 
        
        instrucao = self.barramento.leia(self.pc, 32)
        if instrucao == 0: return False 
        
        next_pc = self.pc + 4

        # Separação da entrada
        opcode = instrucao & 0x7F
        rd     = (instrucao >> 7) & 0x1F
        funct3 = (instrucao >> 12) & 0x7
        rs1    = (instrucao >> 15) & 0x1F
        rs2    = (instrucao >> 20) & 0x1F
        funct7 = (instrucao >> 25) & 0x7F

        # Imediatos (Com correção de sinal ajustada)
        # Tipo I Imediato
        imm_i = instrucao >> 20
        if imm_i & 0x800: imm_i -= 0x1000 
        # Tipo S Imediato
        imm_s = ((instrucao >> 25) << 5) | ((instrucao >> 7) & 0x1F)
        if imm_s & 0x800: imm_s -= 0x1000
        # Tipo B Imediato
        imm_b = ((instrucao >> 31) << 12) | ((instrucao & 0x7E000000) >> 20) | ((instrucao & 0xF00) >> 7) | ((instrucao & 0x80) << 4)
        if imm_b & 0x1000: imm_b -= 0x2000 
        # Tipo U Imediato
        imm_u = instrucao & 0xFFFFF000
        # Tipo J Imediato
        imm_j = ((instrucao >> 31) << 20) | (instrucao & 0xFF000) | ((instrucao & 0x100000) >> 9) | ((instrucao & 0x7FE00000) >> 20)
        if imm_j & 0x100000: imm_j -= 0x200000

        # Instrucoes - Em ordem de Opcode
        
        # Opcode 0b0000011 - Tipo I (LOAD)
        if opcode == 0x03: 
            addr = self.regs[rs1] + imm_i
        
            if funct3 == 0x0: # LB (Load Byte)
                val = self.barramento.leia(addr, 8)
                if (val & 0x80) != 0: 
                    val -= 0x100
                self.regs[rd] = self.correcao_dtamanho(val)

            elif funct3 == 0x1: # LH (Load Half - Signed)
                val = self.barramento.leia(addr, 16)
                if (val & 0x8000) != 0: 
                    val -= 0x10000
                self.regs[rd] = self.correcao_dtamanho(val)

            elif funct3 == 0x2: # LW (Load Word)
                self.regs[rd] = self.barramento.leia(addr, 32)

            elif funct3 == 0x4: # LBU (Load Byte Unsigned)
                self.regs[rd] = self.barramento.leia(addr, 8)

            elif funct3 == 0x5: # LHU (Load Half Unsigned)
                self.regs[rd] = self.barramento.leia(addr, 16)

        # Opcode 0b0010011 - Tipo I (OPERACAO IMEDIATA)
        elif opcode == 0x13: 
            val1 = self.correcao_dsinal(self.regs[rs1]) # Valor com sinal
            
            if funct3 == 0x0:   # ADDI
                self.regs[rd] = self.correcao_dtamanho(val1 + imm_i)

            elif funct3 == 0x1: # SLLI
                self.regs[rd] = self.correcao_dtamanho(val1 << (imm_i & 0x1F))

            elif funct3 == 0x2: # SLTI (Set Less Than Immediate - Signed)
                self.regs[rd] = 1 if val1 < imm_i else 0

            elif funct3 == 0x3: # SLTIU (Set Less Than Immediate Unsigned)
                if self.correcao_dtamanho(val1) < self.correcao_dtamanho(imm_i):
                    self.regs[rd] = 1
                else:
                    self.regs[rd] = 0

            elif funct3 == 0x4: # XORI
                self.regs[rd] = self.correcao_dtamanho(val1 ^ imm_i)

            elif funct3 == 0x5: # SRLI / SRAI
                shamt = imm_i & 0x1F
                if (imm_i >> 10) & 1: # SRAI (Shift Right Arithmetic)
                    self.regs[rd] = self.correcao_dtamanho(val1 >> shamt)
                else: # SRLI (Shift Right Logical)
                    self.regs[rd] = self.correcao_dtamanho(self.regs[rs1] >> shamt)

            elif funct3 == 0x6: # ORI
                self.regs[rd] = self.correcao_dtamanho(val1 | imm_i)

            elif funct3 == 0x7: # ANDI
                self.regs[rd] = self.correcao_dtamanho(val1 & imm_i)
            
        # Opcode 0b0010111 - Tipo U (CRIAR ENDERECO IMEDIATO)
        elif opcode == 0x17: # AUIPC (add upper immediate to PC)
            self.regs[rd] = self.correcao_dtamanho(self.pc + imm_u)
            
        # Opcode 0b0100011 - S-Type (ARMAZENAR)
        elif opcode == 0x23: 
            addr = self.regs[rs1] + imm_s
            if funct3 == 0x0: # SB (Store Byte)
                self.barramento.escreva(addr, self.regs[rs2] & 0xFF, 8)
            elif funct3 == 0x1: # SH (store half)
                self.barramento.escreva(addr, self.regs[rs2] & 0xFFFF, 16)
            elif funct3 == 0x2: # SW (Store Word)
                self.barramento.escreva(addr, self.regs[rs2], 32)

        # Opcode 0b0110011 - Tipo R (OPERACOES ENTRE REGISTRADORES)
        elif opcode == 0x33: 
            val1 = self.correcao_dsinal(self.regs[rs1])
            val2 = self.correcao_dsinal(self.regs[rs2])
        
            if funct3 == 0x0:
                if funct7 == 0x00:   # ADD
                    self.regs[rd] = self.correcao_dtamanho(val1 + val2) 
                elif funct7 == 0x20: # SUB
                    self.regs[rd] = self.correcao_dtamanho(val1 - val2) 
            
            elif funct3 == 0x1: # SLL (Shift Left Logical)
                shamt = val2 & 0x1F
                self.regs[rd] = self.correcao_dtamanho(val1 << shamt)
            
            elif funct3 == 0x2: # SLT (Set Less Than Signed)
                self.regs[rd] = 1 if val1 < val2 else 0
            
            elif funct3 == 0x3: # SLTU (Set Less Than Unsigned)
                u_val1 = self.correcao_dtamanho(val1)
                u_val2 = self.correcao_dtamanho(val2)
                self.regs[rd] = 1 if u_val1 < u_val2 else 0
        
            elif funct3 == 0x4: # XOR
                self.regs[rd] = self.correcao_dtamanho(val1 ^ val2)

            elif funct3 == 0x5: # SRL / SRA (Shift Right)
                shamt = val2 & 0x1F
                if funct7 == 0x20: # SRA (Arithmetic)
                    self.regs[rd] = self.correcao_dtamanho(val1 >> shamt)
                else: # SRL (Logical)
                    self.regs[rd] = self.correcao_dtamanho(self.correcao_dtamanho(val1) >> shamt)

            elif funct3 == 0x6: # OR
                self.regs[rd] = self.correcao_dtamanho(val1 | val2)

            elif funct3 == 0x7:  # AND
                self.regs[rd] = self.correcao_dtamanho(val1 & val2)
        
        # Opcode 0b0110111 - Tipo U (CARREGAR ENDERECO IMEDIATO)
        elif opcode == 0x37: # LUI
            self.regs[rd] = imm_u

        # Opcode 0x1100011 - Tipo B (ESCOLHAS)
        elif opcode == 0x63: # BRANCH
            val1 = self.correcao_dsinal(self.regs[rs1])
            val2 = self.correcao_dsinal(self.regs[rs2])
            desvio = False
            
            # Comparações com SINAL (Tratam -1 como menor que 1)
            if funct3 == 0x0: # BEQ (IGUAL)  
                desvio = (val1 == val2)
            elif funct3 == 0x1: # BNE (DIFERENTE) 
                desvio = (val1 != val2)
            elif funct3 == 0x4: # BLT (MENOR QUE)
                desvio = (val1 < val2)
            elif funct3 == 0x5: # BGE (MAIOR OU IGUAL)
                desvio = (val1 >= val2)        
            elif funct3 == 0x6: # BLTU (MAIIOR)
                desvio = (self.correcao_dtamanho(val1) < self.correcao_dtamanho(val2))
            elif funct3 == 0x7: # BGEU (MENOR OU IGUAL)
                desvio = (self.correcao_dtamanho(val1)>= self.correcao_dtamanho(val2))
            
            # Se a condição for verdadeira, atualiza o next_pc
            if desvio == True: 
                next_pc = self.pc + imm_b

        # Opcode 0x67 (1100111) - Tipo I (PULO com registrador)
        elif opcode == 0x67: # JALR
            self.regs[rd] = next_pc
            next_pc = (self.regs[rs1] + imm_i) & ~1

        # Opcode 0x6F (1101111) - Tipo J (PULO)
        elif opcode == 0x6F: # JAL
            self.regs[rd] = next_pc
            next_pc = self.pc + imm_j

        self.pc = self.correcao_dtamanho(next_pc)
        return True