# Scrapling de precios

Este flujo consulta páginas públicas de Cardmarket y ventas completadas de eBay ES cada 8 horas (00:17, 08:17 y 16:17 UTC). No usa navegador furtivo, proxies ni resolución de desafíos; si la web rechaza la petición, registra la fuente como no disponible.

## Configuración

En GitHub, añade el secreto de Actions `PRICE_TARGETS` con una lista JSON de productos. Guarda ahí solo los objetivos que quieras consultar; el secreto no se incluye en el repositorio.

```json
[
  {
    "id": "charizard-base-set",
    "name": "Charizard Base Set",
    "cardmarket_url": "https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Charizard",
    "ebay_query": "Pokemon Charizard Base Set 4/102"
  }
]
```

Las dos fuentes son opcionales por producto. Limita la lista a 30 objetivos; el proceso espera entre objetivos para reducir solicitudes. Lanza la primera ejecución desde Actions → “Actualizar precios públicos” → “Run workflow”.

## Resultado

Cada ejecución publica `price-results.json` como artefacto privado de Actions durante 7 días. Incluye hora UTC, fuentes, importes visibles y cantidad de ofertas/ventas. eBay puede ocultar el importe final de ofertas aceptadas. Este artefacto no es una API ni lo descarga Android automáticamente; publicar precios para consumo desde la app requiere un destino accesible adicional.

El scraping debe respetar las condiciones y límites de cada sitio. No se intenta sortear bloqueos o controles de acceso.
