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
        "source":"Solow B, Tallgren A. Head posture and craniofacial morphology. Am J Phys Anthropol. 1976;44(3):417-435. DOI 10.1002/ajpa.1330440306; Rocabado M. protocolo de análisis cráneo-cervical (referencia secundaria; trazabilidad bibliográfica incompleta para algunas distancias).",
        "rows":[
            ("SN-OPT","Sin umbral universal validado","No aplica","Describir el ángulo medido; no asignar flexión/extensión patológica por una cifra aislada.","Comparar solo con una cohorte y protocolo de adquisición equivalentes.","Describir el ángulo medido; no asignar flexión/extensión patológica por una cifra aislada."),
            ("SN-CVT","Sin umbral universal validado","No aplica","Describir la relación cráneo-cervical observada.","Comparar solo con una cohorte y protocolo de adquisición equivalentes.","Describir la relación cráneo-cervical observada."),
            ("OPT-CVT","Sin umbral universal validado","No aplica","Describir el ángulo entre tangentes; no inferir rectificación clínica por sí solo.","Comparar solo con una cohorte y protocolo de adquisición equivalentes.","Describir el ángulo entre tangentes; no inferir hiperlordosis clínica por sí solo."),
            ("Ángulo McGregor / odontoides","101°","±5°","Menor de 96°: desviación respecto a la referencia del protocolo Rocabado; no es diagnóstico.","96°–106°: intervalo orientativo del protocolo Rocabado.","Mayor de 106°: desviación respecto a la referencia del protocolo Rocabado; no es diagnóstico."),
            ("Espacio C0–C1","4–9 mm","Rango de protocolo","Menor de 4 mm: desviación del rango descrito; confirmar puntos y proyección.","4–9 mm: rango descrito en protocolo Rocabado.","Mayor de 9 mm: desviación del rango descrito; confirmar puntos y proyección."),
            ("Espacio C1–C2","Sin referencia verificada","No aplica","No clasificar con umbral en esta versión.","Registrar la medida si el protocolo está definido.","No clasificar con umbral en esta versión."),
            ("Triángulo hioideo","Descripción cualitativa","No aplica","Registrar posición y landmarks; no inferir función muscular aislada.","Describir el triángulo según el método y puntos definidos.","Registrar posición y landmarks; no inferir función muscular aislada."),
            ("Interpretación global","Descriptiva, no diagnóstica","No aplica","No diagnostica trastornos posturales, respiratorios ni cervicales.","Integrar con posición natural de cabeza y exploración clínica.","No diagnostica trastornos posturales, respiratorios ni cervicales."),
        ],
        "note":"Las normas de SN-OPT, SN-CVT y OPT-CVT varían entre cohortes y no se verificó una fuente primaria que respalde los antiguos cortes ±8°/±2°. Se retiran como límites universales. El ángulo McGregor–odontoides 101°±5° y C0–C1 4–9 mm se conservan como referencias de protocolo Rocabado, no como diagnóstico. La trazabilidad del material original debe completarse.",
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
