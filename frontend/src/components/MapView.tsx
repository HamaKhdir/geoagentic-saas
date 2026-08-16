import React, { useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default Leaflet marker icon issue in React
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

interface MapProps {
  geoJsonData: any;
}

// Controller to zoom to bounds when GeoJSON updates
const MapBoundsSetter: React.FC<{ geoJsonData: any }> = ({ geoJsonData }) => {
  const map = useMap();
  
  useEffect(() => {
    if (geoJsonData && geoJsonData.features && geoJsonData.features.length > 0) {
      const geoJsonLayer = L.geoJSON(geoJsonData);
      map.fitBounds(geoJsonLayer.getBounds(), { padding: [50, 50] });
    }
  }, [geoJsonData, map]);

  return null;
};
export const MapView: React.FC<MapProps> = ({ geoJsonData }) => {
  const defaultCenter: [number, number] = [51.62, 0.30]; // Center around Brentwood / London area

  return (
    <div className="h-full w-full rounded-2xl overflow-hidden shadow-xl border border-slate-700 relative min-h-[500px]">
      <MapContainer 
        center={defaultCenter} 
        zoom={12} 
        style={{ height: '100%', width: '100%', minHeight: '500px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {geoJsonData && (
          <>
            <GeoJSON 
              key={JSON.stringify(geoJsonData)} 
              data={geoJsonData}
              style={() => ({
                color: '#2563eb',
                weight: 3,
                opacity: 0.8,
                fillColor: '#3b82f6',
                fillOpacity: 0.35
              })}
            />
            <MapBoundsSetter geoJsonData={geoJsonData} />
          </>
        )}
      </MapContainer>
    </div>
  );
};