# Scrapling de precios

Este flujo consulta páginas públicas de Cardmarket y ventas completadas de eBay ES cada 8 horas (00:17, 08:17 y 16:17 UTC). Cuando Cardmarket bloquea o no muestra ofertas, consulta el precio guía Cardmarket de TCGdex para añadir tendencias, mínimos y medias recientes por impresión (por ejemplo, ilimitada y Shadowless); esos datos son referencias agregadas, no ofertas actuales. No usa navegador furtivo, proxies ni resolución de desafíos.

## Configuración

En GitHub, añade el secreto de Actions `PRICE_TARGETS` con una lista JSON de productos. Guarda ahí solo los objetivos que quieras consultar; el secreto no se incluye en el repositorio.

```json
[
  {
    "id": "charizard-base-set",
    "name": "Charizard",
    "cardmarket_url": "https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Charizard",
    "ebay_query": "Pokemon Charizard Base Set 4/102",
    "app_match": {"name": "Charizard", "set": "Base Set", "language": "en", "finish": "Normal"}
  }
]
```

Las dos fuentes son opcionales por producto. Puedes añadir `tcgdex_id` para fijar la carta exacta; si falta, el scraper intenta resolver nombre y colección desde `app_match` o la URL de Cardmarket. Limita la lista a 30 objetivos; el proceso espera entre objetivos para reducir solicitudes. Lanza la primera ejecución desde Actions → “Actualizar precios públicos” → “Run workflow”.

## Resultado

Cada ejecución conserva `price-results.json` como artefacto privado de Actions durante 7 días y lo despliega también en GitHub Pages para que Android pueda leerlo. El JSON incluye hora UTC, fuentes, importes visibles y cantidad de ofertas/ventas. eBay puede ocultar el importe final de ofertas aceptadas. El campo `app_match` enlaza un objetivo con nombre, colección, idioma y acabado de una ficha Android. La publicación hace públicos esos datos de precios y objetivos.

El scraping debe respetar las condiciones y límites de cada sitio. No se intenta sortear bloqueos o controles de acceso.
