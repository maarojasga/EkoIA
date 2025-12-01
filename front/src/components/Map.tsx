import { useEffect, useRef, useState, useMemo } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useQuery } from '@tanstack/react-query';
import { fetchRegionStats, DashboardFilters } from '@/services/api';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

// Coordenadas fijas para centrar los marcadores
const REGION_COORDS: Record<string, [number, number]> = {
  "AMAZONIA": [-72.0, 1.0],
  "ANDES": [-75.5, 5.5],
  "ANDINA": [-75.0, 5.0],
  "ANTIOQUIA": [-75.5, 7.0],
  "BOGOTA": [-74.0721, 4.7110],
  "CARIBE": [-74.5, 10.0],
  "COLOMBIA": [-73.0, 4.0],
  "MAGDALENA": [-74.2, 10.5],
  "ORINOQUIA": [-70.0, 5.0],
  "PACIFICA": [-77.0, 5.0],
  "SANTANDER": [-73.3, 6.7],
  "VALLE DEL CAUCA": [-76.5, 3.5]
};

interface MapProps {
  filters: DashboardFilters;
}

const Map = ({ filters }: MapProps) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  
  // Token desde .env
  const envToken = import.meta.env.VITE_MAPBOX_TOKEN || '';
  const [mapboxToken, setMapboxToken] = useState(envToken);
  const [isInitialized, setIsInitialized] = useState(!!envToken);

  // Fetch de datos
  const { data: apiData, isLoading } = useQuery({
    queryKey: ['regionStats', filters],
    queryFn: () => fetchRegionStats(filters),
    retry: 1
  });

  // Aseguramos que sea un array
  const co2Data = apiData?.stats || [];

  const initializeMap = (token: string) => {
    if (!mapContainer.current || !token) return;
    try {
      mapboxgl.accessToken = token;
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-74.0721, 4.7110], // Centro en Colombia
        zoom: 5,
        pitch: 0,
      });
      
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
      
      map.current.on('load', () => {
        setIsInitialized(true);
      });

    } catch (error) {
      console.error("Error mapa:", error);
      toast.error('Error al inicializar el mapa.');
    }
  };

  const updateMarkers = () => {
    if (!map.current) return;

    // 1. Limpiar marcadores existentes
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    console.log("Datos para el mapa:", co2Data); // DEBUG: Ver qué llega

    if (co2Data.length === 0) return;

    // 2. Crear nuevos marcadores
    co2Data.forEach((stat: any) => {
      // Normalizar nombre: Mayúsculas y sin espacios extra
      const regionNameRaw = stat.REGION || stat.region || '';
      const regionKey = regionNameRaw.toString().toUpperCase().trim();
      
      const coords = REGION_COORDS[regionKey];
      
      if (coords) {
        // Cálculo de tamaño (mínimo 20px, máximo 60px)
        const size = Math.min(Math.max(stat.count / 50, 20), 60); 
        
        // Crear elemento DOM para el marcador
        const el = document.createElement('div');
        // Estilos base Tailwind + Estilo en línea para asegurar visibilidad
        el.className = 'rounded-full border-2 border-white shadow-lg cursor-pointer hover:scale-110 transition-transform flex items-center justify-center';
        el.style.backgroundColor = 'hsl(34, 100%, 48%)'; // Color primario (Naranja) directo
        el.style.width = `${size}px`;
        el.style.height = `${size}px`;
        el.style.opacity = '0.8';

        // Texto o icono dentro del marcador (opcional, ayuda a verlo)
        el.innerHTML = `<span style="color:white; font-size:10px; font-weight:bold">${stat.count}</span>`;
        
        // Popup con información
        const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
          <div class="p-2 min-w-[150px]">
            <h3 class="font-bold text-sm mb-2 border-b pb-1 text-slate-800">${regionKey}</h3>
            <div class="space-y-1 text-xs text-slate-600">
              <div class="flex justify-between">
                <span>Total:</span>
                <span class="font-mono font-bold">${stat.mean?.toExponential(2)}</span>
              </div>
              <div class="flex justify-between">
                <span>Registros:</span>
                <span class="font-mono">${stat.count}</span>
              </div>
            </div>
          </div>
        `);

        // Añadir al mapa
        const marker = new mapboxgl.Marker(el)
          .setLngLat(coords as [number, number])
          .setPopup(popup)
          .addTo(map.current!);

        markersRef.current.push(marker);
      } else {
        console.warn(`Coordenadas no encontradas para la región: "${regionKey}"`);
      }
    });
  };

  useEffect(() => {
    if (envToken && !map.current) initializeMap(envToken);
  }, []);

  // Re-dibujar marcadores cuando cambien los datos o el mapa esté listo
  useEffect(() => {
    if (isInitialized && map.current && co2Data.length > 0) {
      updateMarkers();
    }
  }, [co2Data, isInitialized]);

  const handleTokenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (mapboxToken.trim()) initializeMap(mapboxToken);
  };

  return (
    <div className="relative w-full h-[600px] rounded-xl overflow-hidden shadow-card border border-border bg-muted/20">
      {isLoading && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-background/50 backdrop-blur-sm">
          <Loader2 className="w-10 h-10 animate-spin text-primary" />
        </div>
      )}
      
      {!isInitialized && !isLoading && (
        <div className="absolute inset-0 z-20 bg-background/95 backdrop-blur-sm flex items-center justify-center p-4">
           <Card className="w-full max-w-md shadow-xl border-primary/20">
              <CardHeader className="text-center pb-2">
                <CardTitle>Configurar Mapa</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleTokenSubmit} className="space-y-4">
                  <Input 
                    type="text"
                    placeholder="Mapbox Public Token" 
                    value={mapboxToken} 
                    onChange={e => setMapboxToken(e.target.value)} 
                  />
                  <Button type="submit" className="w-full">Cargar Mapa</Button>
                </form>
              </CardContent>
           </Card>
        </div>
      )}

      <div ref={mapContainer} className="absolute inset-0" />
    </div>
  );
};

export default Map;