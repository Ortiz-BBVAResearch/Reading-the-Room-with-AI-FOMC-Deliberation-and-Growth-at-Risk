# Review 37e — Addendum: penalizaciones por bloque, rama UPPER y benchmark de la tendencia central en el centro

**Contexto.** El informe provisional de la Review 37e encuentra que:
- el M2 principal (A1) y `M2_CH` usan **λ = 5,6234** en el centro;
- el único M2 con historia desde 1974Q4 y **λ = 100** en el centro son los bancos `A4B_M2_SEP`, es decir, C1 con la tendencia central larga;
- el contrato operativo A4B usa **λ = 0,3162** en el bloque superior.

El paper declara **λ_L = 0,5623 y λ_C = λ_U = 100**. Además, en la Review 34 se concluyó que en el bloque superior se usaba 100.

Hay que resolver esta discrepancia **antes de cerrar la Review 37e** y antes de abrir pérdidas de la rama UPPER.

**Nada de esto reabre C1–C4.** Cada contraste es coherente por dentro, porque benchmark y modelo con Hidden Dissent comparten λ. Etiquetado: **post-audit, descriptive**.

Contrato inferencial sin cambios: H=4, HAC Bartlett con desfase 3, HLN df=N−1, bootstrap de bloques móviles con B=10.000, semilla 20260903, L=4 principal y L=6 y 8 como sensibilidad.

---

## A. Tabla de penalizaciones por bloque (prioridad 1, sin estimar nada)

Entregar una tabla con **una fila por familia de bancos** y estas columnas:
- λ efectivamente usada en el bloque inferior (Q05–Q25), en el centro (Q30–Q70) y en el bloque superior (Q75–Q95);
- primera observación de estimación y número de observaciones en el primer origen;
- unidad o escala de λ (por observación o sobre la suma de pérdidas; si se reescala con N, cómo);
- hash del vector de λ;
- fuente: código o metadatos del banco, no el nombre del modelo.

**Familias:**

| # | Familia | Uso en el paper |
|---|---|---|
| 1 | M2, M2+HD principales (A1) | Tablas 2 y 3 |
| 2 | M3, M3+HD principales (A1) | Tabla 3 |
| 3 | `M2_CH`, `M2_CH+HD` | benchmark de historia común |
| 4 | `M3_CH`, `M3_CH+HD` | benchmark de historia común |
| 5 | `A4B_M2_SEP` y `A4B_M2_SEP+HD` (C1) | Tabla 9 |
| 6 | M2+DISP_long y +HD (C3, centro) | Tabla 9 |
| 7 | M3+DISP_long y +HD (C2) | Tabla 9 |
| 8 | M3+CT_long y +HD (C4) | Tabla 9 |
| 9 | Los 20 bancos nuevos de M2+DISP_long (bloques inferior y superior; primera ejecución) | Review 37e, sección 3 |
| 10 | Los 10 bancos UPPER100 en curso | Review 37e, sección 3 |
| 11 | Bancos en tiempo real de las Tablas 4 y 5 | Tablas 4 y 5 |

**Responder además, de forma explícita:**
1. ¿Qué λ usa en cada bloque la **especificación principal del paper** (familias 1 y 2)? Es la que debe constar en el texto.
2. ¿Usan C1 y C3 **la misma λ en el centro**? Si no, ¿cuál usa cada uno y por qué?
3. ¿Coincide la λ del centro de 5,6234 con alguna regla preespecificada (por ejemplo, el mínimo de validación o un reescalado de 100)? Citar el documento de congelación correspondiente.
4. ¿Por qué la Review 34 concluyó que el bloque superior usaba 100 y el contrato A4B usa 0,3162? ¿Son familias distintas?

## B. Rama UPPER de los 20 bancos

**Corrección a la instrucción de la Review 37e, sección 3.** La regla que manda es que los bancos nuevos usen **la misma λ que su benchmark de historia común en cada bloque** (`M2_CH` para M2+DISP_long). El valor "λ_U = 100" de la Review 37e reproducía lo que dice el paper y puede no coincidir con esa regla.

