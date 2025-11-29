import { useEffect, useRef, useState, useMemo } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useQuery } from '@tanstack/react-query';
import { fetchRegionStats } from '@/services/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

// Coordenadas aproximadas se mantienen
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

const Map = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  
  const envToken = import.meta.env.VITE_MAPBOX_TOKEN || '';
  const [mapboxToken, setMapboxToken] = useState(envToken);
  const [isInitialized, setIsInitialized] = useState(!!envToken);
  const [selectedRegion, setSelectedRegion] = useState<string>("all");

  // Fetch de datos desde la API
  const { data: apiData, isLoading, isError } = useQuery({
    queryKey: ['regionStats'],
    queryFn: fetchRegionStats,
    retry: 1
  });

  const co2Data = apiData?.stats || [];

  const filteredData = useMemo(() => {
    return co2Data.filter(item => {
      const regionName = item.REGION || item.region; // Manejar posibles diferencias en nombres de campo
      if (!regionName) return false;
      return selectedRegion === "all" || regionName.toUpperCase() === selectedRegion.toUpperCase();
    });
  }, [selectedRegion, co2Data]);

  const uniqueRegions = useMemo(() => {
    const regions = new Set(co2Data.map(d => (d.REGION || d.region || '').toUpperCase()));
    return Array.from(regions).filter(Boolean).sort();
  }, [co2Data]);

  const initializeMap = (token: string) => {
    if (!mapContainer.current || !token) return;
    try {
      mapboxgl.accessToken = token;
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-74.0721, 4.7110],
        zoom: 5,
        pitch: 0,
      });
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
      map.current.on('load', () => {
        setIsInitialized(true);
        // Llamar a updateMarkers solo si ya tenemos datos
        if (co2Data.length > 0) updateMarkers();
      });
    } catch (error) {
      toast.error('Error al inicializar el mapa.');
    }
  };

  const updateMarkers = () => {
    if (!map.current) return;
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    filteredData.forEach(stat => {
      const regionKey = (stat.REGION || stat.region || '').toUpperCase();
      const coords = REGION_COORDS[regionKey];
      
      if (coords) {
        const el = document.createElement('div');
        el.className = 'w-4 h-4 bg-primary rounded-full border-2 border-white shadow-lg cursor-pointer hover:scale-125 transition-transform';
        
        const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
          <div class="p-2 min-w-[200px]">
            <h3 class="font-bold text-base mb-2 border-b pb-1">${regionKey}</h3>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Media CO₂:</span>
                <span class="font-mono font-medium">${stat.mean?.toExponential(2)}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Total:</span>
                <span class="font-mono">${stat.count}</span>
              </div>
            </div>
          </div>
        `);

        const marker = new mapboxgl.Marker(el)
          .setLngLat(coords as [number, number])
          .setPopup(popup)
          .addTo(map.current!);

        markersRef.current.push(marker);
      }
    });
  };

  useEffect(() => {
    if (envToken && !map.current) initializeMap(envToken);
  }, []);

  // Actualizar marcadores cuando lleguen los datos de la API
  useEffect(() => {
    if (isInitialized && map.current && co2Data.length > 0) {
      updateMarkers();
    }
  }, [filteredData, isInitialized, co2Data]);

  const handleTokenSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (mapboxToken.trim()) initializeMap(mapboxToken);
    else toast.error('Token inválido');
  };

  return (
    <div className="relative w-full h-[700px] rounded-xl overflow-hidden shadow-card border border-border bg-muted/20">
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
            <CardContent className="space-y-4">
              <form onSubmit={handleTokenSubmit} className="space-y-4">
                <Input
                  type="text"
                  placeholder="Mapbox Public Token"
                  value={mapboxToken}
                  onChange={(e) => setMapboxToken(e.target.value)}
                />
                <Button type="submit" className="w-full">Cargar Mapa</Button>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      <div ref={mapContainer} className="absolute inset-0" />

      {isInitialized && !isError && (
        <div className="absolute top-4 left-4 z-10 w-72 md:w-80">
          <Card className="bg-background/95 backdrop-blur shadow-xl border-primary/10">
            <CardHeader className="pb-3 pt-4 px-4">
              <CardTitle className="text-base font-bold flex items-center justify-between">
                <span>Filtros Regionales</span>
                <Badge variant="outline" className="text-[10px] font-normal">
                  {filteredData.length} Zonas
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4 space-y-4">
              <div className="space-y-1.5">
                <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                  <SelectTrigger className="h-9">
                    <SelectValue placeholder="Seleccionar región" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las regiones</SelectItem>
                    {uniqueRegions.map((region) => (
                      <SelectItem key={region} value={region}>{region}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Map;