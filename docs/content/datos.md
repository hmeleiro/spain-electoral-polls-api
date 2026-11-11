---
title: "Datos y metodología"
description: "Qué contiene la API, cómo se normaliza y qué debes tener en cuenta al reutilizarla."
---

Spain Electoral Polls reúne encuestas electorales publicadas en fuentes abiertas. Un proceso ETL independiente extrae, limpia y normaliza los datos; esta API se limita a leer la base publicada y servirla de forma estable.

## Modelo de datos

La unidad principal es la **encuesta**. Cada encuesta se vincula con una elección y una encuestadora, conserva sus fechas de trabajo de campo y publicación y contiene uno o varios resultados por partido.

| Entidad | Contenido principal |
|---|---|
| Elección | Convocatoria, tipo, territorio y fecha prevista. |
| Encuesta | Encuestadora, medio, fechas, muestra, participación y fuente. |
| Resultado | Partido normalizado, voto estimado y horquilla de escaños. |
| Partido | Clave estable, nombre, sigla, color y orden de visualización. |
| Encuestadora | Clave estable, nombre normalizado y actividad pública. |

## Fechas

El final del trabajo de campo es preferible a la fecha de publicación para ordenar observaciones: representa mejor cuándo se recogieron las respuestas. El endpoint `/timeseries` aplica esa regla con `date_field=auto`, recurriendo a la publicación solo si falta el fin de campo.

## Calidad y publicación

Los endpoints públicos excluyen por defecto:

- encuestas marcadas como inactivas;
- registros cuya identidad está pendiente de revisión manual.

Esto evita que duplicados o coincidencias todavía no validadas aparezcan accidentalmente en aplicaciones públicas. Los parámetros `include_inactive` e `include_manual_review` existen para auditoría y análisis avanzados.

## Cómo interpretar una encuesta

Una estimación no es un resultado electoral ni una predicción por sí sola. Para interpretar una observación conviene considerar al menos:

1. las fechas del trabajo de campo;
2. el tamaño y diseño de la muestra;
3. la casa encuestadora y sus decisiones metodológicas;
4. el medio o entidad que publica el estudio;
5. la fuente original enlazada por la API.

## Procedencia y trazabilidad

Cuando la fuente lo proporciona, cada encuesta incluye `source_url` y `source_title`. Esos campos permiten volver a la publicación original. La API conserva además `first_seen_at`, que indica cuándo entró por primera vez el registro en el sistema; no debe confundirse con la fecha de publicación.

## Reutilización responsable

Al publicar análisis derivados, identifica Spain Electoral Polls como proveedor del dataset y conserva la atribución a la fuente original de cada estudio. Explica los filtros aplicados, la fecha de descarga y cualquier transformación posterior. Para visualización y exploración humana puedes usar el [dashboard de encuestas](https://polls.spainelectoralproject.com/).
