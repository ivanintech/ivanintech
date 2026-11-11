"""Radar de noticias IA desde YouTube — v2 (nov-2026).

Sustituye a `aggregated_news`, muerto desde jun-2025: dependía de GNews + Event
Registry (sin key) y Gemini (suspendida), y quedó sirviendo basura de prensa local.

Diseño v2 frente a la v1:
  1. Structured Outputs (`json_schema` estricto) -> se acaba el parseo defensivo.
     Verificado: DeepSeek-V4-Flash acepta strict=true en DeepInfra.
  2. Modelo 3x más barato: DeepSeek-V4-Flash ($0.09/$0.18 por M) vs V3.1-Terminus
     ($0.27/$0.95). Coste medido: ~$0.00006 por noticia.
  3. Score calibrado con ANCLAS explícitas (técnica rubric+anchor, 2026) en vez de
     "1-5" a secas, que el modelo colapsaba a 3.
  4. Filtro previo `es_noticia`: descarta opinión pura y clickbait antes de insertar.
  5. `sort=newest` en channel-videos (changelog ScrapeCreators 27-oct-2026).

Todo por HTTP directo: NO hay ~/.hermes ni scripts locales en Render.
Contrato: (AsyncSession, User) -> nº de noticias publicadas.
"""
from __future__ import annotations

import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.models.news_item import NewsItem
from app.db.models.user import User

logger = logging.getLogger(__name__)

SC_BASE = "https://api.scrapecreators.com"
LLM_URL = "https://api.deepinfra.com/v1/openai/chat/completions"

# --- Parámetros del radar -----------------------------------------------------
# Canales curados: los tres originales dan el pulso técnico; el resto amplía
# cobertura (lanzamientos de modelos, open source, investigación, robótica).
CANALES = [
    "@aiexplained-official",
    "@matthew_berman",
    "@Fireship",
    "@TwoMinutePapers",
    "@bycloud",
    "@YannicKilcher",
    "@GoogleDeepMind",
]
UMBRAL_OUTLIER = 1.8      # veces la mediana del canal
MAX_POR_EJECUCION = 4
MIN_QUOTES = 3
VENTANA_DIAS = 21         # 21 días: el RSS trae 15 vídeos que abarcan ~2 meses,
                          # así que una ventana de 14 dejaba fuera outliers reales.
                          # Con 21 se compensa frescura y volumen.
LLM_MODEL = "deepseek-ai/DeepSeek-V4-Flash"

# Fallos acumulados de ScrapeCreators durante la ejecución. Se vacía al empezar
# y se lee al final para distinguir "no hay novedades" de "la fuente está caída".
_SC_FALLOS: list[tuple[str, str]] = []

# --- Rúbrica con anclas -------------------------------------------------------
# Sin anclas el modelo devolvía casi todo 3. Con ejemplos puntuados discrimina.
RUBRICA = """Escala de relevance_rating, con anclas de referencia:
5 = lanzamiento o cambio mayor y verificable de un modelo/empresa grande
    (ej.: "OpenAI lanza GPT-6", "Google cierra Gemini a terceros").
4 = avance técnico relevante o movimiento estratégico confirmado
    (ej.: "Anthropic duplica el contexto útil", "Meta abre pesos de Llama").
3 = análisis de tendencia con datos propios o entrevista con información nueva
    (ej.: "Cómo cambia el trabajo de ingeniero en 2027").
2 = opinión, reacción o predicción personal sin hechos nuevos
    (ej.: "Por qué creo que la IA generativa está sobrevalorada").
1 = contenido menor: reacción a otro vídeo, rumores sin fuente, clickbait.
Puntúa con estas anclas. NO uses 3 por defecto: si dudas entre 3 y 4, elige
según haya o no un hecho verificable."""

SECTORES = ["Modelos", "Hardware", "Open Source", "Investigación", "Regulación",
            "Producto", "Empresa", "Robótica"]

