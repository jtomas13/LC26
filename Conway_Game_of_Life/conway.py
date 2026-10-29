import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import z3

    print("Z3 disponível")
    print(z3.get_version_string())
    return (z3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## TP2 - Conway's Game of Life
    ## Introdução

    O Conway's Game of Life é um autómato celular no qual cada célula de uma grelha pode estar viva ou morta. A evolução do sistema é determinada pelo estado das células vizinhas, seguindo regras de nascimento, sobrevivência e morte.

    Neste trabalho é considerada uma versão modificada do autómato, com uma grelha de dimensão finita e células adicionais nas fronteiras, cujos valores permanecem constantes.

    O problema será modelado através de uma Máquina de Estados Finita (FSM), permitindo representar a evolução do sistema e verificar propriedades do seu comportamento.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Objetivo

    O objetivo deste trabalho é construir uma FSM que represente o funcionamento do Conway's Game of Life modificado, considerando duas modalidades de transição:

    - **Atualização individual:** em cada transição é atualizada uma única célula normal.
    - **Atualização simultânea:** em cada transição são atualizadas todas as células normais.

    Pretende-se também verificar duas propriedades:

    1. Se o sistema pode alcançar um estado em que todas as células normais estão mortas.
    2. Se alguma célula normal pode permanecer definitivamente viva ou morta.

    A verificação deverá permitir demonstrar as propriedades ou apresentar contraexemplos quando estas não se verificam.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Abordagem

    A implementação será desenvolvida em Python, utilizando o Z3 para representar simbolicamente os estados e as relações de transição do autómato.

    Cada célula normal será representada por uma variável booleana. As células adicionais das fronteiras terão valores constantes durante a evolução do sistema.

    A FSM será definida através de:

    - Um conjunto de variáveis que representam os estados das células.
    - Um predicado que caracteriza os estados iniciais.
    - Uma relação de transição que determina as mudanças de estado segundo a regra B3/S23.

    As duas modalidades de transição serão selecionadas através de um parâmetro.

    Para analisar as propriedades pedidas, serão utilizadas técnicas de verificação de modelos baseadas em SAT/SMT, permitindo procurar estados alcançáveis que violem as propriedades e, quando possível, demonstrar a sua validade.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A1 - Representação dos estados

    O espaço de estados do autómato é constituído por uma grelha de dimensão `N × N`, com `N > 16`, onde cada célula normal pode assumir um de dois valores:

    - `0` — célula morta;
    - `1` — célula viva.

    No estado inicial, todas as células normais estão mortas, exceto as que pertencem ao bloco `3 × 3` situado no canto superior esquerdo.

    Para representar a configuração inicial é utilizada uma matriz de listas Python. A dimensão `N` é parametrizável, começando-se com `N = 17`, o menor valor permitido pelo enunciado.

    Na implementação, os índices das listas começam em `0`, pelo que as células inicialmente vivas correspondem às posições `0 ≤ i < 3` e `0 ≤ j < 3`.
    """)
    return


@app.cell
def _():
    N = 17

    grelha = [
        [1 if i < 3 and j < 3 else 0 for j in range(N)]
        for i in range(N)
    ]

    for linha in grelha:
        print(" ".join(map(str, linha)))
    return N, grelha


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Teste da configuração inicial

    É verificado que:

    - a grelha possui exatamente `N` linhas e `N` colunas;
    - existem exatamente 9 células inicialmente vivas;
    - todas as restantes células normais estão mortas.

    Este teste permite confirmar que a configuração inicial respeita as condições definidas para o autómato.
    """)
    return


