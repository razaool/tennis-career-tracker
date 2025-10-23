import React from 'react';

export default function HomePage() {
  return (
    <div className="fixed inset-0 bg-black text-white w-full h-full">
      {/* Main Dashboard Grid */}
      <div className="h-full p-4 grid grid-cols-1 lg:grid-cols-12 auto-rows-fr lg:grid-rows-12 gap-4 overflow-y-auto">
        
        {/* Panel 1: Stat of the Day (Top Left) */}
        <div className="col-span-1 lg:col-span-4 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">1</h3>
        </div>

        {/* Panel 2: System Status (Top Center Left) */}
        <div className="col-span-1 lg:col-span-3 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">2</h3>
        </div>

        {/* Panel 3: Live Tournaments (Top Center Right) */}
        <div className="col-span-1 lg:col-span-3 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">3</h3>
        </div>

        {/* Panel 4: Recent Match Results (Top Right) */}
        <div className="col-span-1 lg:col-span-2 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">4</h3>
        </div>

        {/* Panel 5: Player Rankings (Left Column - Tall) */}
        <div className="col-span-1 lg:col-span-4 row-span-1 lg:row-span-11 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">5</h3>
        </div>

        {/* Panel 6: Season Completion Graph (Right Column - Tall) */}
        <div className="col-span-1 lg:col-span-8 row-span-1 lg:row-span-8 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">6</h3>
        </div>


        {/* Panel 7: Main Trajectory Chart (Bottom - Full Width) */}
        <div className="col-span-1 lg:col-span-8 lg:col-start-5 lg:row-start-10 row-span-1 lg:row-span-3 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">7</h3>
        </div>
      </div>
    </div>
  );
}