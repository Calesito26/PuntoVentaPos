from reportlab.platypus import Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet


def agregar_cabecera_empresa(elementos, empresa, titulo):
    styles = getSampleStyleSheet()

    if empresa and empresa.logo:
        try:
            logo = Image(
                empresa.logo.path,
                width=90,
                height=60
            )
            elementos.append(logo)
            elementos.append(Spacer(1, 8))
        except Exception:
            pass

    elementos.append(
        Paragraph(
            empresa.nombre_empresa if empresa else 'PuntoVentaPOS',
            styles['Title']
        )
    )

    if empresa:
        if empresa.razon_social:
            elementos.append(Paragraph(empresa.razon_social, styles['Normal']))

        if empresa.ruc:
            elementos.append(Paragraph(f'RUC: {empresa.ruc}', styles['Normal']))

        if empresa.direccion:
            elementos.append(Paragraph(f'Dirección: {empresa.direccion}', styles['Normal']))

        if empresa.telefono:
            elementos.append(Paragraph(f'Teléfono: {empresa.telefono}', styles['Normal']))

        if empresa.email:
            elementos.append(Paragraph(f'Correo: {empresa.email}', styles['Normal']))

    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(titulo, styles['Heading1']))
    elementos.append(Spacer(1, 12))