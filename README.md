# 🌿 EkoIA - Análisis de Balance de Carbono en Colombia

![EkoIA Logo](./src/assets/EkoIA.png) 

## Prueba aquí: [![Link](eko-hcaxhfo60-maalejandrarojasgarzon-2008s-projects.vercel.app)](eko-hcaxhfo60-maalejandrarojasgarzon-2008s-projects.vercel.app)

> **EcoBalance360**: Analítica territorial y datos abiertos para un futuro carbono neutral.

[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5-purple?logo=vite)](https://vitejs.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-cyan?logo=tailwindcss)](https://tailwindcss.com/)
[![Shadcn UI](https://img.shields.io/badge/Shadcn-UI-000000?logo=shadcnui&logoColor=white)](https://ui.shadcn.com/)

---

## 📖 Descripción

**EkoIA** es una plataforma interactiva de visualización de datos diseñada para analizar el balance de carbono en el territorio colombiano. Permite a investigadores, entidades gubernamentales y ciudadanos explorar emisiones y absorciones de CO₂ a través de mapas interactivos, gráficos estadísticos y modelos predictivos.

El objetivo es facilitar la toma de decisiones informadas para la mitigación del cambio climático mediante el uso de **datos abiertos** y tecnología geoespacial.

## ✨ Características Principales

-   🗺️ **Mapa Interactivo:** Visualización geoespacial de emisiones por regiones utilizando **Mapbox GL**.
-   📊 **Dashboard Analítico:** Estadísticas detalladas de emisiones totales, promedios y conteos de registros.
-   📉 **Análisis Temporal:** Gráficos de línea para observar la evolución histórica de las emisiones.
-   🏆 **Top Emisores:** Rankings de las regiones con mayor impacto.
-   🔍 **Filtros Dinámicos:** Segmentación de datos por **Año**, **Región** y **Categoría**.
-   🌱 **Módulos Especializados:**
    -   **Cultivos:** Análisis de uso de suelo.
    -   **Energía:** Matriz energética y consumo.
    -   **Predicción:** Proyecciones futuras basadas en IA (Mockup).

## 🛠️ Tecnologías Utilizadas

Este proyecto ha sido construido con un stack moderno para asegurar rendimiento y mantenibilidad:

-   **Core:** [React](https://react.dev/) + [Vite](https://vitejs.dev/)
-   **Lenguaje:** [TypeScript](https://www.typescriptlang.org/)
-   **Estilos:** [Tailwind CSS](https://tailwindcss.com/)
-   **Componentes UI:** [Shadcn UI](https://ui.shadcn.com/) (basado en Radix UI)
-   **Mapas:** [Mapbox GL JS](https://www.mapbox.com/)
-   **Gráficos:** [Recharts](https://recharts.org/)
-   **Gestión de Estado/Data:** [TanStack Query (React Query)](https://tanstack.com/query/latest)
-   **Iconos:** [Lucide React](https://lucide.dev/)

## 🚀 Comenzando

Sigue estos pasos para ejecutar el proyecto en tu entorno local.

### Prerrequisitos

-   Node.js (v18 o superior)
-   npm o yarn

### Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone 
    cd ekoia-front
    ```

2.  **Instalar dependencias:**
    ```bash
    npm install
    # o
    yarn install
    ```

3.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz del proyecto y añade tu token de Mapbox:
    ```env
    VITE_MAPBOX_TOKEN=tu_token_publico_de_mapbox
    ```

4.  **Ejecutar el servidor de desarrollo:**
    ```bash
    npm run dev
    ```

    Abre [http://localhost:8080](http://localhost:8080) en tu navegador.

## 📂 Estructura del Proyecto

```text
EkoIA-front/
├── src/
│   ├── assets/          # Imágenes y logos
│   ├── components/      # Componentes reutilizables (UI, Mapas, Gráficos)
│   │   ├── ui/          # Componentes base de Shadcn
│   │   └── ...          # Map.tsx, Statistics.tsx, etc.
│   ├── hooks/           # Custom hooks (use-toast, use-mobile)
│   ├── lib/             # Utilidades (cn, utils)
│   ├── pages/           # Vistas principales (Index, Dashboard, NotFound)
│   ├── services/        # Lógica de conexión con la API
│   ├── App.tsx          # Configuración de rutas
│   └── main.tsx         # Punto de entrada
├── public/              # Archivos estáticos
└── ...config files      # Tailwind, Vite, Eslint, TSConfig