# Cole aqui os seus criterios de aceitacao, no formato Dado / Quando / Entao,
# um por requisito, antes de pedir qualquer teste ao Copilot.
#
# Exemplo do formato:
#   RF-002
#   Dado um trabalho com prazo em 10/11 as 23h59
#   Quando o aluno entrega em 10/11 as 22h00
#   Entao a nota final e igual a nota integral
# RF-001
# Dado uma nota 8,0, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-10 23:59 (exatamente no limite)
# Então a entrega é aceita, a nota final é 8,0, o desconto é 0% e os dias de atraso são 0
# RF-002
# Dado uma nota 10, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-11 00:00 (1 minuto depois)
# Então a entrega é aceita, o desconto é 10%, os dias de atraso são 1 e a nota final é 9,0
# RF-003
# Dado uma nota 10, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-12 00:00 (24 horas e 1 minuto depois)
# Então os dias de atraso são 2, o desconto é 20% e a nota final é 8,0
# RF-004
# Dado uma nota 10, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-15 23:59 (exatamente 5 dias depois)
# Então a entrega é aceita, o desconto é 50% (nunca mais que isso) e a nota final é 5,0
# RF-005
# Dado uma nota 10, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-16 00:00 (5 dias e 1 minuto depois)
# Então a entrega não é aceita, a nota final é None e o desconto é None
# RF-006
# Dado uma nota 10, prazo em 2026-11-10 23:59, justificativa aprovada e novo prazo em 2026-11-20 23:59
# Quando a entrega ocorre em 2026-11-18 10:00 (depois do prazo original, antes do novo)
# Então a entrega é aceita, o desconto é 0% e a nota final é 10,0
# RF-007
# Dado uma nota 10, prazo em 2026-11-10 23:59, justificativa aprovada e novo prazo em 2026-11-20 23:59
# Quando a entrega ocorre em 2026-11-21 10:00 (cerca de 10 horas depois do novo prazo)
# Então os dias de atraso são 1, o desconto é 10% e a nota final é 9,0
# RF-008
# Dado uma nota 10, prazo em 2026-11-10 23:59, sem justificativa aprovada e novo prazo informado em 2026-11-20 23:59
# Quando a entrega ocorre em 2026-11-12 00:00
# Então o novo prazo é ignorado, os dias de atraso são 2 e a nota final é 8,0
# RF-009
# Dado uma entrega aceita com atraso de 1 dia
# Quando a função retorna o resultado
# Então o resultado contém as informações aceita, nota_final, desconto_percentual e dias_atraso
# RF-010
# Cenário A
# Dado uma nota 11 (fora da faixa de 0 a 10)
# Quando a função é chamada
# Então a função lança ValueError

# Cenário B
# Dado uma nota True (bool)
# Quando a função é chamada
# Então a função lança ValueError
# RF-011
# Dado justificativa aprovada e novo prazo não informado (None)
# Quando a função é chamada
# Então a função lança ValueError
# RF-012
# Dado prazo em 2026-11-10 23:59, justificativa aprovada e novo prazo em 2026-11-09 23:59
# Quando a função é chamada
# Então a função lança ValueError
# RF-013
# Dado prazo sem fuso horário e entrega com fuso horário UTC
# Quando a função é chamada
# Então a função lança ValueError
# RF-014
# Dado uma nota 10, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-16 00:00 (5 dias e 1 minuto depois)
# Então a entrega não é aceita e os dias de atraso são 6
# RF-015
# Dado uma nota 9,25, prazo em 2026-11-10 23:59 e sem justificativa aprovada
# Quando a entrega ocorre em 2026-11-11 00:00 (1 dia de atraso)
# Então a nota final é 8,33 (8,325 arredondado para cima)
from datetime import datetime, timezone

import pytest

from src.nota import calcular_nota_final


def test_rf001_entrega_exatamente_no_limite():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 10, 23, 59)

    resultado = calcular_nota_final(8.0, prazo, entrega, False, None)

    assert resultado["aceita"] is True
    assert resultado["nota_final"] == 8.0
    assert resultado["desconto_percentual"] == 0
    assert resultado["dias_atraso"] == 0


def test_rf002_entrega_um_minuto_atrasada():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 11, 0, 0)

    resultado = calcular_nota_final(10.0, prazo, entrega, False, None)

    assert resultado["aceita"] is True
    assert resultado["desconto_percentual"] == 10
    assert resultado["dias_atraso"] == 1
    assert resultado["nota_final"] == 9.0


