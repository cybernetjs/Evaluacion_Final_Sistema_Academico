from app import db


def calcular_numero_seccion(oferta) -> int:
    """Devuelve la posición (>=1) de `oferta` entre las ofertas del mismo
    curso y periodo académico, ordenadas por id."""
    from app.dominio.modelos.ofertas.oferta_academica import OfertaAcademica

    ofertas_hermanas = (
        OfertaAcademica.query
        .filter_by(curso_id=oferta.curso_id, periodo_academico_id=oferta.periodo_academico_id)
        .order_by(OfertaAcademica.id.asc())
        .all()
    )

    for posicion, hermana in enumerate(ofertas_hermanas, start=1):
        if hermana.id == oferta.id:
            return posicion

    return 1


def etiqueta_seccion(oferta) -> str:
    """Etiqueta lista para mostrar, ej. 'S-1'."""
    return f"S-{calcular_numero_seccion(oferta)}"
