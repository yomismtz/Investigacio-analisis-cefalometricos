from __future__ import annotations

import yornis_reference_help_v0154 as _base

_EXTRA_TABLES = [
    {
        "id":"powell","title":"ANÁLISIS DE POWELL","subtitle":"Perfil blando · referencia estética orientativa","first":"Ángulo o plano",
        "source":"Powell N, Humphreys B. Proportions of the Aesthetic Face. Thieme-Stratton; 1984. Referencia estética orientativa, a correlacionar con sexo, edad y etnia.",
        "rows":[
            ("Ángulo nasofrontal","122°","±7°","Ángulo más agudo; glabela y/o dorso nasal relativamente más prominentes.","Transición armónica frente–nariz.","Ángulo más obtuso; región glabelar o puente nasal más planos."),
            ("Ángulo nasofacial","36°","±4°","Nariz menos proyectada o mentón relativamente más prominente.","Proyección nasal equilibrada respecto al perfil facial.","Nariz más proyectada o mentón relativamente retrusivo."),
            ("Ángulo nasomental","128°","±6°","Mayor prominencia nasal y/o mentoniana; perfil más tenso o angulado.","Relación armónica nariz–mentón.","Perfil más plano o menos definido; posible menor proyección mentoniana."),
            ("Ángulo mentocervical","87°","±7°","Ángulo cervicomentoniano más cerrado; mentón/cuello más agudos.","Contorno cuello–mentón estéticamente equilibrado.","Ángulo más abierto; posible retrusión mentoniana o plenitud submentoniana."),
            ("Interpretación global","Perfil armónico","cualitativa","Rasgos más agudos o prominentes en el perfil blando.","Proporciones faciales agradables dentro de la referencia clásica.","Rasgos más obtusos o suavizados del perfil."),
        ],
    },
    {
        "id":"via_aerea","title":"ANÁLISIS DE VÍA AÉREA","subtitle":"McNamara · referencia orientativa","first":"Ángulo o plano",
        "source":"McNamara JA Jr. A method of cephalometric evaluation. Am J Orthod. 1984;86(6):449-469. DOI 10.1016/S0002-9416(84)90352-X.",
        "rows":[
            ("Vía aérea superior (nasofaringe)","Adultos: 17.4 mm; aumenta con edad","♀ ±3.4 / ♂ ±4.3 mm","≤5 mm: indicador de posible compromiso, no diagnóstico; requiere valoración otorrinolaringológica.","Media adulta Ann Arbor; la deglución/posición del paladar puede limitar la medición.","Un valor alto aislado no confirma permeabilidad funcional."),
            ("Vía aérea inferior (orofaringe)","10–12 mm; cambio escaso con edad","Adultos: ♀ 11.3 ±3.3 / ♂ 13.5 ±4.3 mm","Un valor menor a la media no es notable por sí solo y no demuestra obstrucción.","Referencia descrita por McNamara; correlacionar con edad, postura y clínica.",">15 mm puede sugerir posición anterior de lengua; no equivale a mejor función."),
            ("Interpretación funcional","Indicador cefalométrico bidimensional","No es prueba funcional","La radiografía lateral no diagnostica apnea, obstrucción ni respiración oral.","Describe dimensiones en una proyección y momento determinados.","No permite inferir flujo aéreo normal ni ausencia de trastorno."),
            ("Relación con crecimiento","Interpretar con edad y desarrollo","No aplica","No inferir patrón vertical o maduración a partir de una sola medida faríngea.","Correlacionar con morfología, postura y exploración clínica.","No usar como predictor aislado de crecimiento o sueño."),
        ],
        "note":"McNamara advierte que la telerradiografía es una representación 2D de una estructura 3D; la deglución puede alterar el paladar blando. ≤5 mm en faringe superior solo indica posible compromiso; el diagnóstico requiere valoración otorrinolaringológica. En faringe inferior, un valor bajo no es notable por sí solo; >15 mm puede reflejar posición anterior de lengua.",
    },
    {
        "id":"craneo_cervical","title":"ANÁLISIS CRÁNEO-CERVICAL","subtitle":"Solow–Tallgren / Rocabado · referencias orientativas","first":"Ángulo o plano",
        "source":"Solow B, Tallgren A. Head posture and craniofacial morphology. Am J Phys Anthropol. 1976;44(3):417-435. DOI 10.1002/ajpa.1330440306; Sandoval P et al. Rev Med Chil. 1999;127(5):547-555; Rocabado M.",
        "rows":[
            ("SN-OPT","102°","±8°","Menor extensión cráneo-cervical; cabeza relativamente más flexionada.","Posición de la cabeza equilibrada respecto a la columna cervical superior.","Mayor angulación cráneo-cervical; tendencia a postura de cabeza adelantada/extensión relativa."),
            ("SN-CVT","109°","±8°","Relación cráneo-cervical más cerrada; menor extensión global.","Balance cráneo-cervical dentro de la referencia orientativa.","Mayor extensión de la cabeza respecto a la columna cervical."),
            ("OPT-CVT","7°","±2°","Rectificación relativa de la columna cervical superior.","Curvatura cervical compatible con alineación funcional.","Mayor curvatura/discordancia entre cervical superior e inferior."),
            ("Ángulo McGregor / odontoides","101°","±5°","Compatible con postura de cabeza adelantada o flexión relativa.","Relación occípito-cervical armónica.","Compatible con extensión cefálica relativa."),
            ("Espacio C0–C1","4–9 mm","cualitativa","Disminución del espacio suboccipital; posible compensación postural.","Espacio posterior funcional conservado.","Apertura relativa del espacio suboccipital."),
            ("Espacio C1–C2","4–9 mm","cualitativa","Disminución del espacio atlantoaxoideo posterior.","Relación C1–C2 funcional conservada.","Aumento relativo del espacio posterior C1–C2."),
            ("Triángulo hioideo","Compatible / positivo","cualitativa","Posición hioidea superior o alterada; posible adaptación muscular/postural.","Posición hioidea funcionalmente equilibrada.","Posición hioidea más inferior; valorar en conjunto con postura y vía aérea."),
            ("Interpretación global","Equilibrio cráneo-cervical","cualitativa","Tendencia a flexión, rectificación o reducción de espacios posteriores.","Postura cefálica y cervical armónica en esta proyección.","Tendencia a extensión cefálica o angulación cráneo-cervical aumentada."),
        ],
        "note":"Referencias orientativas; correlacionar con postura natural, técnica radiográfica y clínica funcional.",
    },
    {
        "id":"lordosis_c1_c7","title":"LORDOSIS CERVICAL C1–C7","subtitle":"Referencia orientativa postural","first":"Ángulo o plano",
        "source":"Referencias cefalométricas cervicales y la referencia usada por la app (media 40°, rango 35–45°).",
        "rows":[
            ("Ángulo de lordosis C1–C7","40°","±5°","Lordosis disminuida; compatible con rectificación. Si el valor es negativo, considerar inversión/cifosis.","Curvatura cervical dentro del rango orientativo fisiológico.","Lordosis aumentada; compatible con hiperlordosis cervical."),
            ("Rango orientativo","35°–45°","referencial","Por debajo de 35°: valorar postura, técnica radiográfica y compensación cervical.","Entre 35° y 45°: referencia usada por la app.","Por encima de 45°: mayor curvatura cervical."),
            ("Implicación postural","Curvatura funcional","cualitativa","Puede asociarse con postura de cabeza adelantada, rigidez o adaptación respiratoria.","Compatible con alineación cervical fisiológica en esta proyección.","Puede asociarse con extensión cefálica y adaptación postural."),
            ("Interpretación clínica","Orientativa","cualitativa","Requiere correlación con síntomas, función y resto del análisis cráneo-cervical.","No sugiere alteración marcada de la curva en esta medición aislada.","Confirmar con clínica y revisar el resto de la columna cervical."),
        ],
        "note":"Outcome orientativo; no sustituye evaluación radiológica específica.",
    },
]

existing = {t.get('id') for t in _base.TABLES}
for item in _EXTRA_TABLES:
    if item['id'] not in existing:
        _base.TABLES.append(item)

TABLES = _base.TABLES
DISCLAIMER = _base.DISCLAIMER
COLORS = _base.COLORS
validate_tables = _base.validate_tables
open_reference_help = _base.open_reference_help
attach_help_button = _base.attach_help_button
