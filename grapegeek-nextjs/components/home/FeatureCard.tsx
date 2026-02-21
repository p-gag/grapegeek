import Link from 'next/link';

interface FeatureCardProps {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  exploreLabel?: string;
}

export default function FeatureCard({ title, description, href, icon, exploreLabel = 'Explore →' }: FeatureCardProps) {
  return (
    <Link href={href} className="block group">
      <div className="bg-white p-8 rounded-xl shadow-brand hover:shadow-brand-hover transition-all duration-300 h-full">
        <div className="text-brand mb-4 group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-brand transition-colors">
          {title}
        </h3>
        <p className="text-gray-600 leading-relaxed">
          {description}
        </p>
        <div className="mt-4 text-brand font-semibold group-hover:translate-x-2 transition-transform inline-block">
          {exploreLabel}
        </div>
      </div>
    </Link>
  );
}
