# Auditoría de entrega: evidencia disponible y obligaciones pendientes

Corte de esta auditoría: 15 de noviembre de 2026, 10:08 UTC. **El objetivo temporal sigue activo hasta las 11:30 UTC / 08:30 de Santiago.** Este documento no anticipa su cumplimiento ni convierte todos los protocolos científicos en aprobados.

Se contrastaron el objetivo de iteración, los planes conjuntos, los archivos actuales y el estado remoto. La [matriz científica de 13 requisitos](evidence/goal-audit-20261115/scientific-governance.json) y la [auditoría operativa](evidence/goal-audit-20261115/operational.json) conservan fuentes, hashes, estados y límites. La segunda fue realizada por un contribuidor al HTML: verifica cobertura operativa, sin presentarse como una revisión independiente de su propio artifact.

| Obligación | Evidencia comprobada | Alcance o pendiente |
|---|---|---|
| Consejos multifocal y adversario; enfoque loco | Rondas 24, 31, 35 y 38, votos y ratificaciones; criterios 30/25/20/15/10 conservados. | El enfoque loco es explícito en 24/31/38; en 35 el tercer voto se rotula ingeniería. Las prioridades no fueron unánimes. |
| Criterios antes de ordenar opciones | Cronología Git de 24/31, pesos heredados en 35/38 y hashes de planes/votos. | Los rangos son subjetivos; B38 queda N/A, sin imputar cero. |
| Ganancias marginales comparables | Endpoints del mismo panel18, reducción compuesta 12,18 %. | No sumar porcentajes alternativos ni mezclar MAE18/21 y CRPS39. |
| Negativos y límites visibles | 23, 35 y 37 permanecen negativos; el continuo30B sigue fallido. | 39 no rescata esas primarias; 32/33 usan un estimando nominal diferente. |
| Máximo de cuatro agentes activos | Restricción del scheduler y secuencias de revisión documentadas. | No se reconstruyó un registro histórico completo de activaciones; no se afirma esa auditoría exhaustiva. |
| Publicación científica sin promoción automática | 448 archivos protegidos, 12 entradas y 8 archivos de código mantienen los hashes39; M1/14 no cambia. | No se resolvieron oportunidad física, PSF, exposición por píxel o puente local NOAA-20. |
| Identidad de commits y entrega incremental | 89 commits locales examinados en la auditoría: Daniel Quinteros, correo solicitado, sin firma. PR58–62 abiertos hacia dev y comparaciones propias. | Estados remotos comprobados al momento del informe; no certifican merges o despliegues posteriores. |
| HTML detallado y reproducibilidad acotada | Siete SVG, fuentes con hashes, revisión separada y navegador390/1440; lector39 portátil pasa también en CI Linux. | No equivale a reconstrucción desde los 1.071 CSV canónicos ausentes ni a calibración física. |
| Preservar trabajo anterior | 47 entradas raw y tres documentos originales coinciden con su inventario; bundle FireChronos original y dos archivos de cobertura de suelo verificados. | Auditoría local de inventarios explícitos, no afirmación absoluta sobre cualquier trabajo que nunca se inventarió. |
| Preservar los dos casos L2 | Ocho miembros de backups tar coinciden con hashes de adquisición: 389.098.300 bytes. | Comprobación de integridad, sin lectura científica nueva, descargas o reapertura del presupuesto L2. |
| Credenciales fuera de la entrega | Búsqueda de los valores reales en 1.699 archivos versionados y 210 archivos comprimidos: cero coincidencias. | Alcance sobre los valores proporcionados y el árbol actual; no detector universal ni auditoría de todo el historial. |
| Cierre y actualización final | PR62 y bundle0956 verificados al corte, más auditorías posteriores por incorporar. | Proteger D10:13–11:13, sus últimos30min de consolidación, y contingencia11:13–11:30; comprobar estado real al finalizar. |

Hay dos desviaciones de protocolo que deben acompañar a los resultados. **37 omitió el snapshot contemporáneo del entorno del productor**: el registro posterior del revisor no cumple retroactivamente ese requisito. El estudio39 corrigió ese proceso para su propio freeze. **35 omitió diagnósticos B/C**: un suplemento independiente autorizado completó el registro sin refits, sin cambiar la primaria y sin editar el paquete original. No se presentan esas primeras entregas como si hubieran cumplido todos los requisitos desde el inicio.

La auditoría detectó además que los cambios puramente documentales no activaban el job científico. La corrección propuesta añade al CI general, que sí se ejecuta en todos los PR, la regeneración determinista del HTML y su comparación exacta con el artifact versionado. Comprueba coherencia entre fuentes y documento; no sustituye la revisión científica o el navegador. El resultado remoto de ese nuevo paso debe verificarse después del push.

Los registros de [preservación inicial](evidence/goal-audit-20261115/preservation.json), [backups L2](evidence/goal-audit-20261115/raw-case-preservation.json) y [credenciales](evidence/goal-audit-20261115/credential-byte-check.json) explicitan sus límites. Ninguna de estas comprobaciones calcula otra ganancia predictiva, altera observaciones o certifica la verdad de un incendio.