@app.cell
def _(N, grelha):
    assert len(grelha) == N
    assert all(len(linha) == N for linha in grelha)

    total_vivas = sum(sum(linha) for linha in grelha)

    assert total_vivas == 9

    for i in range(N):
        for j in range(N):
            esperado = 1 if i < 3 and j < 3 else 0
            assert grelha[i][j] == esperado

    print("Configuração inicial validada.")
    print("Dimensão:", N, "x", N)
    print("Células vivas:", total_vivas)
    print("Células mortas:", N * N - total_vivas)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A2 — Células de fronteira

    Além das `N²` células normais, o autómato possui dois conjuntos de células adicionais:

    - **Células iniciais:** `2N + 1` células situadas na linha `0` ou na coluna `0`. Os seus valores são gerados aleatoriamente, com probabilidade `1/2` de estarem vivas, e permanecem constantes durante a evolução.
    - **Células finais:** `2N + 3` células situadas na linha `N + 1` ou na coluna `N + 1`, excluindo as células iniciais. Estas permanecem sempre mortas.

    As células de fronteira influenciam o número de vizinhos vivos das células normais próximas das extremidades.

    Para garantir a reprodução dos testes, será utilizada uma semente fixa na geração aleatória das células iniciais.
    """)
    return


@app.cell
def _(N):
    import random

    rng = random.Random(42)

    iniciais = {
        (i, j): rng.randint(0, 1)
        for i in range(N + 1)
        for j in range(N + 1)
        if i == 0 or j == 0
    }

    finais = {
        (i, j): 0
        for i in range(N + 2)
        for j in range(N + 2)
        if i == N + 1 or j == N + 1
    }

    print("Células iniciais:", len(iniciais))
    print("Células finais:", len(finais))
    return finais, iniciais, random


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Teste das células de fronteira

    É verificado que:

    - existem exatamente `2N + 1` células iniciais;
    - existem exatamente `2N + 3` células finais;
    - todas as células finais estão mortas;
    - nenhuma célula pertence simultaneamente aos dois conjuntos.

    A geração aleatória das células iniciais utiliza uma semente fixa para permitir reproduzir os resultados.
    """)
    return


@app.cell
def _(N, finais, iniciais):
    assert len(iniciais) == 2 * N + 1
    assert len(finais) == 2 * N + 3

    assert all(valor == 0 for valor in finais.values())

    assert set(iniciais).isdisjoint(set(finais))

    assert all(valor in (0, 1) for valor in iniciais.values())

    print("Células de fronteira validadas.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A3 — Definição da vizinhança e regra B3/S23

    ### Definição da vizinhança

    Cada célula normal pode ter até 8 vizinhos, considerando as posições horizontais, verticais e diagonais.

    Duas células `(i0, j0)` e `(i1, j1)` são consideradas vizinhas quando:

    $$
    \max(|i_0-i_1|, |j_0-j_1|)=1
    $$

    A função `vizinhos` recebe as coordenadas de uma célula e devolve as posições dos seus 8 vizinhos.

    Para obter o estado de cada vizinho, é utilizada a função `valor_celula`, que distingue entre células normais, iniciais e finais.

    A função `contar_vizinhos_vivos` utiliza estas duas funções para determinar quantos vizinhos de uma célula estão vivos.
    """)
    return


@app.cell
def _():
    def vizinhos(i, j):
        return [
            (i + di, j + dj)
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if (di, dj) != (0, 0)
        ]


    def valor_celula(i, j, grelha, iniciais, finais):
        # Células iniciais
        if (i, j) in iniciais:
            return iniciais[(i, j)]

        # Células finais
        if (i, j) in finais:
            return finais[(i, j)]

        # Células normais
        n = len(grelha)

        if 1 <= i <= n and 1 <= j <= n:
            return grelha[i - 1][j - 1]

        raise ValueError("Coordenadas fora da grelha")


    def contar_vizinhos_vivos(i, j, grelha, iniciais, finais):
        return sum(
            valor_celula(vi, vj, grelha, iniciais, finais)
            for vi, vj in vizinhos(i, j)
        )

    return contar_vizinhos_vivos, vizinhos


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Regra de evolução B3/S23

    A evolução das células normais segue a regra B3/S23 do Conway's Game of Life.

    O estado seguinte de cada célula depende do seu estado atual e do número de vizinhos vivos:

    - **Nascimento (B3):** uma célula morta passa a viva quando possui exatamente 3 vizinhos vivos.
    - **Sobrevivência (S23):** uma célula viva mantém-se viva quando possui 2 ou 3 vizinhos vivos.
    - **Morte:** nos restantes casos, a célula fica morta.

    A função `regra_b3_s23` implementa estas condições e devolve `1` se a célula estiver viva no estado seguinte ou `0` se estiver morta.
    """)
    return


