from figurinhas import Figurinha, Usuario


def criar_usuario_padrao(nome: str, total: int = 100) -> Usuario:
    usuario = Usuario(nome=nome, total_esperado=total)
    return usuario


def exibir_menu() -> None:
    print("\n=== Sistema de Figurinhas da Copa ===")
    print("1. Inserir figurinha no álbum")
    print("2. Remover figurinha do álbum")
    print("3. Consultar figurinha")
    print("4. Ver álbum completo")
    print("5. Ver porcentagem de conclusão")
    print("6. Ver figurinhas repetidas")
    print("7. Buscar por jogador")
    print("8. Buscar por seleção")
    print("9. Propor troca")
    print("10. Efetuar troca automática")
    print("11. Salvar usuário em JSON")
    print("12. Carregar usuário de JSON")
    print("13. Exportar para CSV")
    print("14. Exportar para TXT")
    print("15. Ver histórico de trocas")
    print("0. Sair")


def ler_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_texto(prompt: str) -> str:
    return input(prompt).strip()


def exibir_figurinhas(figurinhas: list[Figurinha]) -> None:
    if not figurinhas:
        print("Nenhuma figurinha encontrada.")
        return
    for figurinha in figurinhas:
        print(f"- {figurinha.numero}: {figurinha.jogador} / {figurinha.selecao}")


def main() -> None:
    usuario = criar_usuario_padrao("Jogador", total=100)
    outro = criar_usuario_padrao("Colega", total=100)
    print("Sistema inicializado com dois usuários de exemplo: Jogador e Colega.")

    while True:
        exibir_menu()
        opcao = ler_int("Escolha uma opção: ")

        if opcao == 0:
            print("Encerrando o sistema.")
            break

        if opcao == 1:
            numero = ler_int("Número da figurinha: ")
            jogador = ler_texto("Nome do jogador: ")
            selecao = ler_texto("Seleção: ")
            resultado = usuario.album.inserir_figurinha(Figurinha(numero, jogador, selecao))
            print("Figurinha inserida no álbum." if resultado == "inserida" else "Figurinha adicionada às repetidas.")

        elif opcao == 2:
            numero = ler_int("Número da figurinha a remover: ")
            removida = usuario.album.remover_figurinha(numero)
            if removida:
                print(f"Removida: {removida.numero} - {removida.jogador} / {removida.selecao}")
            else:
                print("Figurinha não encontrada no álbum.")

        elif opcao == 3:
            numero = ler_int("Número da figurinha a consultar: ")
            figurinha = usuario.album.consultar_por_numero(numero)
            if figurinha:
                print(f"{figurinha.numero}: {figurinha.jogador} / {figurinha.selecao}")
            else:
                print("Figurinha não encontrada no álbum.")

        elif opcao == 4:
            print("Álbum completo:")
            exibir_figurinhas(usuario.album.listar_album())

        elif opcao == 5:
            print(f"Conclusão do álbum: {usuario.album.porcentagem_conclusao()}%")

        elif opcao == 6:
            print("Figurinhas repetidas:")
            exibir_figurinhas(usuario.album.listar_repetidas())

        elif opcao == 7:
            jogador = ler_texto("Nome do jogador para busca: ")
            resultados = usuario.album.buscar_por_jogador(jogador).to_list()
            exibir_figurinhas(resultados)

        elif opcao == 8:
            selecao = ler_texto("Seleção para busca: ")
            resultados = usuario.album.buscar_por_selecao(selecao).to_list()
            exibir_figurinhas(resultados)

        elif opcao == 9:
            print("Propondo troca com 'Colega'.")
            meu_numero = ler_int("Número da figurinha repetida para oferecer: ")
            numero_desejado = ler_int("Número da figurinha repetida desejada do Colega: ")
            sucesso, mensagem = usuario.propor_troca(outro, meu_numero, numero_desejado)
            print(mensagem)

        elif opcao == 10:
            sucesso, mensagem = usuario.troca_automatica(outro)
            print(mensagem)

        elif opcao == 11:
            caminho = ler_texto("Caminho de saída JSON: ")
            usuario.salvar_json(caminho)
            print("Dados salvos em JSON com sucesso.")

        elif opcao == 12:
            caminho = ler_texto("Caminho do arquivo JSON: ")
            try:
                usuario = Usuario.carregar_json(caminho)
                print("Usuário carregado com sucesso.")
            except Exception as erro:
                print(f"Falha ao carregar JSON: {erro}")

        elif opcao == 13:
            caminho = ler_texto("Caminho do arquivo CSV: ")
            usuario.exportar_csv(caminho)
            print("Exportado para CSV com sucesso.")

        elif opcao == 14:
            caminho = ler_texto("Caminho do arquivo TXT: ")
            usuario.exportar_txt(caminho)
            print("Exportado para TXT com sucesso.")

        elif opcao == 15:
            eventos = usuario.historico.listar()
            if not eventos:
                print("Nenhum evento de troca registrado.")
            else:
                for evento in eventos:
                    print(f"{evento.data_hora}: {evento.mensagem} (de {evento.origem} para {evento.destino})")

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
