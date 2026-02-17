const WinegrowerMap = ({ producer }) => {
  const buildGoogleMapsUrl = (producer) => {
    if (!producer) return ''
    
    const query = `${producer.name} ${producer.city} ${producer.state_province}`
    return `https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q=${encodeURIComponent(query)}`
  }

  const fallbackMapUrl = (producer) => {
    if (!producer) return ''

    const query = `${producer.name} ${producer.city} ${producer.state_province}`
    return `https://www.google.com/maps?q=${encodeURIComponent(query)}&output=embed&z=11`
  }

  return (
    <div className="winegrower-map-container">
      <iframe
        src={fallbackMapUrl(producer)}
        className="winegrower-map-iframe"
        allowFullScreen=""
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        title={`Location of ${producer.name}`}
      ></iframe>
    </div>
  )
}

export default WinegrowerMap