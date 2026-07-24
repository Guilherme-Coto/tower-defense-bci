import scipy.io as sio

def investigar_ficheiro(caminho_ficheiro):
    print(f"A abrir: {caminho_ficheiro}...\n")
    
    # Carrega o ficheiro para a memória
    dados_mat = sio.loadmat(caminho_ficheiro)
    
    print("--- CONTEÚDO DO FICHEIRO ---")
    for chave, valor in dados_mat.items():
        # Ignorar as variáveis de sistema do MATLAB (que começam por '__')
        if not chave.startswith('__'):
            # Mostra o nome da chave e o formato dos dados (ex: matriz 64x1000)
            formato = getattr(valor, 'shape', 'Não é um array')
            print(f"Chave: '{chave}' | Tipo: {type(valor).__name__} | Tamanho/Shape: {formato}")

# Substitui pelo nome real do teu ficheiro
investigar_ficheiro("data_imputed\song21_Imputed.mat")