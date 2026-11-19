# Cierre pre-envío JME — estado de comprobaciones

## Hallazgos y archivos

1. **Especificación principal, familias A1 #1–2:** λ inferior = 0,562341; centro = 100; superior = 100. Esta es la especificación que debe constar en el texto para M2/M2+HD y M3/M3+HD. La λ se lee de `lambda_mean` por cuantil en los bancos sellados; el objetivo L1 usa la suma primaria de pérdidas, sin reescalado por N.
2. **Tabla A de penalizaciones:** completada para las 11 familias del addendum (la familia 11 tiene dos filas: Tablas 4 y 5) en `penalties_by_family.csv`. Incluye historia de entrenamiento, primer origen, tamaño de muestra, unidad, fuentes, valores y SHA-256 de los vectores completos cuando hay 19 cuantiles. Las familias parciales se marcan como hash no computable; no se extrapoló un vector completo. Los metadatos `lambda_vector_sha256` de los workers no son el hash del vector canónico de 19 λ redondeadas a seis decimales.
3. **Respuestas a las cuatro preguntas del addendum:** (i) A1 principal usa 0,562341 / 100 / 100; (ii) C1 usa centro 100 y C3 centro 5,623413, por lo que no coinciden; (iii) 5,623413 corresponde a la regla secundaria preespecificada `BLOCK_VALIDATION_ARGMIN_SECONDARY` en el contrato Review34 A1 R1; la regla primaria de una desviación estándar selecciona 100; no es un reescalado de 100; (iv) Review34 mezcla familias: A1 principal tiene λ superior 100, mientras que el contrato A4B/C1 de historia común tiene λ superior 0,316228. `M2_CH` también usa 0,316228 arriba.
4. **Review37e, alcance:** se completó únicamente la Tabla A. De acuerdo con la nota del addendum, las secciones B–F ya se ejecutaron y no se reabrieron. No se abrieron pérdidas nuevas ni se generaron bancos.
5. **Dispersión — rama final, λ_U = 100:** se mantienen los resultados finales, en los CSV entregados sin cambios: `REVIEW37E_SECTION3_TABLE9_HD_DISP.csv` y `REVIEW37E_SECTION3_TABLE2_DISP.csv`. Las tres filas para el suplemento son:

| Comparación | Bloque | Ganancia % | d̄ (pérdida pinball) | p HLN | IC MBB 95 % (L=4; unidades de d̄) | Wins |
|---|---:|---:|---:|---:|---:|---:|
| HD sobre M2 + dispersión | All 19 | +4,69 | −0,031089 | 0,000089 (una cola, mejora) | [−0,045832; −0,016750] | 56/70 |
| Dispersión sobre M2 | All 19 | −6,01 | +0,037592 | 0,157238 (bilateral) | [−0,015663; +0,082870] | 13/70 |
| Dispersión sobre M2 | Upper | −6,34 | +0,034281 | 0,625119 (bilateral) | [−0,124117; +0,124059] | 10/70 |

Las ganancias, d̄, p HLN y wins proceden de las dos tablas anteriores. Los intervalos percentiles MBB (B=10.000, semilla 20260903) proceden de `REVIEW37E_SECTION3_TABLE9_HD_DISP_MBB.csv` y `REVIEW37E_SECTION3_TABLE2_DISP_MBB.csv`; no se recalcularon.
6. **Tabla H.3 / Review46:** certificación ejecutada. Los cinco CSV y el informe están en esta carpeta; resumen, método y discrepancias en `REPORT_review46.md`. La composición con controles reproduce el rango indicado (F=0,323 por reunión y 0,274 trimestral); la variante rotatoria no reproduce F=0,28 de forma estable. Vacantes arrojan β≈−0,00447 en 1994–2025 y F=1,283, β positivo en 1994–2007 y F=5,100 en 2008–2025. Las diferencias frente a referencia están cuantificadas en el informe. No se estimó segunda etapa.
7. **AH añadido a M2:** cálculo desde archivos sellados, 70 objetivos, pinball por cuantiles y HLN bilateral: LOWER −5,86306% (d̄=0,029799; p=0,210448), CENTER +4,18320% (d̄=−0,030372; p=0,001890), UPPER +0,78845% (d̄=−0,004274; p=0,786816); detalle en `f2_ah_m2_blocks.csv`.
8. **Modelo de lenguaje:** el identificador local `gpt-5.6-terra` coincide con el nombre público de OpenAI y su documentación lo registra como modelo de API. La documentación fecha el anuncio público de la familia el 9 de julio de 2026, pero no la revisión concreta usada en esta corrida. El protocolo local registra el alias, no una revisión fechada ni la fecha de invocación; no puede atribuirse una versión concreta.
9. **Historia por familia:** A1: primera observación 1973Q1, primer origen 2007Q4, N=136. `M2_CH`: primera observación 1974Q4, primer origen 2007Q4, N=129. Los valores completos por familia están en la tabla A.

