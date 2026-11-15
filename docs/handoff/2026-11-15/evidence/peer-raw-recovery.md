# Originales recibidos del equipo: inventario completo

El 15 de noviembre de 2026 se verificó el archivo proporcionado por el usuario `goliat-data-raw.tar.gz`, de **23.522.998 bytes**, mediante lectura secuencial gzip/tar. Su SHA-256 es:

```text
6999eec9d27c4ebe3af1314355a78c7fb98acb7f77224b04db8ccc85c0bd1698
```

El tar contiene **1.072 miembros regulares**: los **1.071 CSV raw** y una copia de `data/processed/inventory.csv`. Esta última coincide con el inventario congelado `97428b84e89ae70c9d87529a0239a5b4872a453f42b6f853cb51a7377b1090ad` y no se instaló ni sobrescribió. Los nombres raw tienen prefijo `data/raw/`, conservado sin reubicación; el lector sólo permite retirar un `./` inicial si lo hubiera.

Cada CSV del tar coincide en **ruta, tamaño y SHA-256** con el inventario. No se encontraron miembros peligrosos, enlaces, duplicados raw, CSV inesperados o diferencias. No se usó `extractall`: únicamente se prepararon los 115 archivos ausentes y se instalaron sin sobrescribir archivos existentes, después de validar sus bytes. Los archivos previamente recuperados y la evidencia histórica permanecen intactos.

| Estado | Antes | Después |
| --- | ---: | ---: |
| Originales exactos | 956/1.071 | **1.071/1.071** |
| Archivos faltantes | 115 | **0** |
| Archivos diferentes | 0 | **0** |
| CSV adicionales en raw | 0 | **0** |
| Bytes exactos | 94.345.574 | **101.477.474** |

Se restauraron **115 originales**, incluidos los cuatro snapshots NRT que no coincidían con sus redescargas y las 111 ventanas que no alcanzaron a consultarse. Son **7.131.900 bytes adicionales**. Los cuerpos no coincidentes de la recuperación anterior continúan separados en quarantine; no se hicieron pasar por los originales.

La [evidencia de restauración](peer-raw-recovery.json) conserva el SHA del tar, sus miembros, el mapeo, las 115 rutas instaladas y los estados antes/después. El [resultado del verificador independiente por CLI](peer-verification.json) procede de:

```sh
.venv/bin/python pipeline/verify_raw_inventory.py --details
```

Su resultado es **COMPLETE**, con salida **0**, 1.071 archivos exactos y ninguna ausencia, diferencia o CSV adicional. El verificador sólo lee; no genera un inventario nuevo.

**Alcance:** se completó la disponibilidad de los originales congelados. No se ejecutó ingestión, ajuste, publicación ni reconstrucción cartográfica. La comparación estricta de detecciones que falló una fila por cada lado permanece fallida; disponer de todos los CSV no la resuelve ni valida por sí mismo el modelo o la observabilidad física. Los reportes anteriores de recuperación parcial siguen describiendo sus respectivos momentos.