@app.function
def regra_b3_s23(atual, vivos):
    # Nascimento
    if atual == 0 and vivos == 3:
        return 1

    # Sobrevivência
    if atual == 1 and vivos in (2, 3):
        return 1

    # Morte ou permanência no estado morto
    return 0


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Testes da vizinhança e da regra B3/S23

    São realizados testes para verificar:

    - que cada célula normal possui exatamente 8 posições vizinhas;
    - que a vizinhança da célula `(1, 1)` inclui corretamente as células da fronteira;
    - que a contagem de vizinhos vivos considera tanto células normais como células iniciais;
    - que uma região sem células vivas apresenta uma contagem igual a zero;
    - que a regra B3/S23 produz os resultados esperados para todos os números possíveis de vizinhos vivos.

    Estes testes permitem validar as funções que serão utilizadas posteriormente na construção da relação de transição da FSM.
    """)
    return


@app.cell
def _(contar_vizinhos_vivos, finais, grelha, iniciais, vizinhos):
    # Testar a vizinhança
    vizinhos_teste = vizinhos(1, 1)

    assert len(vizinhos_teste) == 8

    assert set(vizinhos_teste) == {
        (0, 0), (0, 1), (0, 2),
        (1, 0),         (1, 2),
        (2, 0), (2, 1), (2, 2)
    }

    print("Vizinhança validada.")


    # Testar a contagem de vizinhos vivos
    contagem_esperada = 3 + sum(
        iniciais[pos]
        for pos in [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)]
    )

    assert contar_vizinhos_vivos(
        1, 1, grelha, iniciais, finais
    ) == contagem_esperada

    assert contar_vizinhos_vivos(
        5, 5, grelha, iniciais, finais
    ) == 0

    print("Contagem de vizinhos vivos validada.")


    # Testar todas as possibilidades da regra B3/S23
    for numero_vivos in range(9):
        assert regra_b3_s23(0, numero_vivos) == int(
            numero_vivos == 3
        )

        assert regra_b3_s23(1, numero_vivos) == int(
            numero_vivos in (2, 3)
        )

    print("Regra B3/S23 validada.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A4 — Construção da máquina de estados finita (FSM)

    ### Representação simbólica dos estados

    O autómato é modelado através de uma Máquina de Estados Finita (FSM), definida por:

    $$
    \Sigma = (Q, I, T)
    $$

    onde:

    - `Q` representa o espaço de estados;
    - `I` representa o conjunto de estados iniciais;
    - `T` representa a relação de transição entre estados.

    Cada célula normal é representada por uma variável booleana do Z3, que indica se está viva (`True`) ou morta (`False`).

    Para representar uma transição, são criados dois conjuntos de variáveis:

    - `estado0`: valores das células antes da transição;
    - `estado1`: valores das células depois da transição.

    As células iniciais da fronteira são representadas por variáveis booleanas simbólicas, permitindo considerar todas as configurações iniciais possíveis.

    As células finais são representadas pela constante booleana `False`, uma vez que permanecem sempre mortas.

    As variáveis de fronteira são partilhadas entre os diferentes estados, garantindo que os seus valores permanecem constantes.
    """)
    return


