import { Winegrower } from '@/lib/types';
import { Building2, User, MapPin, Mail, Phone, Facebook, Instagram, Twitter, Youtube, Linkedin } from 'lucide-react';

interface WinegrowerInfoProps {
  winegrower: Winegrower;
}

function getSocialIcon(url: string) {
  const urlLower = url.toLowerCase();

  if (urlLower.includes('facebook.com')) {
    return { Icon: Facebook, color: '#1877F2', platform: 'Facebook' };
  }
  if (urlLower.includes('instagram.com')) {
    return { Icon: Instagram, color: '#E4405F', platform: 'Instagram' };
  }
  if (urlLower.includes('twitter.com') || urlLower.includes('x.com')) {
    return { Icon: Twitter, color: '#000000', platform: 'Twitter/X' };
  }
  if (urlLower.includes('youtube.com')) {
    return { Icon: Youtube, color: '#FF0000', platform: 'YouTube' };
  }
  if (urlLower.includes('linkedin.com')) {
    return { Icon: Linkedin, color: '#0A66C2', platform: 'LinkedIn' };
  }
  return { Icon: Building2, color: '#666', platform: 'Social Media' };
}

export default function WinegrowerInfo({ winegrower }: WinegrowerInfoProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Contact Information</h2>

      <div className="space-y-4">
        {/* Business Name */}
        <div className="flex items-start gap-3">
          <Building2 className="w-5 h-5 text-gray-500 mt-0.5" />
          <div>
            <p className="text-sm text-gray-500">Business</p>
            <p className="font-medium">{winegrower.business_name}</p>
          </div>
        </div>

        {/* Permit Holder */}
        {winegrower.permit_holder && winegrower.permit_holder !== winegrower.business_name && (
          <div className="flex items-start gap-3">
            <User className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-sm text-gray-500">Permit Holder</p>
              <p className="font-medium">{winegrower.permit_holder}</p>
            </div>
          </div>
        )}

        {/* Address */}
        <div className="flex items-start gap-3">
          <MapPin className="w-5 h-5 text-gray-500 mt-0.5" />
          <div>
            <p className="text-sm text-gray-500">Address</p>
            <p className="font-medium">
              {winegrower.address && <>{winegrower.address}<br /></>}
              {winegrower.city}, {winegrower.state_province}
              {winegrower.postal_code && <> {winegrower.postal_code}</>}
              <br />
              {winegrower.country}
            </p>
          </div>
        </div>

        {/* Permit ID */}
        <div className="flex items-start gap-3">
          <Building2 className="w-5 h-5 text-gray-500 mt-0.5" />
          <div>
            <p className="text-sm text-gray-500">Permit ID</p>
            <p className="font-mono text-sm">{winegrower.permit_id}</p>
          </div>
        </div>

        {/* Classification */}
        {winegrower.classification && (
          <div className="flex items-start gap-3">
            <Building2 className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-sm text-gray-500">Classification</p>
              <p className="font-medium">{winegrower.classification}</p>
            </div>
          </div>
        )}

        {/* Activities */}
        {winegrower.activities && winegrower.activities.length > 0 && (
          <div className="flex items-start gap-3">
            <Building2 className="w-5 h-5 text-gray-500 mt-0.5" />
            <div>
              <p className="text-sm text-gray-500">Activities</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {winegrower.activities.map((activity, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                  >
                    {activity}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Social Media */}
        {winegrower.social_media && winegrower.social_media.length > 0 && (
          <div className="pt-4 border-t">
            <p className="text-sm text-gray-500 mb-3">Social Media</p>
            <div className="flex flex-wrap gap-3">
              {winegrower.social_media.map((url, index) => {
                const { Icon, color, platform } = getSocialIcon(url);
                return (
                  <a
                    key={index}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-3 py-2 rounded-lg border hover:bg-gray-50 transition"
                    title={`Visit ${platform}`}
                  >
                    <Icon className="w-5 h-5" style={{ color }} />
                    <span className="text-sm">{platform}</span>
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {/* Data Source */}
        {winegrower.source && (
          <div className="pt-4 border-t">
            <p className="text-xs text-gray-400">
              Data source: {winegrower.source}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