ESQUEMA = {
    "type": "object",
    "properties": {
        "es_noticia": {
            "type": "boolean",
            "description": ("true si el vídeo aporta un hecho concreto: lanzamiento, "
                            "versión, paper, dato propio, entrevista o movimiento "
                            "confirmado. false solo si es opinión pura, reacción a otro "
                            "vídeo o clickbait sin ningún hecho nuevo."),
        },
        "title": {"type": "string", "maxLength": 120},
        "description": {"type": "string"},
        "why_matters": {"type": "string"},
        "relevance_rating": {"type": "integer", "minimum": 1, "maximum": 5},
        "sentiment": {"type": "string"},
        "sectors": {"type": "array", "items": {"type": "string", "enum": SECTORES}},
    },
    "required": ["es_noticia", "title", "description", "why_matters",
                 "relevance_rating", "sentiment", "sectors"],
    "additionalProperties": False,
}


def _key(nombre: str) -> str | None:
    """Lee la key de settings (viene del .env de Render/local)."""
    return getattr(settings, nombre, None) or None


def _num(txt) -> int:
    """'3.7K' / '1.2M' / 1234 -> int."""
    if isinstance(txt, (int, float)):
        return int(txt)
    if not txt:
        return 0
    s = str(txt).replace(",", "").strip().upper()
    try:
        for suf, mult in (("B", 1_000_000_000), ("M", 1_000_000), ("K", 1_000)):
            if s.endswith(suf):
                return int(float(s[:-1]) * mult)
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def _mediana(valores: list[int]) -> int:
    v = sorted(x for x in valores if x > 0)
    if not v:
        return 0
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) // 2


async def _sc_get(client: httpx.AsyncClient, path: str, params: dict) -> dict | None:
    """GET a ScrapeCreators. None si falla (nunca rompe el job).

    OJO: un None aquí NO significa "no hay noticias". Puede ser una key muerta,
    créditos agotados (402) o un 5xx. Quien llame debe distinguirlo; si no, el
    job reporta "sin outliers" cuando en realidad está caído. El estado real se
    acumula en `_SC_FALLOS` para que el punto de entrada lo pueda propagar.
    """
    key = _key("SCRAPECREATORS_API_KEY")
    if not key:
        logger.error("Falta SCRAPECREATORS_API_KEY en la configuración")
        _SC_FALLOS.append(("sin_key", "falta SCRAPECREATORS_API_KEY"))
        return None
    try:
        r = await client.get(f"{SC_BASE}{path}", params=params,
                             headers={"x-api-key": key}, timeout=120.0)
        if r.status_code != 200:
            logger.warning(f"ScrapeCreators {path} -> {r.status_code}: {r.text[:160]}")
            motivo = "sin_creditos" if r.status_code in (402, 403) else f"http_{r.status_code}"
            _SC_FALLOS.append((motivo, f"{path} -> {r.status_code}"))
            return None
        return r.json()
    except Exception as e:  # noqa: BLE001
        logger.error(f"ScrapeCreators {path} excepción: {e}")
        _SC_FALLOS.append(("excepcion", f"{path}: {e}"))
        return None


def _extraer_outliers(videos: list[dict], solo_recientes: bool = False) -> list[dict]:
    """Vídeos que superan UMBRAL_OUTLIER veces la mediana del canal.

    `solo_recientes` limita el cálculo a la ventana VENTANA_DIAS. Con el RSS
    solo llegan 15 vídeos que pueden abarcar meses; sin este filtro la mediana
    se contamina con vídeos viejos y el outlier de la semana queda enterrado.
    """
    if solo_recientes:
        corte = datetime.now(timezone.utc) - timedelta(days=VENTANA_DIAS)
        filtrados = []
        for v in videos:
            f = v.get("publishedTime") or v.get("publishedAt") or v.get("date")
            if not f:
                continue
            try:
                if datetime.fromisoformat(str(f).replace("Z", "+00:00")) >= corte:
                    filtrados.append(v)
            except (ValueError, TypeError):
                continue
        videos = filtrados

    if len(videos) < 5:
        return []
    views = [_num(v.get("viewCountInt") or v.get("viewCount") or v.get("views"))
             for v in videos]
    mediana = _mediana(views)
    if mediana <= 0:
        return []

    salida = []
    for v, views_i in zip(videos, views):
        if views_i <= 0:
            continue
        ratio = views_i / mediana
        if ratio < UMBRAL_OUTLIER:
            continue
        vid = v.get("id") or v.get("videoId")
        url = v.get("url") or (f"https://www.youtube.com/watch?v={vid}" if vid else None)
        if not url:
            continue
        salida.append({
            "url": url,
            "id": vid,
            "title": v.get("title") or "",
            "views": views_i,
            "ratio": ratio,
            "thumbnail": v.get("thumbnail"),
            "description": (v.get("description") or "")[:600],
            "date": v.get("publishedTime") or v.get("publishedAt") or v.get("date"),
        })
    return salida