@app.cell
def _(N, finais, iniciais, z3):
    def criar_estado_z3(n, instante):
        return {
            (i, j): z3.Bool(f"x_{instante}_{i}_{j}")
            for i in range(1, n + 1)
            for j in range(1, n + 1)
        }


    # Estados antes e depois de uma transição
    estado0 = criar_estado_z3(N, 0)
    estado1 = criar_estado_z3(N, 1)

    # Fronteira inicial simbólica
    borda_inicial_z3 = {
        (i, j): z3.Bool(f"b_{i}_{j}")
        for i, j in iniciais
    }

    # Fronteira final permanentemente morta
    borda_final_z3 = {
        pos: z3.BoolVal(False)
        for pos in finais
    }

    print("Variáveis normais por estado:", len(estado0))
    print("Variáveis da fronteira inicial:", len(borda_inicial_z3))
    print("Células finais constantes:", len(borda_final_z3))
    return borda_final_z3, borda_inicial_z3, criar_estado_z3, estado0, estado1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Definição dos estados iniciais

    No estado inicial, apenas as 9 células normais situadas nas posições `1 ≤ i ≤ 3` e `1 ≤ j ≤ 3` estão vivas.

    Todas as restantes células normais encontram-se mortas.

    O predicado `predicado_inicial` representa estas condições através de uma conjunção de restrições booleanas.

    As células da fronteira inicial não são fixadas pelo predicado, permitindo que o Z3 considere qualquer combinação dos seus valores.

    Esta representação corresponde ao conjunto de configurações iniciais possíveis, independentemente de uma realização aleatória concreta.
    """)
    return


@app.cell
def _(z3):
    def predicado_inicial(estado, n):
        restricoes = []

        for i in range(1, n + 1):
            for j in range(1, n + 1):

                if i <= 3 and j <= 3:
                    restricoes.append(estado[(i, j)])

                else:
                    restricoes.append(z3.Not(estado[(i, j)]))

        return z3.And(*restricoes)

    return (predicado_inicial,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Teste do predicado inicial

    É utilizado o Z3 para verificar se existe uma atribuição de valores que satisfaz todas as condições iniciais.

    Um resultado `sat` indica que o conjunto de restrições é satisfazível.

    Também é verificado que as 9 células inicialmente vivas são obrigatoriamente verdadeiras e que as restantes células normais são obrigatoriamente falsas.
    """)
    return


@app.cell
def _(N, estado0, predicado_inicial, z3):
    teste_inicial_z3 = z3.Solver()

    teste_inicial_z3.add(
        predicado_inicial(estado0, N)
    )

    assert teste_inicial_z3.check() == z3.sat

    _modelo_inicial = teste_inicial_z3.model()

    for _i in range(1, N + 1):
        for _j in range(1, N + 1):

            _valor = _modelo_inicial.eval(
                estado0[(_i, _j)],
                model_completion=True
            )

            _esperado = _i <= 3 and _j <= 3

            assert z3.is_true(_valor) == _esperado

    print("Predicado inicial validado.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Relação de transição

    A relação de transição determina os valores das células no estado seguinte de acordo com a regra B3/S23.

    Para cada célula normal, o número de vizinhos vivos é calculado simbolicamente através do Z3.

    O estado seguinte da célula é definido pela expressão:

    $$
    x'_{i,j} \leftrightarrow
    (v_{i,j}=3)\lor(x_{i,j}\land v_{i,j}=2)
    $$

    onde `v` representa o número de vizinhos vivos.

    São consideradas duas modalidades de atualização:

    - **Individual:** é selecionada uma célula normal para aplicar a regra B3/S23. Todas as outras mantêm o seu valor.
    - **Simultânea:** todas as células normais aplicam a regra B3/S23, utilizando os valores do estado anterior.

    A modalidade é determinada pelo parâmetro `modo` da função `transicao_z3`.

    Na atualização individual, a variável `escolhida` identifica a célula selecionada. A seleção de uma célula não obriga a que o seu valor mude, caso a regra B3/S23 determine a manutenção do estado.
    """)
    return


@app.cell
def _(vizinhos, z3):
    def valor_simbolico_z3(pos, estado, borda_inicial, borda_final):

        if pos in estado:
            return estado[pos]

        if pos in borda_inicial:
            return borda_inicial[pos]

        if pos in borda_final:
            return borda_final[pos]

        raise ValueError("Coordenadas inválidas")


    def regra_simbolica_z3(i, j, estado, borda_inicial, borda_final):

        vivos = z3.Sum([
            z3.If(
                valor_simbolico_z3(
                    pos, estado, borda_inicial, borda_final
                ),
                1,
                0
            )
            for pos in vizinhos(i, j)
        ])

        return z3.Or(
            vivos == 3,
            z3.And(estado[(i, j)], vivos == 2)
        )


    def transicao_z3(
        antes, depois, borda_inicial, borda_final,
        n, modo, escolhida=None
    ):

        if modo not in ("individual", "simultanea"):
            raise ValueError("Modalidade inválida")

        restricoes = []

        if modo == "individual":

            if escolhida is None:
                raise ValueError("É necessária uma célula escolhida")

            restricoes.extend([
                escolhida >= 0,
                escolhida < n * n
            ])

        for i in range(1, n + 1):
            for j in range(1, n + 1):

                novo_valor = regra_simbolica_z3(
                    i, j, antes, borda_inicial, borda_final
                )

                if modo == "individual":

                    indice = (i - 1) * n + (j - 1)

                    valor_seguinte = z3.If(
                        escolhida == indice,
                        novo_valor,
                        antes[(i, j)]
                    )

                else:
                    valor_seguinte = novo_valor

                restricoes.append(
                    depois[(i, j)] == valor_seguinte
                )

        return z3.And(*restricoes)

    return (transicao_z3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Testes das relações de transição

    São realizados testes para as duas modalidades de transição.

    Primeiro, verifica-se que existe pelo menos um estado seguinte válido a partir de um estado inicial.

    Na modalidade individual, é verificado que uma célula não selecionada mantém obrigatoriamente o seu valor.

    Na modalidade simultânea, é verificado que a célula `(2, 2)`, inicialmente viva e com 8 vizinhos vivos, fica obrigatoriamente morta no estado seguinte.

    Estes testes utilizam o Z3 para procurar violações das restrições definidas.
    """)
    return


