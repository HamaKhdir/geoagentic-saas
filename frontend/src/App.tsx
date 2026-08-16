import { useState } from 'react';
import { MapView } from './components/MapView';
import { ChatPanel } from './components/ChatPanel';

export default function App() {
  const [geoJsonData, setGeoJsonData] = useState<any>(null);

  return (
    <div className="flex h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Lighter Side Panel for Chat Engine */}
      <div className="w-full md:w-[420px] h-full p-4 flex flex-col z-10">
        <ChatPanel onGeoDataReceived={(data) => setGeoJsonData(data)} />
      </div>

      {/* Main Spatial Map Area */}
      <div className="flex-1 h-full p-4 pl-0">
        <MapView geoJsonData={geoJsonData} />
      </div>
    </div>
  );
}