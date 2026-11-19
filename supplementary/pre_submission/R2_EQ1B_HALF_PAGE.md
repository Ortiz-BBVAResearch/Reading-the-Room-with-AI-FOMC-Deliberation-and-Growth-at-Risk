# R-2 sobre el objetivo EQ-1B

La comparación preespecificada R-2 está ejecutada sobre el objetivo final **ABG_H4_AVERAGE_NEXT4**, definido como la media del crecimiento entre t+1 y t+4. Se usaron 70 orígenes (2007Q4–2025Q1), 19 cuantiles y λ por bloque 0,562341 / 100 / 100, sin reselección. Las dos especificaciones generan 2.660 pronósticos sellados en total. Los benchmarks A1 M2/M3 se mantuvieron intactos.

Para M2, penalizar HD deja una ganancia de 0,032% en la pérdida agregada (42 victorias y 28 derrotas); HLN unilateral de mejora p=0,241 y bilateral p=0,481. Para M3, bloque bajo, la ganancia es 0,110% (41 victorias y 29 derrotas); p unilateral=0,247 y bilateral=0,494. Ambos IC HAC 95% incluyen cero. Los IC percentiles MBB con bloques 4, 6 y 8 también incluyen cero en ambos contrastes (10.000 réplicas, semilla 20260903). No hay evidencia estadística de mejora por penalizar la señal HD.

La retención mediana absoluta de β_HD es aproximadamente 6,8% (M2, bloque bajo), 7,0% (M3, bloque bajo) y 0,066% (centro). El bloque alto no se informa porque no está disponible el artefacto de coeficientes pareados de la especificación base; no se reestimó para completarlo. Se reutilizan los resultados ya abiertos y la inferencia ya calculada. El freeze de diseño conserva casillas de estado “NO” anteriores a la ejecución; el manifiesto nuevo documenta la discrepancia.