## Archivos de Review46

- `first_stage_meeting.csv`, `first_stage_quarterly.csv`, `vacancies_quarterly.csv`, `board_roster.csv`, `person_fe.csv`, `REPORT_review46.md`.
- `person_fe.csv` contiene exclusivamente IDs seudónimos y valores agregados de efectos fijos; el archivo privado no fue copiado ni se reportan filas o nombres individuales.
- La lista de gobernadores se contrastó con la fuente oficial de la Reserva Federal, consultada el 27-10-2026: [Board of Governors, 1914–Present](https://www.federalreserve.gov/aboutthefed/bios/board/boardmembership.htm).

## Alcance

Se completaron los entregables solicitados en el v3 y las dos adiciones recibidas. No se reestimaron pronósticos ni se modificaron bancos de previsiones. Las secciones B–F del addendum Review37e no se reabrieron. El informe de Review46 debe leerse como reproducción de primeras etapas con las definiciones documentadas, no como certificación de un instrumento exógeno.

## Aclaración de trazabilidad de penalizaciones (follow-up)

- **Review37e, Tabla 2 (`DISP_long | M2_CH`):** el benchmark M2_CH de `outputs/sa6/construct_validation/review34/a4b_panel_spf/checkpoints/M2_CH_Q75_sealed.csv` hasta `M2_CH_Q95_sealed.csv` registra `lambda_mean=0.3162277660168379`; el challenger `M2_DISP_LONG70` de `outputs/sa6/construct_validation/review37e/forecasting/disp_m2_upper100/checkpoints/` registra `lambda_mean=100.0` en Q75–Q95. No existe un banco M2_CH Q75–Q95 con λ=100: `outputs/sa6/construct_validation/review37e/forecasting/m2_center100/checkpoints/` contiene solo cuantiles centrales. Por tanto, **UPPER y ALL19 no son comparaciones a penalización igual**. Mantener las celdas numéricas como descriptivas, pero corregir cualquier texto que las presente como ganancia incremental aislada de la dispersión; no retirar ni recalcular los resultados sellados.
- **Review37e, Tabla 9 (`HD | M2_CH + DISP_long`):** el brazo sin HD es `M2_DISP_LONG70` y el brazo HD es `M2_DISP_LONG70_HD`, ambos en `outputs/sa6/construct_validation/review37e/forecasting/disp_m2_upper100/checkpoints/`; en ambos, Q75–Q95 `lambda_mean=100.0`. La comparación de Tabla 9 mantiene la misma penalización alta entre sus dos brazos.
- **Tablas 4 y 5, tiempo real:** Q75–Q95 registra `lambda_mean=1.0` para los dos brazos `REALTIME_MATCHED` y `FINAL_MATCHED`, con y sin HD/NFCI, en `outputs/sa6/realtime_fredmd/rt1_sealed_test/checkpoints/` y `outputs/sa6/realtime_fredmd/rtm3_sealed_test/checkpoints/`. El contrato `outputs/sa6/protocol_b/b4_test_contract/ProtocolB_B4_Frozen_Test_Contract.csv` fija `lambda_mean=1.0` para bloque UPPER; los workers `scripts/sa6_rt1i_matched_test_worker.py` y `scripts/sa6_rtm3_test_worker.py` declaran que usan sin selección la lambda congelada B4/B2. Texto recomendado para C y las notas de Tablas 4–5: **«λ_U = 1 en ambos brazos de cada comparación; fijado por el diseño del ejercicio en tiempo real»**.
- La cercanía de las ganancias 1,109% y 1,103% puede describirse como similitud numérica, pero no como reproducción del bloque superior principal de Tabla 3: A1 principal usa λ_U=100, mientras que el ejercicio en tiempo real usa λ_U=1. Las filas adicionales `11-FV4` y `11-FV5` de `penalties_by_family.csv` documentan los dos bancos `FINAL_MATCHED`; no son familias nuevas del addendum.
- Hay bancos históricos con prefijo `FINAL_MATCHED` en `outputs/sa6/abg_target_correction/rtabg2_realtime_fredmd/` y `rtnfci2_realtime_fredmd_nfci/` que registran λ_U=100. No son los bancos sellados de `realtime_fredmd/rt1_sealed_test` y `rtm3_sealed_test` usados para las columnas de vintage final de Tablas 4–5, que registran λ_U=1.

## Penalizaciones pendientes — lectura de metadatos sellados

Se leyeron exclusivamente `lambda_mean` por cuantil y los metadatos de las previsiones selladas. No se reestimó ni se reabrió ningún banco. La referencia A1 principal es λ_L=0,562341, λ_C=100 y λ_U=100 para M2 y M3. Las penalizaciones por cuantil, las rutas y los valores leídos están en `penalties_by_family.csv`.

- **Review 42 — M2 + BB-DISP**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1; el M2 de comparación en Tabla 2 es A1 principal (λ_U=100).
- **Review 42 — M3 + BB-DISP**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1; el M2 de comparación en Tabla 2 es A1 principal (λ_U=100).
- **Review 42 — M2 + BB-DISP + HD**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1; el M2 de comparación en Tabla 2 es A1 principal (λ_U=100).
- **Review 42 — M3 + BB-DISP + HD**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1; el M2 de comparación en Tabla 2 es A1 principal (λ_U=100).
- **Tabla 2 — Balance of risks**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Insurance motive**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Salience**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Quantifier discount**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Verbosity / placebo**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — SPF dispersion**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Geopolitical risk**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Policy uncertainty**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — VIX**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Oil**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Tabla 2 — Attributed heterogeneity**: λ_L=0.562341; λ_C=100.000000; λ_U=100.000000. Sí: λ_U=100.000000 frente a λ_U=100 de A1 principal.
- **Review 40 — M2_GB**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1 principal.
- **Review 40 — M3_GB**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1 principal.
- **Review 40 — M2_GB_HD**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1 principal.
- **Review 40 — M3_GB_HD**: λ_L=0.562000; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1 principal.
- **R-2 — R2_HD**: λ_L=0.562341; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1 principal. En cada cuantil la señal focal y el bloque de panel reciben la misma λ; R-2 los penaliza conjuntamente por bloque.
- **R-2 — R2_NFCI_HD**: λ_L=0.562341; λ_C=100.000000; λ_U=1.000000. No: λ_U=1.000000 frente a λ_U=100 de A1 principal. En cada cuantil la señal focal y el bloque de panel reciben la misma λ; R-2 los penaliza conjuntamente por bloque.
- **Review 48 — I-M2 — PCEPI**: λ_L=100.000000; λ_C=100.000000; λ_U=0.316228. Sí: λ_U=0.316228 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M2 — PCEPILFE**: λ_L=100.000000; λ_C=100.000000; λ_U=1.000000. Sí: λ_U=1.000000 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M2_HD — PCEPI**: λ_L=100.000000; λ_C=100.000000; λ_U=0.316228. Sí: λ_U=0.316228 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M2_HD — PCEPILFE**: λ_L=100.000000; λ_C=100.000000; λ_U=1.000000. Sí: λ_U=1.000000 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M3 — PCEPI**: λ_L=100.000000; λ_C=100.000000; λ_U=0.316228. Sí: λ_U=0.316228 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M3 — PCEPILFE**: λ_L=100.000000; λ_C=100.000000; λ_U=1.000000. Sí: λ_U=1.000000 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M3_HD — PCEPI**: λ_L=100.000000; λ_C=100.000000; λ_U=0.316228. Sí: λ_U=0.316228 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-M3_HD — PCEPILFE**: λ_L=100.000000; λ_C=100.000000; λ_U=1.000000. Sí: λ_U=1.000000 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-SPF — PCEPI**: λ_L=100.000000; λ_C=100.000000; λ_U=0.316228. Sí: λ_U=0.316228 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-SPF — PCEPILFE**: λ_L=100.000000; λ_C=100.000000; λ_U=1.000000. Sí: λ_U=1.000000 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-SPF_HD — PCEPI**: λ_L=100.000000; λ_C=100.000000; λ_U=0.316228. Sí: λ_U=0.316228 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Review 48 — I-SPF_HD — PCEPILFE**: λ_L=100.000000; λ_C=100.000000; λ_U=1.000000. Sí: λ_U=1.000000 coincide con el benchmark de comparación para el mismo objetivo de inflación (I-M2 sin HD para la fila correspondiente).
- **Tabla 5 realtime — M3 + SPF dispersion**: λ_L=0.562341; λ_C=not banked in this universe; λ_U=not banked in this universe. Sí: λ_L=0.562341 coincide con M3 realtime sin señal (λ_L=0,562341); estos bancos no tienen cuantiles centrales ni altos.
- **Tabla 5 realtime — M3 + Geopolitical risk**: λ_L=0.562341; λ_C=not banked in this universe; λ_U=not banked in this universe. Sí: λ_L=0.562341 coincide con M3 realtime sin señal (λ_L=0,562341); estos bancos no tienen cuantiles centrales ni altos.
- **Tabla 5 realtime — M3 + Policy uncertainty**: λ_L=0.562341; λ_C=not banked in this universe; λ_U=not banked in this universe. Sí: λ_L=0.562341 coincide con M3 realtime sin señal (λ_L=0,562341); estos bancos no tienen cuantiles centrales ni altos.
- **Tabla 5 realtime — M3 + VIX**: λ_L=0.562341; λ_C=not banked in this universe; λ_U=not banked in this universe. Sí: λ_L=0.562341 coincide con M3 realtime sin señal (λ_L=0,562341); estos bancos no tienen cuantiles centrales ni altos.
- **Tabla 5 realtime — M3 + Oil**: λ_L=0.562341; λ_C=not banked in this universe; λ_U=not banked in this universe. Sí: λ_L=0.562341 coincide con M3 realtime sin señal (λ_L=0,562341); estos bancos no tienen cuantiles centrales ni altos.

## Confirmaciones finales — R-2 y Review 45

- **R-2:** la inferencia de `scripts/sa6_protocol_b_r2_open_inference.py` empareja `R2_HD` con `outputs/sa6/protocol_b/b5_sealed_test/checkpoints/R2_Q75_sealed.csv`–`R2_Q95_sealed.csv`, y `R2_NFCI_HD` con los archivos `R2_NFCI_Q75_sealed.csv`–`R2_NFCI_Q95_sealed.csv` de la misma ruta; sus λ_U son 1.0, no los bancos A1 de `abg4_sealed_test` (λ_U=100). **Las cifras citadas no corresponden al objetivo corregido EQ-1B:** los workers de esos bancos usan el crecimiento de PIB del trimestre t+4, mientras EQ-1B es el promedio de crecimiento de t+1 a t+4. No presentar esas cifras como estimadas sobre EQ-1B.

- **Review 45 / Tabla H.1:** las ocho filas añadidas registran λ_L/λ_C/λ_U de los bancos M2 (19 cuantiles) y M3 (solo bloque inferior, cinco cuantiles). El benchmark es el M2/M3 sellado del paper v4.25 restringido en `outputs/sa6/review45/data_paper/dist_v425_targets_2008Q4_2018Q4.json` a 41 objetivos; A1 lleva λ_U=100. Los ocho bancos focales usan λ=(0,562341; 100; 100), aunque los bancos M3 solo tienen λ_L efectivamente archivada.


## R-2 sobre EQ-1B y ledger de objetivos (2026-10-29)

La comparación R-2 sobre `ABG_H4_AVERAGE_NEXT4` ya estaba estimada, abierta una vez y acompañada por inferencia HAC/HLN y MBB (L=4,6,8). No se duplicó la corrida ni se tocó A1. Los archivos `R2_EQ1B_RESULTS.csv`, `R2_EQ1B_HALF_PAGE.md` y `R2_EQ1B_MANIFEST.json` resumen la evidencia; `PAPER_OBJECTIVE_LEDGER.csv` inventaría Tablas 2–9, Figuras 2–3 y Suplemento C–M, con la ruta de metadatos disponible. El ledger marca como **anterior t+4** las ventanas de Tabla 6 y la reconstrucción heredada de Figura 3; marca Tabla 4–5 con la ruta histórica de Protocol B, pendiente de reconciliar con el banco de tiempo real que se use en la versión final. Figura 2 y Suplemento E están confirmados en EQ-1B por metadatos de los bancos de descomposición. Las filas no certificadas deben resolverse antes de citar el ledger como mapa final del manuscrito.

El freeze A3 conserva los campos “FORECASTS RUN: NO” y “PERFORMANCE OPENED: NO” aunque existen los bancos, first-open e inferencia; esta discrepancia de estado se documenta en el manifiesto R-2. Retención de coeficiente por bloque superior queda no disponible porque faltan coeficientes pareados del benchmark primario; no se reestimó.