1. **No abrir pérdidas** de ninguna versión del bloque superior hasta entregar la tabla A.
2. Si los bancos UPPER100 ya se están generando, **terminar y certificar** sin abrir pérdidas.
3. Con la tabla A:
   - **si `M2_CH` usa 0,3162 en el bloque superior:** la versión válida es la primera ejecución (0,3162). Los bancos UPPER100 se conservan como registro y no se usan;
   - **si `M2_CH` usa 100:** la versión válida es UPPER100;
   - **si `M2_CH` no tiene bancos del bloque superior:** informar y esperar.
4. ALL19 se recalcula con la rama UPPER válida.
5. No se borra ningún banco.

## C. Benchmark de la tendencia central en el centro

Según el informe, no existe un M2 sin la tendencia central con historia desde 1974Q4, 129 observaciones en el primer origen y la λ del centro de C1. Sin él no se puede calcular la contribución propia de la tendencia central en el centro.

**Autorizado, condicionado al resultado de la sección A:**
- **9 bancos:** M2 sin ninguna medida de proyecciones, cuantiles Q30–Q70;
- especificación **idéntica a `A4B_M2_SEP`** (familia 5) salvo la columna de la tendencia central: misma historia, panel, λ por cuantil, reloj, tratamiento de Hidden Dissent (ausente) y contrato de crecimiento corriente;
- **630 forecasts.**

**Condiciones:**
- **Solo si la tabla A confirma que C1 usa en el centro una λ distinta de la de `M2_CH`.** Si C1 usa la misma λ que `M2_CH`, el benchmark ya existe (`M2_CH`): usarlo y no estimar.
- Secuencia obligatoria:
  1. comprobación sin estimar, con la geometría 129 = 96 + 33 sin la columna de la medida y la identidad contractual con `A4B_M2_SEP` en todo lo demás;
  2. generación con las pérdidas cerradas;
  3. certificación estructural;
  4. pérdidas.

**Entregar con estos bancos**, con ganancia, d̄, HLN bilateral, intervalo HAC al 95 % y bootstrap con L=4:
- la contribución propia de la tendencia central en el centro (M2+CT_long frente al nuevo M2);
- la ganancia de Hidden Dissent frente a ese M2 sin proyecciones en el centro, para la columna "sin proyecciones" comparable con C1.

## D. Columna "sin proyecciones" de la Tabla 9

Con el benchmark de historia común que corresponda a cada contraste (sección A), entregar la ganancia de Hidden Dissent **sin proyecciones** con la misma historia y la misma λ:
- **centro:** frente al benchmark comparable con C1 (sección C) y frente a `M2_CH`, comparable con C3 (el +6,31 % del informe, con su inferencia completa);
- **bloque inferior:** frente a `M3_CH`, comparable con C2 y C4, sobre los 70 objetivos.

Cada uno con ganancia, d̄, HLN unilateral y bilateral, HAC al 95 %, bootstrap con L=4, 6 y 8, y W/L.

## E. Qué NO hacer

- No modificar C1–C4, sus familias de Holm ni su lectura.
- No reajustar λ en ninguna familia existente: aquí solo se documenta qué λ usó cada una.
- No abrir pérdidas de la rama UPPER antes de la sección A.
- No estimar los 9 bancos de la sección C si `M2_CH` sirve como benchmark.
- Ninguna otra estimación fuera de las secciones B y C.

## F. Entregable, por orden

1. Tabla A y respuestas 1–4.
2. Decisión sobre la rama UPPER según la regla de B, y ALL19 recalculado.
3. Sección C: o bien "no hace falta" (C1 usa la λ de `M2_CH`), o bien la certificación de los 9 bancos y la contribución propia.
4. Sección D.
5. El resto de la Review 37e (secciones 2 y 3.1–3.2, y el coste de las sensibilidades) con la λ ya resuelta.

Más los CSV, hashes y `REPRODUCTION: PASS`.

---

*Nota para el cierre pre-envío (octubre 2026): de este addendum solo se necesita ahora la Tabla A (las once familias y sus columnas). Las secciones B–F ya se ejecutaron en su momento y no se reabren.*
