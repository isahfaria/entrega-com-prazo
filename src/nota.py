from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import math


def calcular_nota_final(
    nota, prazo, entrega, justificativa_aprovada, novo_prazo=None
):
    """Calcula o resultado de uma entrega aplicando a regra de atraso."""
    if isinstance(nota, bool) or not isinstance(nota, (int, float, Decimal)):
        raise ValueError("nota deve ser um numero entre 0 e 10")
    if not math.isfinite(float(nota)) or nota < 0 or nota > 10:
        raise ValueError("nota deve ser um numero entre 0 e 10")
    if not isinstance(justificativa_aprovada, bool):
        raise ValueError("justificativa_aprovada deve ser bool")

    for nome, valor in (("prazo", prazo), ("entrega", entrega)):
        if not isinstance(valor, datetime):
            raise ValueError(f"{nome} deve ser datetime")
    if novo_prazo is not None and not isinstance(novo_prazo, datetime):
        raise ValueError("novo_prazo deve ser datetime")

    prazo_com_fuso = prazo.tzinfo is not None and prazo.utcoffset() is not None
    entrega_com_fuso = entrega.tzinfo is not None and entrega.utcoffset() is not None
    if prazo_com_fuso != entrega_com_fuso:
        raise ValueError("prazo e entrega devem usar o mesmo formato de fuso horario")

    prazo_efetivo = prazo
    if justificativa_aprovada:
        if novo_prazo is None:
            raise ValueError("justificativa aprovada exige novo prazo")
        if not isinstance(novo_prazo, datetime):
            raise ValueError("novo_prazo deve ser datetime")

        novo_com_fuso = (
            novo_prazo.tzinfo is not None and novo_prazo.utcoffset() is not None
        )
        if prazo_com_fuso != novo_com_fuso:
            raise ValueError("prazo e novo_prazo devem usar o mesmo formato de fuso horario")
        if novo_prazo < prazo:
            raise ValueError("novo_prazo nao pode ser anterior ao prazo original")

        prazo_efetivo = novo_prazo

    entrega_calculo = entrega
    prazo_calculo = prazo_efetivo
    if entrega_com_fuso:
        entrega_calculo = entrega.astimezone(timezone.utc)
        prazo_calculo = prazo_efetivo.astimezone(timezone.utc)
    atraso = entrega_calculo - prazo_calculo
    if atraso.total_seconds() <= 0:
        dias_atraso = 0
    else:
        dias_atraso = atraso.days + (1 if atraso.seconds or atraso.microseconds else 0)

    if dias_atraso == 0:
        return {
            "aceita": True,
            "nota_final": float(
                Decimal(str(nota)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "desconto_percentual": 0,
            "dias_atraso": 0,
        }

    if dias_atraso > 5:
        return {
            "aceita": False,
            "nota_final": None,
            "desconto_percentual": None,
            "dias_atraso": dias_atraso,
        }

    desconto_percentual = min(dias_atraso * 10, 50)
    nota_decimal = Decimal(str(nota))
    fator = Decimal(100 - desconto_percentual) / Decimal(100)
    nota_final = float(
        (nota_decimal * fator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )

    return {
        "aceita": True,
        "nota_final": nota_final,
        "desconto_percentual": desconto_percentual,
        "dias_atraso": dias_atraso,
    }
