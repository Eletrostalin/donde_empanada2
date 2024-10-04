import React, { useEffect, useState } from 'react';
import { GoogleMap, Marker, useLoadScript } from '@react-google-maps/api';
import axios from 'axios';

const Map = () => {
  const [locations, setLocations] = useState([]);
  const [map, setMap] = useState(null); // Добавляем состояние для карты
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY, // Используем API ключ из env
  });

  // Функция для определения местоположения
  const locateMe = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          map.panTo(pos); // Перемещаем карту на определенное местоположение
          map.setZoom(12); // Масштабируем карту
        },
        () => {
          alert('Не удалось определить местоположение.');
        }
      );
    } else {
      alert('Ваш браузер не поддерживает геолокацию.');
    }
  };

  // Функции для зума
  const zoomIn = () => {
    if (map) {
      map.setZoom(map.getZoom() + 1);
    }
  };

  const zoomOut = () => {
    if (map) {
      map.setZoom(map.getZoom() - 1);
    }
  };

  // Загружаем локации с бэкенда
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/locations');
        setLocations(response.data);
      } catch (error) {
        console.error('Ошибка при загрузке локаций:', error);
      }
    };

    fetchLocations();
  }, []);


  // Обработчик клика на карте
  const handleMapClick = (event) => {
    if (isAuthenticated) {  // Проверяем авторизацию
      setClickedPosition({
        lat: event.latLng.lat(),
        lng: event.latLng.lng()
      });
      setShowAddLocationForm(true);  // Показываем форму добавления локации
    } else {
      alert('Только авторизованные пользователи могут добавлять локации.');
    }
  };

  // Функция для отправки формы добавления локации
  const handleAddLocationSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const name = formData.get('name');

    try {
      await axios.post('http://127.0.0.1:8000/add-location', {
        name,
        latitude: clickedPosition.lat,
        longitude: clickedPosition.lng,
      });

      setShowAddLocationForm(false); // Скрываем форму после добавления
      alert('Локация успешно добавлена!');
    } catch (error) {
      console.error('Ошибка при добавлении локации:', error);
    }
  };

  if (!isLoaded) return <div>Загрузка карты...</div>;

  const mapOptions = {
    zoom: 12,
    center: { lat: 51.1657, lng: 10.4515 },
    disableDefaultUI: true,   // Отключает все стандартные элементы управления карты
    zoomControl: false,       // Отключает стандартные кнопки зума
    mapTypeControl: false,    // Отключает выбор типа карты (например, "Карта", "Спутник")
    fullscreenControl: false, // Отключает кнопку полноэкранного режима
    streetViewControl: false, // Отключает элемент управления панорамой (Street View)
  };

  return (
    <div style={{ position: 'relative' }}>
      <GoogleMap
        options={mapOptions}
        mapContainerStyle={{ width: '100%', height: '100vh' }}
        onLoad={mapInstance => setMap(mapInstance)}
      >
        {locations.map((location) => (
          <Marker
            key={location.id}
            position={{ lat: location.latitude, lng: location.longitude }}
            title={location.name}
          />
        ))}
      </GoogleMap>

      {/* Кастомные кнопки для зума */}
      <div className="custom-button-right" id="zoom-controls">
        <div onClick={zoomIn}>
          <img src="/zoom_in.png" alt="Zoom In" style={{ width: '40px', height: '40px' }} />
        </div>
        <div onClick={zoomOut}>
          <img src="/zoom_out.png" alt="Zoom Out" style={{ width: '40px', height: '40px', marginTop: '10px' }} />
        </div>
      </div>
    </div>
  );
};

export default Map;