def test_rf003_entrega_vinte_quatro_horas_e_um_minuto_atrasada():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 12, 0, 0)

    resultado = calcular_nota_final(10.0, prazo, entrega, False, None)

    assert resultado["dias_atraso"] == 2
    assert resultado["desconto_percentual"] == 20
    assert resultado["nota_final"] == 8.0


def test_rf004_entrega_exatamente_cinco_dias_atrasada():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 15, 23, 59)

    resultado = calcular_nota_final(10.0, prazo, entrega, False, None)

    assert resultado["aceita"] is True
    assert resultado["desconto_percentual"] == 50
    assert resultado["nota_final"] == 5.0


def test_rf005_entrega_cinco_dias_e_um_minuto_atrasada():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 16, 0, 0)

    resultado = calcular_nota_final(10.0, prazo, entrega, False, None)

    assert resultado["aceita"] is False
    assert resultado["nota_final"] is None
    assert resultado["desconto_percentual"] is None


def test_rf006_entrega_dentro_do_novo_prazo_com_justificativa():
    prazo_original = datetime(2026, 11, 10, 23, 59)
    novo_prazo = datetime(2026, 11, 20, 23, 59)
    entrega = datetime(2026, 11, 18, 10, 0)

    resultado = calcular_nota_final(
        10.0, prazo_original, entrega, True, novo_prazo
    )

    assert resultado["aceita"] is True
    assert resultado["desconto_percentual"] == 0
    assert resultado["nota_final"] == 10.0


def test_rf007_entrega_atrasada_apos_novo_prazo():
    prazo_original = datetime(2026, 11, 10, 23, 59)
    novo_prazo = datetime(2026, 11, 20, 23, 59)
    entrega = datetime(2026, 11, 21, 10, 0)

    resultado = calcular_nota_final(
        10.0, prazo_original, entrega, True, novo_prazo
    )

    assert resultado["dias_atraso"] == 1
    assert resultado["desconto_percentual"] == 10
    assert resultado["nota_final"] == 9.0


def test_rf008_novo_prazo_e_ignorado_sem_justificativa():
    prazo_original = datetime(2026, 11, 10, 23, 59)
    novo_prazo = datetime(2026, 11, 20, 23, 59)
    entrega = datetime(2026, 11, 12, 0, 0)

    resultado = calcular_nota_final(
        10.0, prazo_original, entrega, False, novo_prazo
    )

    assert resultado["dias_atraso"] == 2
    assert resultado["nota_final"] == 8.0


def test_rf009_resultado_contem_as_informacoes_requeridas():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 11, 0, 0)

    resultado = calcular_nota_final(10.0, prazo, entrega, False, None)

    assert set(resultado) == {
        "aceita",
        "nota_final",
        "desconto_percentual",
        "dias_atraso",
    }


def test_rf010_nota_fora_da_faixa_lanca_value_error():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 10, 23, 59)

    with pytest.raises(ValueError):
        calcular_nota_final(11.0, prazo, entrega, False, None)


def test_rf010_nota_bool_lanca_value_error():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 10, 23, 59)

    with pytest.raises(ValueError):
        calcular_nota_final(True, prazo, entrega, False, None)


def test_rf011_justificativa_sem_novo_prazo_lanca_value_error():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 11, 0, 0)

    with pytest.raises(ValueError):
        calcular_nota_final(10.0, prazo, entrega, True, None)


def test_rf012_novo_prazo_antes_do_prazo_original_lanca_value_error():
    prazo = datetime(2026, 11, 10, 23, 59)
    novo_prazo = datetime(2026, 11, 9, 23, 59)
    entrega = datetime(2026, 11, 11, 0, 0)

    with pytest.raises(ValueError):
        calcular_nota_final(10.0, prazo, entrega, True, novo_prazo)


def test_rf013_prazo_sem_fuso_e_entrega_com_fuso_lanca_value_error():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 10, 23, 59, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        calcular_nota_final(10.0, prazo, entrega, False, None)


def test_rf014_entrega_rejeitada_informa_seis_dias_de_atraso():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 16, 0, 0)

    resultado = calcular_nota_final(10.0, prazo, entrega, False, None)

    assert resultado["aceita"] is False
    assert resultado["dias_atraso"] == 6


def test_rf015_nota_decimal_e_arredondada_para_cima():
    prazo = datetime(2026, 11, 10, 23, 59)
    entrega = datetime(2026, 11, 11, 0, 0)

    resultado = calcular_nota_final(9.25, prazo, entrega, False, None)

    assert resultado["nota_final"] == 8.33
