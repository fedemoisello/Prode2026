# Prode Mundial 2026 — Estado del proyecto

**Última actualización:** 18 de abril de 2026  
**Autor:** Fede Moisello  
**Deadline del producto:** 11 de junio de 2026, 13:00 hs ARG (16:00 UTC)

---

## Infraestructura ✅

| Componente | Estado | Detalle |
|-----------|--------|---------|
| GitHub repo | ✅ Live | github.com/fedemoisello/Prode2026 (público) |
| Supabase DB | ✅ Live | htbouphuhouiivuwhocq.supabase.co |
| Streamlit Cloud | ✅ Live | Conectado a GitHub, redeploy automático |
| Tablas DB | ✅ Creadas | users, teams, fixture, picks_grupos, picks_eliminatorias, results, config |
| RLS Supabase | ✅ Activo | Bloquea escritura post-deadline en picks |
| Seed DB | ✅ Ejecutado | 48 equipos + 104 partidos cargados |

---

## Datos cargados ✅

- **48 equipos** — todos los grupos A-L con flag emoji, seed y nombres en español
- **72 partidos de grupos** — fechas/horas UTC reales, sedes y ciudades verificadas (fuente: Infobae/FIFA)
- **32 partidos de eliminatorias** — bracket FIFA oficial con placeholders (1A, 2B, 3ABCDF, W73, L101, etc.)
- **Config deadline** — 2026-06-11T16:00:00Z en tabla config

---

## Código implementado ✅

### Lógica (`lib/`)
- `db.py` — cliente Supabase, helpers query/upsert/update
- `auth.py` — login con bcrypt, session 24hs en session_state
- `deadline.py` — chequeo server-side, tiempo restante formateado
- `grupos.py` — tabla de posiciones con desempates FIFA (pts → DG → GF)
- `terceros.py` — backtracking para asignar 8 mejores terceros a sus slots según restricciones FIFA
- `bracket.py` — build_16vos() propaga clasificados al bracket; resolver en eliminatorias via placeholders
- `scoring.py` — sistema completo: tendencia(2pts) + gol local(1pt) + gol visitante(1pt) + bonus exacto(2pts) en grupos y eliminatorias
- `constants.py` — grupos, equipos, bracket structure, puntos por fase

### UI (`pages/`)
- `1_Inicio.py` — login dropdown+PIN, estado del prode, countdown
- `2_Fase_Grupos.py` — 72 partidos organizados por grupo con tabla en vivo
- `3_Eliminatorias.py` — bracket completo con propagación recursiva de equipos (incl. tercer puesto via perdedores)
- `4_Mi_Prode.py` — vista read-only del prode completo con tabla de posiciones derivada
- `5_Ranking.py` — ranking en vivo con desglose por categoría
- `6_Admin.py` — carga de resultados reales, auditoría de usuarios

### Scripts
- `scripts/seed_db.py` — carga teams + fixture desde JSONs
- `scripts/create_users.py` — genera PINs aleatorios, hashea con bcrypt, guarda en users_pines.txt

### Tests
- `tests/test_grupos.py` — tabla de posiciones y desempates
- `tests/test_scoring.py` — puntaje grupos y eliminatorias
- `tests/test_terceros.py` — asignación de terceros con restricciones

---

## Sistema de puntaje

| Evento | Puntos |
|--------|--------|
| Tendencia correcta (W/D/L) en grupos | 2 |
| Goles de un equipo exactos | 1 |
| Resultado exacto bonus (tendencia + ambos goles) | +2 |
| Acertar 1ro de grupo | 3 |
| Acertar 2do de grupo | 3 |
| Ganador cruce 16vos | 5 |
| Ganador cruce 8vos | 10 |
| Ganador cuartos | 20 |
| Ganador semis | 40 |
| Campeón | 80 |
| Subcampeón (tercer puesto correcto vía picks) | 20 |
| Bonus goles eliminatorias: mismo sistema que grupos | 1+1+2 |

---

## Pendiente antes del 11 de junio

### Crítico
- [ ] **Crear usuarios reales** — editar `scripts/create_users.py` con los 20 nombres y correr `py -3 scripts/create_users.py`
- [ ] **Verificar key de Supabase** — la key actual es `sb_publishable_...` (nuevo formato). Confirmar en Project Settings → API que sea la anon/public key con el JWT `eyJ...` si hay problemas de conexión
- [ ] **Correr tests** — `py -3 -m pytest tests/ -v` con las dependencias instaladas
- [ ] **Test end-to-end** — hacer que Gasti, Bidi y Sebi carguen un prode de prueba completo

### Importante
- [ ] Probar desde mobile (el bracket en pantalla chica puede ser el talón de Aquiles)
- [ ] Verificar que el bloqueo de deadline funciona (mock de timestamp)
- [ ] Preparar mensaje de WhatsApp con link + PIN para cada usuario
- [ ] Backup plan: tener Railway + Docker listo si Streamlit Cloud falla el 11/6

### Menor
- [ ] CSS para que se vea mejor (opcional, funciona sin esto)
- [ ] Agregar página "Ver prode de otros" post-deadline

---

## Cómo correr localmente

```bash
cd prode-2026
py -3 -m pip install -r requirements.txt
# Crear .streamlit/secrets.toml con SUPABASE_URL, SUPABASE_KEY, DEADLINE_UTC
py -3 -m streamlit run app.py
```

## Archivos sensibles (NO en GitHub)

- `.streamlit/secrets.toml` — credenciales Supabase
- `.env` — credenciales para scripts locales
- `users_pines.txt` — PINs en claro (se genera al correr create_users.py, borrarlo después)

---

## Estructura de carpetas

```
prode-2026/
├── app.py                    # entry point Streamlit
├── pages/                    # 6 páginas
├── lib/                      # lógica de negocio
├── data/                     # teams.json + fixture.json
├── scripts/                  # seed_db.py + create_users.py
├── tests/                    # pytest
├── .streamlit/               # config.toml + secrets (gitignored)
├── schema.sql                # SQL para ejecutar en Supabase
├── requirements.txt
└── STATUS.md                 # este archivo
```
