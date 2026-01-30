# PVPC REE Data (Pro) para Home Assistant

Esta integración avanzada permite monitorizar en tiempo real el mercado eléctrico español, extrayendo datos directamente de Red Eléctrica de España (R.E.E.). A diferencia de otras versiones, "Pro" ofrece una visión integral tanto de precios como de la situación operativa del sistema eléctrico nacional.

## Características Principales
* **Información Total R.E.E.**: Acceso a los indicadores más destacados del sistema eléctrico.
* **Atributos Extendidos**: Cada sensor no solo ofrece un estado principal, sino que incluye múltiples atributos (como precios horarios para las próximas 24h, máximos, mínimos y medias) que permiten un análisis profundo sin necesidad de múltiples peticiones API.
* **Optimizado para Visualización**: Datos estructurados específicamente para ser explotados en gráficas de alto rendimiento como ApexCharts.

## Sensores Incluidos
La integración genera las siguientes entidades clave, proporcionando la información más relevante del sector:

* **Precio PVPC**: Precio Voluntario para el Pequeño Consumidor (tarifa regulada).
* **Precio OMIE**: Precio del mercado diario (pool) gestionado por el Operador del Mercado Ibérico.
* **Precio Tarifa Indexada**: Cálculo optimizado para contratos vinculados al mercado mayorista.
* **Precio Inyección**: Precio de compensación por excedentes de autoconsumo.
* **Demanda Real**: Monitorización en tiempo real de la carga eléctrica a nivel nacional.
* **Generación Renovables**: Porcentaje y potencia de energía limpia producida en el sistema.
* **Intensidad de CO2**: Impacto ambiental de la generación eléctrica actual.
* **Periodo Tarifario**: Indicador del tramo horario vigente (P1, P2, P3).
---

**Para acceder a todos los sensores es necesario el uso de TOKEN. Si no dispone de token puede solicitarlo en consultasios@ree.es indicando su nombre y apellidos**
## Instalación
---

### Opción 1: Repositorio Personalizado en HACS (Recomendado)
1. En Home Assistant, dirígete a **HACS** > **Integraciones**.
2. Haz clic en los tres puntos de la esquina superior derecha y selecciona **Repositorios personalizados**.
3. Pega la URL de este repositorio y selecciona la categoría **Integración**.
4. Busca "PVPC REE Data (Pro)" e instala.

### Opción 2: Instalación Manual
1. Copia la carpeta `pvpc_pro` dentro del directorio `custom_components` de tu instancia.
2. Reinicia Home Assistant.
3. Ve a **Ajustes** > **Dispositivos y Servicios** > **Añadir integración** y busca "PVPC REE Data (Pro)".
---
### Agradecimientos
 * **A @azogue, creador de la integración oficial de PVPC para Home Assistant.**
 * **A @oscarrgarciia por diseñar la estructura inicial de directorios en custom_components que ha servido de base para este proyecto.**
 * **A Red Eléctrica de España por facilitar el acceso a los datos abiertos del sistema.**
---
### 🔄 Nota sobre el Historial de Datos
La integracion tiene una funcion para recuperar el id usado anteriormente si ya se tenia otra integración de ESIOS. Si cambia la id siga esta instrucciones.

Para no perder las estadísticas de largo plazo:
1. Instala la nueva integración.
2. Ve a **Ajustes** > **Entidades** y busca el nuevo sensor (ej: `sensor.pvpc_pro_precio_pvpc`).
3. Cambia su **ID de entidad** para que coincida exactamente con el antiguo (ej: `sensor.esios_pvpc`).
4. HA vinculará los nuevos datos con tu historial previo.
---
## Dashboard Recomendado
Para sacar el máximo partido a los atributos de 24h, se recomienda usar `apexcharts-card`. Aquí tienes un ejemplo de configuración para comparar el PVPC y el OMIE:

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "Análisis Energético Pro"
  show_states: true
  colorize_states: true
graph_span: 24h
span:
  start: day
now:
  show: true
  label: Ahora
yaxis:
  - id: precio
    decimals: 5
    apex_config:
      forceNiceScale: true
series:
  - entity: sensor.pvpc_pro_precio_pvpc
    name: PVPC
    yaxis_id: precio
    type: area
    color: "#03A9F4"
    stroke_width: 3
    opacity: 0.1
    curve: smooth
    float_precision: 5
    data_generator: |
      const prices = [];
      for (const [key, value] of Object.entries(entity.attributes)) {
        if (key.match(/^price_\d{2}h$/)) {
          const hour = parseInt(key.split('_')[1]);
          const d = new Date();
          d.setHours(hour, 0, 0, 0);
          prices.push([d.getTime(), value]);
        }
      }
      return prices.sort((a, b) => a[0] - b[0]);
  - entity: sensor.pvpc_pro_precio_omie
    name: OMIE
    yaxis_id: precio
    type: area
    color: "#FF4500"
    stroke_width: 3
    opacity: 0.05
    curve: smooth
    float_precision: 5
    data_generator: |
      const prices = [];
      for (const [key, value] of Object.entries(entity.attributes)) {
        if (key.match(/^price_\d{2}h$/)) {
          const hour = parseInt(key.split('_')[1]);
          const d = new Date();
          d.setHours(hour, 0, 0, 0);
          prices.push([d.getTime(), value]);
        }
      }
      return prices.sort((a, b) => a[0] - b[0]);
apex_config:
  chart:
    height: 300px
  fill:
    type: solid
  legend:
    show: true
  tooltip:
    shared: true
    intersect: false

```