@app.cell
def _(
    N,
    borda_final_z3,
    borda_inicial_z3,
    estado0,
    estado1,
    predicado_inicial,
    transicao_z3,
    z3,
):
    # Teste da atualização simultânea

    teste_simultaneo = z3.Solver()

    teste_simultaneo.add(
        predicado_inicial(estado0, N)
    )

    teste_simultaneo.add(
        transicao_z3(
            estado0, estado1,
            borda_inicial_z3, borda_final_z3,
            N, "simultanea"
        )
    )

    assert teste_simultaneo.check() == z3.sat

    # A célula (2,2) tem 8 vizinhos vivos e deve morrer
    teste_simultaneo.push()

    teste_simultaneo.add(estado1[(2, 2)])

    assert teste_simultaneo.check() == z3.unsat

    teste_simultaneo.pop()

    print("Atualização simultânea validada.")


    # Teste da atualização individual

    escolhida_teste = z3.Int("escolhida_teste")

    teste_individual = z3.Solver()

    teste_individual.add(
        predicado_inicial(estado0, N)
    )

    teste_individual.add(
        transicao_z3(
            estado0, estado1,
            borda_inicial_z3, borda_final_z3,
            N, "individual", escolhida_teste
        )
    )

    assert teste_individual.check() == z3.sat

    # Selecionar apenas a célula (1,1)
    teste_individual.push()

    teste_individual.add(escolhida_teste == 0)

    # Tentar alterar uma célula não selecionada
    teste_individual.add(
        estado1[(2, 2)] != estado0[(2, 2)]
    )

    assert teste_individual.check() == z3.unsat

    teste_individual.pop()

    print("Atualização individual validada.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## B1 — Alcançabilidade do estado de erro

    O enunciado define como estado de erro qualquer configuração em que todas as células normais estão mortas.

    Este estado é representado pelo predicado:

    $$
    E(s)=\bigwedge_{i=1}^{N}\bigwedge_{j=1}^{N}\neg x_{i,j}
    $$

    Pretende-se verificar a propriedade de segurança:

    $$
    G\neg E
    $$

    Isto significa que, em qualquer execução do autómato, o estado de erro nunca deve ser alcançado.

    Para verificar a propriedade, procura-se uma sequência de transições que parta de um estado inicial válido e termine num estado de erro.

    Se essa sequência existir, constitui um contraexemplo à propriedade.
    """)
    return


@app.cell
def _(z3):
    def predicado_erro(estado):
        return z3.And(*[
            z3.Not(celula)
            for celula in estado.values()
        ])

    return (predicado_erro,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Teste do estado de erro

    Antes de analisar as transições, verifica-se que o estado inicial não é um estado de erro.

    O Z3 deve devolver `unsat` para a conjunção do predicado inicial com o predicado de erro, uma vez que existem obrigatoriamente 9 células normais vivas.
    """)
    return


