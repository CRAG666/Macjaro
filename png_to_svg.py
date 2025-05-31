#!/usr/bin/env python3
"""
Script para convertir imágenes PNG a SVG con tamaño personalizable
La imagen PNG se embebe directamente sin reescalar - SVG maneja el escalado
Requiere: pip install Pillow (solo para obtener dimensiones originales)
"""

import base64
import argparse
import os
import sys
from PIL import Image
from io import BytesIO


def png_to_svg(input_path, output_path=None, width=128, height=128):
    """
    Convierte una imagen PNG a SVG con el tamaño especificado

    Args:
        input_path (str): Ruta de la imagen PNG de entrada
        output_path (str): Ruta de salida del SVG (opcional)
        width (int): Ancho deseado en píxeles
        height (int): Alto deseado en píxeles
    """
    try:
        # Leer la imagen original sin modificarla
        with open(input_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()

        # Obtener dimensiones originales para información
        with Image.open(input_path) as img:
            orig_width, orig_height = img.size

        # Crear el contenido SVG (SVG maneja el escalado automáticamente)
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg">
    <image x="0" y="0" width="{width}" height="{height}"
           href="data:image/png;base64,{img_data}"
           preserveAspectRatio="xMidYMid meet"/>
</svg>'''

        # Determinar ruta de salida
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_{width}x{height}.svg"

        # Determinar ruta de salida
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_{width}x{height}.svg"

        # Guardar el archivo SVG
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"✓ Conversión exitosa: {input_path} → {output_path}")
        print(
            f"  Dimensiones originales: {orig_width}x{orig_height} → SVG: {width}x{height} píxeles"
        )

    except Exception as e:
        print(f"✗ Error al procesar {input_path}: {str(e)}")
        return False

    return True


def batch_convert(input_dir, output_dir=None, width=128, height=128):
    """
    Convierte todas las imágenes PNG de un directorio

    Args:
        input_dir (str): Directorio con imágenes PNG
        output_dir (str): Directorio de salida (opcional)
        width (int): Ancho deseado
        height (int): Alto deseado
    """
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    png_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".png")]

    if not png_files:
        print(f"No se encontraron archivos PNG en {input_dir}")
        return

    print(f"Procesando {len(png_files)} archivos PNG...")
    successful = 0

    for filename in png_files:
        input_path = os.path.join(input_dir, filename)

        if output_dir:
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{base_name}_{width}x{height}.svg")
        else:
            output_path = None

        if png_to_svg(input_path, output_path, width, height):
            successful += 1

    print(f"\n✓ Procesados exitosamente: {successful}/{len(png_files)} archivos")


def main():
    parser = argparse.ArgumentParser(
        description="Convierte imágenes PNG a SVG con tamaño personalizable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python png_to_svg.py imagen.png --size 128x128
  python png_to_svg.py imagen.png -s 256x256 -o salida.svg
  python png_to_svg.py --batch ./imagenes/ --size 64x64
  python png_to_svg.py -b ./src/ -o ./svg/ -s 512x512
        """,
    )

    # Argumentos principales
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("input_file", nargs="?", help="Archivo PNG de entrada")
    group.add_argument(
        "-b", "--batch", help="Directorio con archivos PNG para conversión en lote"
    )

    # Opciones
    parser.add_argument("-o", "--output", help="Archivo o directorio de salida")
    parser.add_argument(
        "-s",
        "--size",
        default="128x128",
        help="Tamaño de salida en formato WIDTHxHEIGHT (default: 128x128)",
    )

    args = parser.parse_args()

    # Parsear el tamaño
    try:
        if "x" in args.size.lower():
            width_str, height_str = args.size.lower().split("x")
        else:
            print("Error: El formato de tamaño debe ser WIDTHxHEIGHT (ej: 128x128)")
            sys.exit(1)

        width = int(width_str)
        height = int(height_str)

        if width <= 0 or height <= 0:
            raise ValueError("Las dimensiones deben ser positivas")

    except ValueError as e:
        print(f"Error en el tamaño especificado: {e}")
        sys.exit(1)

    # Ejecutar conversión
    if args.batch:
        # Conversión en lote
        if not os.path.isdir(args.batch):
            print(f"Error: {args.batch} no es un directorio válido")
            sys.exit(1)

        batch_convert(args.batch, args.output, width, height)

    else:
        # Conversión individual
        if not os.path.isfile(args.input_file):
            print(f"Error: {args.input_file} no existe o no es un archivo")
            sys.exit(1)

        if not args.input_file.lower().endswith(".png"):
            print("Error: El archivo debe tener extensión .png")
            sys.exit(1)

        success = png_to_svg(args.input_file, args.output, width, height)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
