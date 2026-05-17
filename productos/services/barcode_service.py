import os

import barcode

from barcode.writer import ImageWriter

from django.conf import settings


class BarcodeService:

    @staticmethod
    def generar_codigo_barras(codigo_producto):

        barcode_class = barcode.get_barcode_class('code128')

        barcode_instance = barcode_class(
            codigo_producto,
            writer=ImageWriter()
        )

        carpeta = os.path.join(
            settings.MEDIA_ROOT,
            'barcodes'
        )

        os.makedirs(carpeta, exist_ok=True)

        ruta_archivo = os.path.join(
            carpeta,
            codigo_producto
        )

        archivo_generado = barcode_instance.save(ruta_archivo)

        nombre_relativo = f'barcodes/{codigo_producto}.png'

        return nombre_relativo