@app.cell
def _(N, estado0, predicado_erro, predicado_inicial, z3):
    teste_erro_inicial = z3.Solver()

    teste_erro_inicial.add(
        predicado_inicial(estado0, N)
    )

    teste_erro_inicial.add(
        predicado_erro(estado0)
    )

    assert teste_erro_inicial.check() == z3.unsat

    print("O estado inicial não é um estado de erro.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Contraexemplo — Atualização individual

    Na modalidade de atualização individual, é possível alcançar o estado de erro.

    Para demonstrar esta situação, considera-se uma configuração válida em que todas as células iniciais da fronteira estão mortas.

    Parte-se do bloco inicial de 9 células vivas e atualizam-se sucessivamente as posições:

    `(1,2), (2,1), (1,1), (2,3), (2,2), (1,3), (3,1), (3,2), (3,3)`

    Nesta sequência, cada atualização provoca a morte da célula selecionada, sem alterar as restantes.

    Após 9 transições, todas as células normais estão mortas, constituindo um contraexemplo à propriedade de segurança.
    """)
    return


@app.cell
def _(N, contar_vizinhos_vivos, finais, iniciais):
    sequencia_erro_individual = [
        (1, 2),
        (2, 1),
        (1, 1),
        (2, 3),
        (2, 2),
        (1, 3),
        (3, 1),
        (3, 2),
        (3, 3)
    ]


    def simular_sequencia_individual(n, sequencia):
        # Construir o estado inicial
        estado = [
            [1 if i < 3 and j < 3 else 0 for j in range(n)]
            for i in range(n)
        ]

        # Escolher todas as células iniciais mortas
        borda_zero = {
            pos: 0 for pos in iniciais
        }

        historico = [9]

        for i, j in sequencia:
            atual = estado[i - 1][j - 1]

            vivos = contar_vizinhos_vivos(
                i, j, estado, borda_zero, finais
            )

            estado[i - 1][j - 1] = regra_b3_s23(
                atual, vivos
            )

            historico.append(
                sum(sum(linha) for linha in estado)
            )

        return estado, historico


    estado_final_erro, historico_erro = (
        simular_sequencia_individual(
            N, sequencia_erro_individual
        )
    )

    print("Células vivas por estado:", historico_erro)

    assert historico_erro == list(range(9, -1, -1))
    assert all(
        valor == 0
        for linha in estado_final_erro
        for valor in linha
    )

    print("Contraexemplo individual validado.")
    return (sequencia_erro_individual,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Verificação simbólica do contraexemplo

    A sequência anterior é também verificada através do Z3.

    São criadas 10 configurações simbólicas, correspondentes ao estado inicial e aos estados após cada uma das 9 transições.

    O solver recebe as seguintes restrições:

    - O primeiro estado satisfaz o predicado inicial.
    - Todas as células iniciais da fronteira estão mortas.
    - Cada par de estados consecutivos satisfaz a relação de transição individual.
    - Em cada transição é selecionada a célula indicada na sequência.
    - O último estado satisfaz o predicado de erro.

    Se o resultado for `sat`, a sequência é um contraexemplo válido no modelo formal da FSM.
    """)
    return


