from __future__ import annotations
import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Callable, Generator, Optional, Any


@dataclass
class Figurinha:
    numero: int
    jogador: str
    selecao: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "numero": self.numero,
            "jogador": self.jogador,
            "selecao": self.selecao,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Figurinha:
        return cls(
            numero=int(data["numero"]),
            jogador=str(data["jogador"]),
            selecao=str(data["selecao"]),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Figurinha):
            return False
        return self.numero == other.numero and self.selecao == other.selecao

    def __repr__(self) -> str:
        return f"Figurinha(numero={self.numero}, jogador='{self.jogador}', selecao='{self.selecao}')"


class NodoLista:
    def __init__(self, data: Any, proximo: Optional[NodoLista] = None) -> None:
        self.data = data
        self.proximo = proximo


class ListaEncadeada:
    def __init__(self) -> None:
        self.cabeca: Optional[NodoLista] = None
        self.tamanho = 0

    def append(self, data: Any) -> None:
        novo = NodoLista(data)
        if self.cabeca is None:
            self.cabeca = novo
        else:
            atual = self.cabeca
            while atual.proximo is not None:
                atual = atual.proximo
            atual.proximo = novo
        self.tamanho += 1

    def remove(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        atual = self.cabeca
        anterior = None
        while atual is not None:
            if predicate(atual.data):
                if anterior is None:
                    self.cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                self.tamanho -= 1
                return atual.data
            anterior = atual
            atual = atual.proximo
        return None

    def find(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        atual = self.cabeca
        while atual is not None:
            if predicate(atual.data):
                return atual.data
            atual = atual.proximo
        return None

    def __iter__(self) -> Generator[Any, None, None]:
        atual = self.cabeca
        while atual is not None:
            yield atual.data
            atual = atual.proximo

    def count(self) -> int:
        return self.tamanho

    def to_list(self) -> list[Any]:
        resultado: list[Any] = []
        atual = self.cabeca
        while atual is not None:
            resultado.append(atual.data)
            atual = atual.proximo
        return resultado

    def clear(self) -> None:
        self.cabeca = None
        self.tamanho = 0

    def filter(self, predicate: Callable[[Any], bool]) -> ListaEncadeada:
        resultado = ListaEncadeada()
        atual = self.cabeca
        while atual is not None:
            if predicate(atual.data):
                resultado.append(atual.data)
            atual = atual.proximo
        return resultado


class NodoFila:
    def __init__(self, data: Any, proximo: Optional[NodoFila] = None) -> None:
        self.data = data
        self.proximo = proximo


class Fila:
    def __init__(self) -> None:
        self.frente: Optional[NodoFila] = None
        self.tras: Optional[NodoFila] = None
        self.tamanho = 0

    def enqueue(self, data: Any) -> None:
        novo = NodoFila(data)
        if self.tras is None:
            self.frente = novo
            self.tras = novo
        else:
            self.tras.proximo = novo
            self.tras = novo
        self.tamanho += 1

    def dequeue(self) -> Optional[Any]:
        if self.frente is None:
            return None
        item = self.frente.data
        self.frente = self.frente.proximo
        if self.frente is None:
            self.tras = None
        self.tamanho -= 1
        return item

    def is_empty(self) -> bool:
        return self.frente is None

    def __iter__(self) -> Generator[Any, None, None]:
        atual = self.frente
        while atual is not None:
            yield atual.data
            atual = atual.proximo

    def count(self) -> int:
        return self.tamanho

    def to_list(self) -> list[Any]:
        resultado: list[Any] = []
        atual = self.frente
        while atual is not None:
            resultado.append(atual.data)
            atual = atual.proximo
        return resultado


@dataclass
class TradeEvent:
    origem: str
    destino: str
    figurinha_oferecida: Figurinha
    figurinha_recebida: Figurinha
    sucesso: bool
    mensagem: str
    data_hora: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "origem": self.origem,
            "destino": self.destino,
            "figurinha_oferecida": self.figurinha_oferecida.to_dict(),
            "figurinha_recebida": self.figurinha_recebida.to_dict(),
            "sucesso": self.sucesso,
            "mensagem": self.mensagem,
            "data_hora": self.data_hora,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TradeEvent:
        return cls(
            origem=data["origem"],
            destino=data["destino"],
            figurinha_oferecida=Figurinha.from_dict(data["figurinha_oferecida"]),
            figurinha_recebida=Figurinha.from_dict(data["figurinha_recebida"]),
            sucesso=bool(data["sucesso"]),
            mensagem=str(data["mensagem"]),
            data_hora=str(data["data_hora"]),
        )


class Historico:
    def __init__(self) -> None:
        self.eventos = Fila()

    def registrar(self, evento: TradeEvent) -> None:
        self.eventos.enqueue(evento)

    def listar(self) -> list[TradeEvent]:
        return self.eventos.to_list()

    def to_list(self) -> list[dict[str, Any]]:
        return [evento.to_dict() for evento in self.eventos]

    @classmethod
    def from_list(cls, eventos: list[dict[str, Any]]) -> Historico:
        historico = cls()
        for evento in eventos:
            historico.registrar(TradeEvent.from_dict(evento))
        return historico


class Album:
    def __init__(self, total_esperado: int = 100) -> None:
        self.total_esperado = total_esperado
        self.figurinhas = ListaEncadeada()
        self.repetidas = ListaEncadeada()

    def inserir_figurinha(self, figurinha: Figurinha) -> str:
        if self.has_figurinha_numero(figurinha.numero):
            self.repetidas.append(figurinha)
            return "repetida"

        self.figurinhas.append(figurinha)
        return "inserida"

    def remover_figurinha(self, numero: int) -> Optional[Figurinha]:
        return self.figurinhas.remove(lambda item: item.numero == numero)

    def consultar_por_numero(self, numero: int) -> Optional[Figurinha]:
        return self.figurinhas.find(lambda item: item.numero == numero)

    def buscar_por_jogador(self, jogador: str) -> ListaEncadeada:
        return self.figurinhas.filter(lambda item: item.jogador.lower() == jogador.lower())

    def buscar_por_selecao(self, selecao: str) -> ListaEncadeada:
        return self.figurinhas.filter(lambda item: item.selecao.lower() == selecao.lower())

    def listar_album(self) -> list[Figurinha]:
        return self.figurinhas.to_list()

    def listar_repetidas(self) -> list[Figurinha]:
        return self.repetidas.to_list()

    def contador_repetidas(self) -> int:
        return self.repetidas.count()

    def has_figurinha_numero(self, numero: int) -> bool:
        return self.figurinhas.find(lambda item: item.numero == numero) is not None

    def tem_repetida_numero(self, numero: int) -> bool:
        return self.repetidas.find(lambda item: item.numero == numero) is not None

    def remover_repetida(self, numero: int) -> Optional[Figurinha]:
        return self.repetidas.remove(lambda item: item.numero == numero)

    def porcentagem_conclusao(self) -> float:
        if self.total_esperado <= 0:
            return 0.0
        concluido = self.figurinhas.count()
        return round((concluido / self.total_esperado) * 100, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_esperado": self.total_esperado,
            "figurinhas": [item.to_dict() for item in self.figurinhas],
            "repetidas": [item.to_dict() for item in self.repetidas],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Album:
        album = cls(total_esperado=int(data.get("total_esperado", 100)))
        for item in data.get("figurinhas", []):
            album.inserir_figurinha(Figurinha.from_dict(item))
        for item in data.get("repetidas", []):
            album.repetidas.append(Figurinha.from_dict(item))
        return album

    def export_csv(self, filepath: str) -> None:
        with open(filepath, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["tipo", "numero", "jogador", "selecao"])
            for fig in self.figurinhas:
                escritor.writerow(["album", fig.numero, fig.jogador, fig.selecao])
            for fig in self.repetidas:
                escritor.writerow(["repetida", fig.numero, fig.jogador, fig.selecao])

    def export_txt(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as arquivo:
            arquivo.write(f"Álbum - {self.figurinhas.count()} figurinhas\n")
            arquivo.write(f"Repetidas - {self.repetidas.count()} figurinhas\n\n")
            arquivo.write("Figurinhas no álbum:\n")
            for fig in self.figurinhas:
                arquivo.write(f"{fig.numero}: {fig.jogador} / {fig.selecao}\n")
            arquivo.write("\nFigurinhas repetidas:\n")
            for fig in self.repetidas:
                arquivo.write(f"{fig.numero}: {fig.jogador} / {fig.selecao}\n")


class Usuario:
    def __init__(self, nome: str, total_esperado: int = 100) -> None:
        self.nome = nome
        self.album = Album(total_esperado=total_esperado)
        self.historico = Historico()

    def propor_troca(self, outro: Usuario, meu_numero: int, numero_desejado: int) -> tuple[bool, str]:
        if meu_numero == numero_desejado:
            return False, "Os números devem ser diferentes para uma troca."

        minha_repetida = self.album.remover_repetida(meu_numero)
        repetida_outro = outro.album.remover_repetida(numero_desejado)
        if minha_repetida is None or repetida_outro is None:
            if minha_repetida is not None:
                self.album.repetidas.append(minha_repetida)
            if repetida_outro is not None:
                outro.album.repetidas.append(repetida_outro)
            return False, "Troca não possível: uma das partes não tem a figurinha repetida solicitada."

        if self.album.has_figurinha_numero(numero_desejado):
            outro.album.repetidas.append(repetida_outro)
            self.album.repetidas.append(minha_repetida)
            return False, "Você já possui a figurinha desejada no álbum."
        if outro.album.has_figurinha_numero(meu_numero):
            self.album.repetidas.append(minha_repetida)
            outro.album.repetidas.append(repetida_outro)
            return False, "A outra pessoa já possui sua figurinha no álbum."

        self.album.inserir_figurinha(repetida_outro)
        outro.album.inserir_figurinha(minha_repetida)

        evento = TradeEvent(
            origem=self.nome,
            destino=outro.nome,
            figurinha_oferecida=minha_repetida,
            figurinha_recebida=repetida_outro,
            sucesso=True,
            mensagem=f"Troca automática realizada: {minha_repetida.numero} por {repetida_outro.numero}",
            data_hora=datetime.now().isoformat(timespec="seconds"),
        )
        self.historico.registrar(evento)
        outro.historico.registrar(evento)
        return True, evento.mensagem

    def troca_automatica(self, outro: Usuario) -> tuple[bool, str]:
        meu_atual = self.album.repetidas.cabeca
        while meu_atual is not None:
            outra_atual = outro.album.repetidas.cabeca
            while outra_atual is not None:
                if not self.album.has_figurinha_numero(outra_atual.data.numero) and not outro.album.has_figurinha_numero(meu_atual.data.numero):
                    minha_repetida = self.album.remover_repetida(meu_atual.data.numero)
                    repetida_outro = outro.album.remover_repetida(outra_atual.data.numero)
                    if minha_repetida and repetida_outro:
                        self.album.inserir_figurinha(repetida_outro)
                        outro.album.inserir_figurinha(minha_repetida)
                        evento = TradeEvent(
                            origem=self.nome,
                            destino=outro.nome,
                            figurinha_oferecida=minha_repetida,
                            figurinha_recebida=repetida_outro,
                            sucesso=True,
                            mensagem=f"Troca automática efetuada: {minha_repetida.numero} por {repetida_outro.numero}",
                            data_hora=datetime.now().isoformat(timespec="seconds"),
                        )
                        self.historico.registrar(evento)
                        outro.historico.registrar(evento)
                        return True, evento.mensagem
                outra_atual = outra_atual.proximo
            meu_atual = meu_atual.proximo
        return False, "Nenhuma troca automática possível entre os dois usuários."

    def to_dict(self) -> dict[str, Any]:
        return {
            "nome": self.nome,
            "album": self.album.to_dict(),
            "historico": self.historico.to_list(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Usuario:
        user = cls(nome=data["nome"], total_esperado=int(data["album"].get("total_esperado", 100)))
        user.album = Album.from_dict(data["album"])
        user.historico = Historico.from_list(data.get("historico", []))
        return user

    def salvar_json(self, caminho: str) -> None:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(self.to_dict(), arquivo, indent=2, ensure_ascii=False)

    @classmethod
    def carregar_json(cls, caminho: str) -> Usuario:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return cls.from_dict(dados)

    def exportar_csv(self, caminho: str) -> None:
        with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["usuario", "tipo", "numero", "jogador", "selecao"])
            for fig in self.album.figurinhas:
                escritor.writerow([self.nome, "album", fig.numero, fig.jogador, fig.selecao])
            for fig in self.album.repetidas:
                escritor.writerow([self.nome, "repetida", fig.numero, fig.jogador, fig.selecao])

    def exportar_txt(self, caminho: str) -> None:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(f"Usuário: {self.nome}\n")
            arquivo.write(f"Figurinhas no álbum: {self.album.figurinhas.count()}\n")
            arquivo.write(f"Repetidas: {self.album.repetidas.count()}\n")
            arquivo.write(f"Conclusão: {self.album.porcentagem_conclusao()}%\n\n")
            arquivo.write("Álbum:\n")
            for fig in self.album.figurinhas:
                arquivo.write(f"{fig.numero}: {fig.jogador} / {fig.selecao}\n")
            arquivo.write("\nRepetidas:\n")
            for fig in self.album.repetidas:
                arquivo.write(f"{fig.numero}: {fig.jogador} / {fig.selecao}\n")
