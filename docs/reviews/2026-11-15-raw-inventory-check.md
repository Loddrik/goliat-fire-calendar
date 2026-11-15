# Guardia de integridad del inventario raw

`pipeline/verify_raw_inventory.py` es un lector de solo lectura, basado exclusivamente en la biblioteca estándar de Python. Comprueba si una raíz contiene los **1.071 originales exactos** del inventario histórico. No descarga, copia, repara, ingesta ni genera datos. No modifica el inventario, los CSV ni los Parquet.

El contrato de entrada está congelado por el SHA256 de `data/processed/inventory.csv`: `97428b84e89ae70c9d87529a0239a5b4872a453f42b6f853cb51a7377b1090ad`. El inventario declara 101.477.474 bytes. `--inventory` permite señalar otra copia de **ese mismo inventario**; no permite sustituir el contrato por una lista reducida para obtener un resultado completo. Los bytes verificados por hash son exactamente los que se analizan como CSV.

## Uso

Desde el repositorio, para comprobar las rutas canónicas:

```sh
python3 pipeline/verify_raw_inventory.py
```

Para comprobar una raíz virtual de recuperación sin instalar los archivos en `data/raw`:

```sh
python3 pipeline/verify_raw_inventory.py --root .runtime/raw-recovery/restored-exact --details
```

Las rutas del inventario se resuelven **bajo `--root`**: por ejemplo, `data/raw/firms_country/modis/modis_2000_Chile.csv`. La raíz predeterminada y el inventario predeterminado se calculan desde la ubicación del script; no dependen del directorio desde el que se invoque Python. Una ruta relativa proporcionada expresamente en un argumento sigue la semántica habitual del directorio de trabajo.

## Resultado y códigos de salida

El resumen JSON se imprime en stdout. Siempre incluye `status`, `readonly` y, cuando el inventario es válido, `inventory_sha256`, `expected_files`, `exact_files`, `missing_files`, `different_files`, `additional_files`, `expected_bytes` y `exact_bytes`.

| Salida | Estado | Significado |
| --- | --- | --- |
| `0` | `COMPLETE` | Los 1.071 archivos existen y coinciden en bytes y SHA256; no hay CSV adicionales bajo `root/data/raw`. |
| `1` | `INCOMPLETE` | Falta al menos un archivo, alguno difiere o existe un CSV adicional. |
| `2` | `ERROR` | Inventario, rutas o entradas de lectura inválidos; no existe una verificación completa. |

`--details` añade las rutas relativas faltantes y los archivos diferentes, con tamaños y hashes esperados/observados. No incluye URL de origen ni claves. Los errores del sistema operativo se expresan mediante un mensaje genérico para evitar exponer rutas ajenas. Los errores de uso de argumentos siguen la interfaz habitual de `argparse` y devuelven `2`.

Antes de leer los CSV se valida la unicidad de las rutas, el conteo, los tamaños enteros no negativos, los SHA256 hexadecimales de 64 caracteres y las rutas relativas normalizadas bajo `data/raw/`. Se rechazan rutas absolutas, componentes `..`, barras inversas, componentes redundantes y enlaces simbólicos que resuelvan fuera de `root/data/raw`. No se sigue un enlace para leer fuera de ese ámbito. Los archivos se procesan con SHA256 incremental en bloques de 1 MiB; se comprueba también que identidad, tamaño y fecha de modificación no cambien durante la lectura.

## Verificación de esta entrega

Pasaron **10 pruebas sintéticas**, también bajo `python3 -O`: conjunto completo, ausencia de un archivo, alteración con el mismo tamaño, CSV adicional no inventariado, rutas inseguras, duplicados, SHA inválido, escape por enlace simbólico, rechazo del inventario reducido por la CLI y preservación de los bytes originales. El helper admite un contrato explícito pequeño únicamente para estas pruebas; la CLI mantiene el hash y los 1.071 registros congelados.

```sh
python3 -m unittest tests.test_verify_raw_inventory -v
python3 -O -m unittest tests.test_verify_raw_inventory
```

En la comprobación de la raíz virtual `restored-exact` durante esta entrega, tanto la ejecución normal como la optimizada devolvieron `INCOMPLETE`, código `1`: **38 exactos, 1.033 faltantes, 0 diferentes**, con **48.448.231 bytes exactos**. Es una fotografía de esa raíz de staging, no el saldo de las recuperaciones de red que avanzan en paralelo.

Esta guardia acredita identidad de archivos de entrada. **No acredita la corrección científica de los filtros, la cobertura física de observación, la reproducibilidad de una adquisición remota ni la ejecución correcta de la ingestión.** No se ejecutaron construcción, ingestión ni modelos para preparar esta entrega.

La enumeración de CSV adicionales lee únicamente rutas, sin abrir su contenido. Un CSV ajeno al inventario impide `COMPLETE` aunque los 1.071 esperados coincidan. No se siguen subdirectorios enlazados: su presencia causa `ERROR` para evitar una cobertura parcial silenciosa.

Se preparó, **sin aplicarlo**, `.runtime/raw-recovery/ingestion-guard.patch`: añade la llamada a esta guardia antes de `duckdb.connect` en `build_detections.py`, sin cambiar SQL ni deduplicación. El generador histórico `pipeline/inventory.py` sigue sin modificar y puede sobrescribir el inventario si se ejecuta: **no debe ejecutarse durante la recuperación**. La guardia exige el SHA congelado y rechazará posteriormente cualquier inventario sobrescrito, pero no sustituye una futura protección directa del generador.
