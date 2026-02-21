import type { Winegrower } from '@/lib/types';

interface WinegrowerMapProps {
  winegrower: Winegrower;
}

export default function WinegrowerMap({ winegrower }: WinegrowerMapProps) {
  const fallbackMapUrl = () => {
    const query = `${winegrower.business_name} ${winegrower.city} ${winegrower.state_province}`;
    return `https://www.google.com/maps?q=${encodeURIComponent(query)}&output=embed&z=11`;
  };

  return (
    <div className="winegrower-map-container">
      <iframe
        src={fallbackMapUrl()}
        className="winegrower-map-iframe"
        allowFullScreen
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        title={`Location of ${winegrower.business_name}`}
      />
    </div>
  );
}