@app.cell
def _(
    N,
    borda_final_z3,
    borda_inicial_z3,
    criar_estado_z3,
    predicado_erro,
    predicado_inicial,
    sequencia_erro_individual,
    transicao_z3,
    z3,
):
    def verificar_contraexemplo_z3(n, sequencia):
        estados = [
            criar_estado_z3(n, f"erro_{t}")
            for t in range(len(sequencia) + 1)
        ]

        solver = z3.Solver()

        # Estado inicial
        solver.add(predicado_inicial(estados[0], n))

        # Fronteira inicial morta
        for celula in borda_inicial_z3.values():
            solver.add(z3.Not(celula))

        # Transições individuais
        for t, (i, j) in enumerate(sequencia):
            indice = (i - 1) * n + (j - 1)

            solver.add(
                transicao_z3(
                    estados[t],
                    estados[t + 1],
                    borda_inicial_z3,
                    borda_final_z3,
                    n,
                    "individual",
                    z3.IntVal(indice)
                )
            )

        # Estado final de erro
        solver.add(predicado_erro(estados[-1]))

        return solver.check()


    resultado_erro_individual = verificar_contraexemplo_z3(
        N, sequencia_erro_individual
    )

    print("Resultado Z3:", resultado_erro_individual)

    assert resultado_erro_individual == z3.sat

    print("Contraexemplo confirmado pela FSM.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Contraexemplo — Atualização simultânea

    Na atualização simultânea, todas as células normais evoluem ao mesmo tempo, utilizando os valores da configuração anterior.

    Para procurar um contraexemplo, considera-se uma configuração inicial válida com `N = 17` e valores de fronteira gerados aleatoriamente através da semente `97`.

    Esta configuração permite alcançar o estado de erro após 3 transições:

    - Estado inicial: 9 células vivas;
    - Após 1 transição: 3 células vivas;
    - Após 2 transições: 1 célula viva;
    - Após 3 transições: 0 células vivas.

    A sequência será inicialmente reproduzida em Python e posteriormente verificada com Z3.

    A utilização de uma semente fixa permite reproduzir o contraexemplo, mas não limita a validade da conclusão: basta existir uma configuração inicial permitida que alcance o estado de erro para refutar a propriedade.
    """)
    return


@app.cell
def _(contar_vizinhos_vivos):
    def simular_simultanea(n, fronteira, finais, passos):
        # Construir a grelha inicial
        atual = [
            [1 if i < 3 and j < 3 else 0 for j in range(n)]
            for i in range(n)
        ]

        configuracoes = [atual]

        for _ in range(passos):
            # Todas as células usam o mesmo estado anterior
            seguinte = [
                [
                    regra_b3_s23(
                        atual[i - 1][j - 1],
                        contar_vizinhos_vivos(
                            i, j, atual, fronteira, finais
                        )
                    )
                    for j in range(1, n + 1)
                ]
                for i in range(1, n + 1)
            ]

            atual = seguinte
            configuracoes.append(atual)

        return configuracoes

    return (simular_simultanea,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Teste do contraexemplo simultâneo

    A função `simular_simultanea` é testada com a configuração de fronteira produzida pela semente `97`.

    São executadas três transições e é contado o número de células normais vivas em cada estado.

    Espera-se obter a sequência `[9, 3, 1, 0]`, confirmando que a última configuração corresponde ao estado de erro.
    """)
    return


