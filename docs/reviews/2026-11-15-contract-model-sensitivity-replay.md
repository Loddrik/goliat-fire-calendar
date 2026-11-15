# Replay offline independiente de24C

El runner congelado reprodujo **los7 archivos de salida byte por byte**, incluidos el manifiesto y el freeze, en un clon local separado del commit `8b29113404d82f71cf6563ab045b78e8d0c1a766`. No hubo diferencias de procedencia ni normalización de cifras. El clon quedó limpio después de ejecutar.

Se utilizó `/private/tmp/goliat-contract-replay-20261115-git`, con HEAD detached verificado, y el mismo intérprete `.venv/bin/python` del repositorio principal. El comando fue `python pipeline/contract_model_sensitivity_audit.py`, sin editar código, protocolo o freeze. El proceso terminó con código0 y estado `frozen-contract-sensitivity-complete`; se verificaron de nuevo510 fuentes protegidas y todos los hashes de código. El clon no contiene `.runtime`; no se copiaron ni leyeron secretos o raw, ni fueron necesarias llamadas de red.

Finalizó a2026-11-15T04:41:11.959135+00:00, antes del límite original05:29:28Z. No se amplió el cap. No se repitió la suite completa ni se ajustaron modelos.

La [evidencia](evidence/contract-model-sensitivity-replay/summary.json) conserva SHA256 y tamaños de cada archivo, entorno y ruta. El replay usa el mismo entorno Python, por lo que prueba reproducción local separada del cálculo, no portabilidad entre plataformas ni validación científica independiente, física oG1.

Una primera extracción de archivo usó por error `/private/tmp` directamente y luego se creó una carpeta de archivo sin Git. Ambas quedan identificadas en las notas operativas; el replay que cumple el encargo usa el clon real separado, sin sobrescribir destinos ni efectuar borrados globales. Ningún artefacto original de24C fue modificado.