def _normalizar_comentarios(raw: list[dict]) -> list[dict]:
    """Schema real: texto en `content`, autor objeto, likes en engagement.likes."""
    salida = []
    for c in raw:
        autor = c.get("author")
        nombre = (autor.get("name") if isinstance(autor, dict) else autor) or "Anónimo"
        eng = c.get("engagement") or {}
        likes = eng.get("likes") if isinstance(eng, dict) else None
        if likes is None:
            likes = c.get("likeCount") or c.get("likes") or 0
        texto = c.get("content") or c.get("text") or ""
        if texto:
            salida.append({"a": str(nombre), "t": str(texto), "likes": _num(likes)})
    return salida


def _quotes(comentarios: list[dict], maximo: int = 3) -> list[dict]:
    validos = [c for c in comentarios if (c.get("t") or "").strip()]
    validos.sort(key=lambda c: -(c.get("likes") or 0))
    return [{"a": (c.get("a") or "Anónimo")[:60],
             "t": c["t"].strip()[:280],
             "likes": c.get("likes") or 0} for c in validos[:maximo]]


# --- Fuente de respaldo sin coste --------------------------------------------
# ScrapeCreators devuelve 402 cuando se agotan los créditos. El feed RSS público
# de YouTube trae los 15 vídeos recientes CON sus views y sin API key, así que
# sirve como respaldo permanente. Sin esto, el radar moría en silencio.
_NS_RSS = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}

# @handle -> channel_id. El feed exige el ID; resolverlo por HTML falla a menudo
# (YouTube responde 302 al scraping), así que van fijados.
CHANNEL_IDS = {
    "@aiexplained-official": "UCNJ1Ymd5yFuUPtn21xtRbbw",
    "@matthew_berman": "UCawZsQWqfGSbCI5yjkdVkTA",
    "@Fireship": "UCsBjURrPoezykLs9EqgamOA",
    "@TwoMinutePapers": "UCbfYPyITQ-7l4upoX8nvctg",
    "@bycloud": "UCgfe2ooZD3VJPB6aJAnuQng",
    "@YannicKilcher": "UCZHmQk67mSJgfCCTn7xBfew",
    "@GoogleDeepMind": "UCP7jMXSY2xbc3KCAE0MHQ-A",
}


async def _videos_via_rss(client: httpx.AsyncClient, canal: str) -> list[dict] | None:
    """Vídeos recientes del canal por RSS. None = no se pudo leer.

    Distinguir None de [] importa: [] es "canal vacío" y None es "fallo".
    """
    cid = CHANNEL_IDS.get(canal)
    if not cid:
        return None
    try:
        r = await client.get(
            f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}",
            headers={"User-Agent": "Mozilla/5.0"}, timeout=30.0,
        )
        if r.status_code != 200:
            logger.warning(f"RSS {canal} -> {r.status_code}")
            return None
        root = ET.fromstring(r.text)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"RSS {canal} excepción: {e}")
        return None

    salida = []
    for entry in root.findall("atom:entry", _NS_RSS):
        vid = entry.findtext("yt:videoId", default="", namespaces=_NS_RSS)
        stats = entry.find("media:group/media:statistics", _NS_RSS)
        views = _num(stats.get("views")) if stats is not None else 0
        thumb = None
        grupo = entry.find("media:group", _NS_RSS)
        if grupo is not None:
            th = grupo.find("media:thumbnail", _NS_RSS)
            if th is not None:
                thumb = th.get("url")
        salida.append({
            "id": vid,
            "url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
            "title": (entry.findtext("atom:title", default="", namespaces=_NS_RSS) or "")[:120],
            "views": views,
            "viewCountInt": views,
            "thumbnail": thumb,
            "date": entry.findtext("atom:published", default="", namespaces=_NS_RSS),
            "description": "",
        })
    return salida


