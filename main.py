from barramento import barramento, monitor, ram
from CPU import CPU

programa = [
    # --- INICIALIZAÇÃO ---
    0x000800b7, # LUI x1, 0x80000 (Base VRAM)
    0x00000113, # ADDI x2, x0, 0
    0x00000293, # ADDI x5, x0, 0 (i = 0)
    0x00900313, # ADDI x6, x0, 9 (Lim = 9)
    # --- LOOP START (0x10) ---
    # BEQ x5, x6, EXIT (Se i==9, vai para 0xAC)
    0x08628e63,
    # Corpo
    0x00128393, # ADDI x7, x5, 1 (a = i+1)
    0x0013f413, # ANDI x8, x7, 1 (Check Impar)
    
    # BNE x8, x0, ODD (Se impar, vai para 0x84) 
    0x06041463,
    # --- CAMINHO PAR (0x20) ---
    # Imprime 'a hey\n'
    0x03038e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    0x02000e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    0x06800e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    0x06500e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    0x07900e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    0x00a00e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    # PULO PARA NEXT (0x80)
    0x02000263,
    # --- CAMINHO IMPAR (0x84) ---
    # Imprime 'a\n'
    0x03038e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    0x00a00e13, 0x00208eb3, 0x01ce8023, 0x00110113, 
    # --- NEXT (0xA4) ---
    0x00128293, # ADDI x5, x5, 1 (i++)
    # VOLTA PARA LOOP (0xA8)
    # BEQ x0, x0, LoopStart (-152 bytes)
    # Hex correto para -152:
    0xF60004E3,
    # --- EXIT (0xAC) ---
    # "Ola Mundo"
    0x04f00e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x06c00e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x06100e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x02000e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x04d00e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x07500e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x06e00e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x06400e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    0x06f00e13, 0x00208eb3, 0x01ce8023, 0x00110113,
    # HALT
    0x00000000
]

if __name__ == "__main__":
    mem = ram()
    e_s = monitor()
    cabo = barramento(mem, e_s)
    cpu = CPU(cabo)

    print("--- Carregando Sistema ---")
    cpu.carregar_programa(programa)
    cpu.run()