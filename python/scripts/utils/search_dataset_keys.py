import scipy.io as sio

#esta função descobre as chaves de um dado dataset
def search_file(caminho_ficheiro):
    print(f"A abrir: {caminho_ficheiro}...\n")
    
    #carrega o ficheiro para a memória
    dados_mat = sio.loadmat(caminho_ficheiro)
    
    print("--- CONTEÚDO DO FICHEIRO ---")
    for chave, valor in dados_mat.items():
        #jgnorar as variáveis de sistema do MATLAB 
        if not chave.startswith('__'):
            #mostra o nome da chave e o formato dos dados
            formato = getattr(valor, 'shape', 'Não é um array')
            print(f"Chave: '{chave}' | Tipo: {type(valor).__name__} | Tamanho/Shape: {formato}")

#colocar aqui o nome real do ficheiro
search_file("data_imputed\song21_Imputed.mat")