@app.cell
def _(N, finais, iniciais, random, simular_simultanea):
    _rng_97 = random.Random(97)

    fronteira_97 = {
        pos: _rng_97.randint(0, 1)
        for pos in sorted(iniciais)
    }

    configuracoes_97 = simular_simultanea(
        N, fronteira_97, finais, 3
    )

    contagens_97 = [
        sum(sum(linha) for linha in estado)
        for estado in configuracoes_97
    ]

    print("Células vivas:", contagens_97)

    assert contagens_97 == [9, 3, 1, 0]

    print("Contraexemplo simultâneo validado.")
    return (fronteira_97,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Verificação simbólica com BMC

    Para confirmar o contraexemplo, utiliza-se Bounded Model Checking (BMC) com profundidade `k = 3`.

    São criados quatro estados simbólicos, correspondentes ao estado inicial e aos três estados seguintes.

    O solver recebe as restrições:

    - O primeiro estado satisfaz o predicado inicial.
    - As células iniciais da fronteira assumem os valores gerados pela semente `97`.
    - Cada par de estados consecutivos respeita a relação de transição simultânea.
    - O último estado satisfaz o predicado de erro.

    Um resultado `sat` demonstra a existência de uma execução válida que alcança o estado de erro.

    Neste caso, é suficiente encontrar um contraexemplo para concluir que a propriedade de segurança é falsa.
    """)
    return


@app.cell
def _(
    borda_final_z3,
    borda_inicial_z3,
    criar_estado_z3,
    predicado_erro,
    predicado_inicial,
    transicao_z3,
    z3,
):
    def verificar_erro_simultaneo_z3(n, fronteira, passos):
        estados = [
            criar_estado_z3(n, f"sync97_{t}")
            for t in range(passos + 1)
        ]

        solver = z3.Solver()

        # Estado inicial
        solver.add(
            predicado_inicial(estados[0], n)
        )

        # Fixar a configuração da fronteira
        for pos, valor in fronteira.items():
            solver.add(
                borda_inicial_z3[pos] == z3.BoolVal(valor == 1)
            )

        # Construir as transições simultâneas
        for t in range(passos):
            solver.add(
                transicao_z3(
                    estados[t],
                    estados[t + 1],
                    borda_inicial_z3,
                    borda_final_z3,
                    n,
                    "simultanea"
                )
            )

        # Procurar o estado de erro
        solver.add(
            predicado_erro(estados[-1])
        )

        resultado = solver.check()

        if resultado == z3.sat:
            modelo = solver.model()

            contagens = [
                sum(
                    z3.is_true(
                        modelo.eval(
                            celula,
                            model_completion=True
                        )
                    )
                    for celula in estado.values()
                )
                for estado in estados
            ]

            return resultado, contagens

        return resultado, None

    return (verificar_erro_simultaneo_z3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Teste da verificação simbólica

    O BMC é executado para a configuração de fronteira previamente utilizada, com profundidade `k = 3`.

    Espera-se que o Z3 devolva `sat`, confirmando que existe uma sequência válida de transições que termina no estado de erro.

    O número de células vivas em cada estado do modelo obtido pelo Z3 é também comparado com os resultados da simulação Python.
    """)
    return


@app.cell
def _(N, fronteira_97, verificar_erro_simultaneo_z3, z3):
    resultado_sync, contagens_sync = verificar_erro_simultaneo_z3(
        N, fronteira_97, 3
    )

    print("Resultado Z3:", resultado_sync)
    print("Células vivas por estado:", contagens_sync)

    assert resultado_sync == z3.sat
    assert contagens_sync == [9, 3, 1, 0]

    print("Contraexemplo simultâneo confirmado pela FSM.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Conclusão da propriedade de segurança

    A propriedade de segurança estabelece que o autómato nunca deve alcançar um estado em que todas as células normais estão mortas.

    Foram encontrados contraexemplos para ambas as modalidades:

    | Modalidade | Transições até ao erro | Resultado |
    |---|---:|---|
    | Individual | 9 | Propriedade falsa |
    | Simultânea | 3 | Propriedade falsa |

    Na atualização individual, o contraexemplo foi construído selecionando sucessivamente as 9 células inicialmente vivas, com a fronteira inicial completamente morta.

    Na atualização simultânea, foi utilizada uma configuração de fronteira reproduzível através da semente `97`.

    Os contraexemplos foram reproduzidos por simulação e verificados simbolicamente com Z3.

    Assim, conclui-se que a propriedade **"Nunca se alcança o estado de erro"** não se verifica em nenhuma das duas modalidades consideradas.
    """)
    return


if __name__ == "__main__":
    app.run()
