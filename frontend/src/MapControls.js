import React from 'react';

const MapControls = ({ locateMe, zoomIn, zoomOut }) => {
  return (
    <div>
      {/* Кастомные кнопки для зума */}
      <div className="custom-button-right" id="zoom-controls">
        <div onClick={zoomIn}>
          <img src="/zoom_in.png" alt="Zoom In" style={{ width: '40px', height: '40px' }} />
        </div>
        <div onClick={zoomOut}>
          <img src="/zoom_out.png" alt="Zoom Out" style={{ width: '40px', height: '40px', marginTop: '10px' }} />
        </div>
      </div>
      {/* Кнопка для определения местоположения */}
      <div className="custom-button-right" id="my-location" onClick={locateMe}>
        <img src="/my_location.png" alt="Locate Me" style={{ width: '40px', height: '40px' }} />
      </div>
    </div>
  );
};

export default MapControls;