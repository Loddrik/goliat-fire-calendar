# GOLIAT: entrega al equipo de presentación

**15 de noviembre de 2026 · límite de entrega 12:30 Santiago / 15:30 UTC.** Este paquete explica el producto conservado, la investigación y sus límites. No cambia M1, compuertas, predicciones ni datos publicados. El candidato de aplicación es el código científico de `6410fcb491e9a318419d7b142ddab52b1e483662` (PR64); la rama `docs/44-handoff-presentacion` añade documentación. El estado de integración y el de despliegue deben comprobarse por separado.

## Empieza aquí: diez minutos para preparar el relato

1. Abrir [el informe de negocio HTML](resumen-negocio.html): problema, resultado, guion de tres minutos y respuestas difíciles. También está en [Markdown](resumen-negocio.md).
2. Consultar [el informe técnico HTML](resumen-tecnico.html): contratos, cambios por etapa, evidencia, comandos y apéndice de PR. También está en [Markdown](resumen-tecnico.md).
3. Revisar [las seis prioridades HTML](pendientes-priorizados.html) o su [lista Markdown](pendientes-priorizados.md). Los votos de los consejos y la ejecución son registros distintos.
4. Antes de anunciar una demo funcional, identificar la versión que se abre y leer el [acta local de comprobación](acta-ensayo.md). Un build local o CI verde no acredita el despliegue público.

## Qué decir y qué comprobar

**Producto conservado:** calendario de actividad térmica para 54 comunas de Biobío y Ñuble. M1 habilita reconstrucción mensual histórica en 14; las otras 40 conservan observaciones. Una celda-día con detección no es un incendio individual y un cero no certifica ausencia de fuego. La vista por plataforma tiene un contrato diferente del calendario armonizado.

**Investigación:** existen mejoras retrospectivas bajo contratos explícitos y resultados negativos preservados. E_coherent y F21 no sustituyen M1. F21 no es un pronóstico de incendios futuros ni una banda anual validada. El diagnóstico estacional de 112 casos es aparente después de seleccionar comunas; no valida 2002–2011.

**Versiones y PR:** el [inventario de entrega](evidence/pr-inventory.json), fechado a las 13:41 UTC, distingue 24 PR científicos: tres fusionados (#23–25) y 21 abiertos. #22, de integración, está fusionado; #31 sigue abierto hacia `main`. Las ramas científicas abiertas requieren revisión y un plan de integración. No corresponde fusionarlas en bloque para presentar. Los nuevos PR se dirigen a `dev`.

**Comprobación de software:** el [recibo de CI](evidence/verification-snapshot.json) identifica el commit `6410fcb` y el run con **358 tests**, más el lector portátil de evidencia CRPS (10.368 CDF y 432 conjuntos). Ambos checks de PR64 estaban en SUCCESS en ese corte. Son verificaciones de software y evidencia congelada, no validación de verdad física ni utilidad municipal.

## Abrir la aplicación sin reingestar datos

Desde la raíz del repositorio, en un checkout con dependencias instaladas:

```sh
npm --prefix web run build
PORT=3999 npm start
```

Abrir `http://localhost:3999/explorar?cut=08111&lang=es` (Tomé), después añadir `&vista=tabla` y finalmente cambiar a `cut=08101` (Concepción). El [guion](resumen-negocio.md) describe qué mostrar. `http://localhost:3999/health` identifica el proceso local, no una versión remota desplegada.

Un checkout nuevo necesita primero `npm ci` en la raíz y `npm --prefix web ci`, respetando sus lockfiles. No hacen falta claves NASA para consultar los JSON publicados incluidos. El mapa carga un estilo externo: para una presentación sin red, preparar capturas y conservar calendario/tabla como alternativa. La aplicación no se convierte en una solución offline por ejecutarla en localhost.

No ejecutar `pipeline/inventory.py`, reconstruir raw ni lanzar drivers históricos con deadlines vencidos para preparar la demo. En particular, no regenerar el inventario para ocultar los 115 faltantes.

## Verificar evidencia y preservar el trabajo

Con el entorno científico bloqueado existente, el lector es de sólo lectura:

```sh
.venv/bin/python pipeline/verify_crps_evidence.py
.venv/bin/python pipeline/verify_raw_inventory.py --details
```

El segundo comando debe informar **INCOMPLETE** y salir con código 1 mientras falten originales. En esta copia hay 956/1.071 exactos; en un clon sin respaldo puede haber cero. Es una negativa esperada del guard, no permiso para reingestar parcialmente. La [auditoría histórica](../../reviews/2026-11-15-raw-historical-core-audit.md) documenta una fila distinta por lado en la comparación estricta, aunque máscara y agregados coincidan usando la asignación comunal congelada.

Los originales están ignorados por Git. El respaldo local `goliat-raw-recovery-20261115-1327.tar` se conserva en la carpeta hermana `nasa/backups`, con 956 miembros verificados; su hash consta en el [acta local](acta-ensayo.md). Su custodia y transferencia requieren un receptor; no están incluidas en un clon de GitHub. El [reporte de recuperación](../../reviews/2026-11-15-raw-recovery-report.md) y su manifest conservan el inventario. Preguntar al otro desarrollador por su `data/raw` es útil para comparar los pendientes, pero no bloquea esta presentación. Conservar la copia sin regenerarla; aceptar sólo archivos que coincidan en ruta, tamaño y SHA con el inventario congelado.

## Reproducir los informes HTML

Los cuatro HTML son autónomos, sin fuentes, scripts o estilos externos, y se generan desde sus Markdown. Pueden abrirse directamente desde disco; imprimir permite guardar PDF. Los enlaces a evidencia requieren conservar la estructura del repositorio.

Instalar las dependencias sólo documentales en un entorno separado del científico:

```sh
python3 -m venv /tmp/goliat-handoff-render
/tmp/goliat-handoff-render/bin/pip install -r docs/handoff/2026-11-15/requirements-render.txt
/tmp/goliat-handoff-render/bin/python pipeline/build_presentation_handoff.py
/tmp/goliat-handoff-render/bin/python pipeline/build_presentation_handoff.py --check
```

El pie de cada informe registra el SHA-256 de su fuente Markdown. El renderer no ajusta modelos, no descarga datos y no cambia la publicación.

## Responsables y límites del traspaso

El coordinador automatizado prepara documentación, comprobaciones locales y PR. El equipo receptor debe nombrar presentador y mantenedor de release, confirmar qué versión presentará y asignar custodia del respaldo. Los responsables por rol del plan no equivalen a personas ya asignadas.

No hay autorización automática de merge o despliegue. El handoff entrega evidencia y acciones verificables; la revisión de integración pertenece al mantenedor. La pregunta final del piloto es si un usuario municipal completa e interpreta una comparación útil, todavía sin medición de ahorro, ROI ni reducción de daños.
