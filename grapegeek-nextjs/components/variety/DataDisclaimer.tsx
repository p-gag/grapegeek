interface DataDisclaimerProps {
  type?: 'variety' | 'producer';
}

export default function DataDisclaimer({ type = 'variety' }: DataDisclaimerProps) {
  const text =
    type === 'variety'
      ? 'Grape variety data compiled from VIVC database, academic sources, and industry publications. Producer information automatically extracted from public sources.'
      : 'Information automatically extracted from public sources. May contain errors.';

  return (
    <div className="data-disclaimer-footer">
      <div className="disclaimer-content">
        <div className="disclaimer-text">
          <span>ℹ️</span>
          <span>{text}</span>
        </div>
      </div>
    </div>
  );
}
