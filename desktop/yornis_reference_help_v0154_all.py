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
            ("Vía aérea superior (nasofaringe)","17 mm","±4 mm","Reducción del espacio nasofaríngeo; posible resistencia aérea aumentada o adenoides prominentes.","Dimensión nasofaríngea compatible con permeabilidad adecuada en esta proyección.","Espacio nasofaríngeo amplio; sin dato de estrechamiento en este nivel."),
            ("Vía aérea inferior (orofaringe)","12 mm","±3 mm","Estrechamiento orofaríngeo; posible disminución de la permeabilidad faríngea.","Relación orofaríngea dentro de la referencia clásica.","Espacio orofaríngeo amplio; valorar siempre junto con clínica respiratoria."),
            ("Interpretación funcional","Flujo aéreo adecuado","cualitativa","Puede asociarse con respiración oral, obstrucción relativa o compensación postural.","No sugiere estrechamiento cefalométrico evidente.","No implica por sí mismo mejor función; integrar con exploración clínica."),
            ("Relación con crecimiento","Compatible","cualitativa","Puede asociarse con patrón vertical aumentado y adaptación cráneo-cervical.","Sin repercusión cefalométrica evidente en esta medición aislada.","Hallazgo descriptivo; no sustituye estudios funcionales o de sueño."),
        ],
        "note":"Medidas bidimensionales orientativas; interpretar con postura, fase respiratoria y evaluación clínica/otorrinolaringológica.",
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