async def _analizar(canal: str, titulo: str, views: int, ratio: float,
                    comentarios: list[dict], descripcion: str) -> dict | None:
    """Un solo paso LLM con salida estructurada garantizada."""
    key = _key("DEEPINFRA_API_KEY")
    if not key:
        logger.error("Falta DEEPINFRA_API_KEY en la configuración")
        return None

    top = "\n".join(f"- ({c['likes']} likes) {c['t'][:200]}"
                    for c in comentarios[:8])
    prompt = f"""Analiza este vídeo de YouTube y decide si merece ser noticia.

CANAL: {canal}
TÍTULO: {titulo}
VIEWS: {views:,} ({ratio:.1f}x la media del canal)
DESCRIPCIÓN: {descripcion[:1200] or '(vacía)'}

COMENTARIOS MÁS VOTADOS:
{top or '(sin comentarios)'}

{RUBRICA}

REGLAS:
- El titular habla del TEMA (modelo, empresa, hecho), NUNCA del canal ni de sus views.
  "AI Explained bate récords" es incorrecto.
- No inventes cifras ni nombres que no aparezcan arriba.
- es_noticia = false SOLO si no hay ningún hecho nuevo (opinión, reacción a otro
  vídeo, clickbait). Un análisis con datos propios o una entrevista SÍ es noticia,
  aunque el tema sea un rumor: en ese caso puntúa bajo (1-2) pero publícalo.
- Si sospechas que el hecho no es verificable, dilo en description y baja el score."""

    body = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content":
             "Eres editor de una web técnica sobre IA en español. No inventas datos. "
             "Escribes para lectores que ya saben lo básico."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 900,
        "temperature": 0.3,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "noticia", "strict": True, "schema": ESQUEMA},
        },
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(LLM_URL,
                                  headers={"Authorization": f"Bearer {key}"},
                                  json=body)
        r.raise_for_status()
        cuerpo = r.json()
        datos = json.loads(cuerpo["choices"][0]["message"]["content"])
        coste = (cuerpo.get("usage") or {}).get("estimated_cost") or 0
        logger.info(f"LLM ok (${coste:.6f})")
        return datos
    except Exception as e:  # noqa: BLE001
        logger.error(f"LLM error: {e}")
        return None


async def _existe(db: AsyncSession, url: str) -> bool:
    r = await db.execute(select(NewsItem.id).where(NewsItem.url == url).limit(1))
    return r.scalar_one_or_none() is not None


async def fetch_and_store_news(db: AsyncSession, user: User):
    """Punto de entrada del job: busca outliers nuevos y los publica.

    Devuelve un dict con el resultado REAL, no solo el número de publicadas:
        {"publicadas": int, "candidatos": int, "canales_ok": int,
         "canales_fallidos": int, "motivo": str | None}
    `motivo` != None significa que la fuente falló y el 0 NO es "sin novedades".
    """
    corte = datetime.now(timezone.utc) - timedelta(days=VENTANA_DIAS)
    candidatos: list[dict] = []
    _SC_FALLOS.clear()
    canales_ok = 0
    canales_fallidos = 0

    async with httpx.AsyncClient() as client:
        for canal in CANALES:
            # channel-videos NO acepta cache_max_age: solo handle/channelId/sort.
            d = await _sc_get(client, "/v1/youtube/channel-videos",
                              {"handle": canal.lstrip("@"), "sort": "newest"})
            videos = (d.get("videos") or d.get("items") or []) if d else []

            # Respaldo gratuito: si ScrapeCreators no devuelve nada (típicamente
            # 402 sin créditos), se lee el RSS público. Así el radar sigue vivo
            # sin pagar y el fallo de la API deja de ser un punto único.
            if not videos:
                rss = await _videos_via_rss(client, canal)
                if rss:
                    videos = rss
                    logger.info(f"Radar {canal}: {len(rss)} vídeos vía RSS (respaldo gratis)")
                elif rss is None and d is None:
                    logger.warning(f"Radar: {canal} ILEGIBLE (ni API ni RSS)")
                    canales_fallidos += 1
                    continue

            if not videos:
                logger.warning(f"Radar: {canal} sin vídeos")
                canales_fallidos += 1
                continue

            canales_ok += 1
            # La mediana se calcula sobre los 15 vídeos del RSS (referencia
            # estable del canal); la ventana temporal se aplica al publicar.
            outs = _extraer_outliers(videos)
            logger.info(f"Radar {canal}: {len(videos)} vídeos, {len(outs)} outliers")
            for o in outs:
                o["canal"] = canal
                candidatos.append(o)

    candidatos.sort(key=lambda c: -c["ratio"])
    candidatos = candidatos[:MAX_POR_EJECUCION]
    logger.info(f"Radar: {len(candidatos)} candidatos tras filtrar")

    publicadas = 0
    async with httpx.AsyncClient() as client:
        for c in candidatos:
            url = str(c["url"])
            try:
                if await _existe(db, url):
                    logger.info(f"Ya existe, se omite: {url}")
                    continue

                # Descartar lo viejo ANTES de gastar LLM: el RSS trae hasta 2
                # meses atrás y no queremos publicar noticias rancias como si
                # fueran de hoy. `corte` estaba calculado pero sin usar.
                fecha_v = c.get("date")
                if fecha_v:
                    try:
                        if datetime.fromisoformat(str(fecha_v).replace("Z", "+00:00")) < corte:
                            logger.info(f"Descartada por antigüedad ({str(fecha_v)[:10]}): {url}")
                            continue
                    except (ValueError, TypeError):
                        pass

                # comments solo acepta url/order/continuationToken (sin limit).
                cm = await _sc_get(client, "/v1/youtube/video/comments",
                                   {"url": url, "order": "top"})
                comentarios = _normalizar_comentarios((cm or {}).get("comments") or [])
                # Los comentarios enriquecen el análisis, pero dependen de
                # ScrapeCreators. Sin créditos esto descartaba el 100% de las
                # noticias; ahora se degrada al título, que el RSS ya trae.
                if len(comentarios) < MIN_QUOTES:
                    logger.info(f"Pocos comentarios ({len(comentarios)}), se enriquece con el título: {url}")

                datos = await _analizar(c["canal"], c["title"], c["views"],
                                        c["ratio"], comentarios, c["description"])
                if not datos or not datos.get("title"):
                    logger.warning(f"LLM sin datos válidos para {url}")
                    continue
                if not datos.get("es_noticia"):
                    logger.info(f"No es noticia, se descarta: {datos.get('title', '')[:60]}")
                    continue

                thumb = c.get("thumbnail")
                if not thumb and c.get("id"):
                    thumb = f"https://i.ytimg.com/vi/{c['id']}/hq720.jpg"

                pub = datetime.now(timezone.utc)
                if c.get("date"):
                    try:
                        pub = datetime.fromisoformat(str(c["date"]).replace("Z", "+00:00"))
                    except Exception:  # noqa: BLE001
                        pub = datetime.now(timezone.utc)

                # Se inserta con el modelo ORM directo: NewsItemCreate convierte
                # url/imageUrl a HttpUrl, que aiosqlite no sabe bindear.
                db.add(NewsItem(
                    title=datos["title"][:200],
                    url=url,
                    sourceName=c["canal"],
                    description=datos.get("description"),
                    imageUrl=thumb,
                    publishedAt=pub,
                    sectors=json.dumps(datos.get("sectors") or [], ensure_ascii=False),
                    is_community=False,
                    relevance_rating=float(datos.get("relevance_rating") or 3),
                    audience_quotes=json.dumps(_quotes(comentarios), ensure_ascii=False),
                ))
                await db.commit()
                publicadas += 1
                logger.info(f"Publicada ({c['ratio']:.1f}x, "
                            f"{datos.get('relevance_rating')}): {datos['title'][:70]}")

            except IntegrityError:
                await db.rollback()
                logger.info(f"URL duplicada, se omite: {url}")
            except Exception as e:  # noqa: BLE001
                await db.rollback()
                logger.error(f"Error con {url}: {e}", exc_info=True)

    logger.info(f"Radar completado: {publicadas} noticias publicadas")

    # Diagnóstico: distinguir "no hay nada bueno" de "no pudimos mirar".
    motivo = None
    if canales_ok == 0 and canales_fallidos > 0:
        razones = sorted({m for m, _ in _SC_FALLOS}) or ["desconocido"]
        motivo = f"todos los canales fallaron ({', '.join(razones)})"
    elif canales_fallidos > 0:
        motivo = f"{canales_fallidos}/{len(CANALES)} canales fallaron"

    return {
        "publicadas": publicadas,
        "candidatos": len(candidatos),
        "canales_ok": canales_ok,
        "canales_fallidos": canales_fallidos,
        "detalle_fallos": [d for _, d in _SC_FALLOS][:5],
        "motivo": motivo,
    }
