import React, { useState } from 'react';
import axios from 'axios';
import { checkAndRefreshToken } from './auth'; // Импорт функции из файла auth.js

const LocationForm = ({ setShowAddLocationForm, clickedPosition }) => {
  const [showOwnerForm, setShowOwnerForm] = useState(false);
  const [ownerData, setOwnerData] = useState({
    website: '',
    owner_info: ''
  });
  const [errors, setErrors] = useState(null); // Для хранения ошибок

  // Обработчик изменения формы владельца
  const handleOwnerChange = (e) => {
    setOwnerData({
      ...ownerData,
      [e.target.name]: e.target.value
    });
  };

  // Обработчик отправки формы локации
  const handleAddLocationSubmit = async (event) => {
    event.preventDefault();
    await checkAndRefreshToken(); // Проверка и обновление токена перед запросом

    const locationData = {
      name: event.target.name.value,
      address: event.target.address.value,
      working_hours_start: event.target.working_hours_start.value,
      working_hours_end: event.target.working_hours_end.value,
      average_check: parseInt(event.target.average_check.value, 10),
      latitude: clickedPosition.lat, // Координаты переданы через пропсы
      longitude: clickedPosition.lng, // Координаты переданы через пропсы
      owner_info: ownerData.owner_info || null,
      website: ownerData.website || null
    };

    const dataToSend = { location: locationData };

     try {
        const response = await axios.post('http://127.0.0.1:8000/locations/add-location', dataToSend, {
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${localStorage.getItem('authToken')}`,
            },
            withCredentials: true,
        });
        alert('Локация добавлена');
        setShowAddLocationForm(false);
    } catch (error) {
        console.error('Ошибка при добавлении локации:', error);
        setErrors(['Произошла ошибка при добавлении локации']);
    }
};

  return (
    <div className="modal">
      <div className="modal-content">
        <h3>Добавить новую локацию</h3>
        <form onSubmit={handleAddLocationSubmit}>
          <div className="form-group">
            <label htmlFor="name">Название локации</label>
            <input type="text" name="name" id="name" placeholder="Введите название" required />
          </div>
          <div className="form-group">
            <label htmlFor="address">Адрес</label>
            <input type="text" name="address" id="address" placeholder="Введите адрес" required />
          </div>
          <div className="form-group">
              <label htmlFor="working_hours_start">Начало работы</label>
              <input type="time" name="working_hours_start" id="working_hours_start" required />
            </div>
            <div className="form-group">
              <label htmlFor="working_hours_end">Конец работы</label>
              <input type="time" name="working_hours_end" id="working_hours_end" required />
            </div>
          <div className="form-group">
            <label htmlFor="average_check">Средний чек (2000-5000)</label>
            <input type="number" name="average_check" id="average_check" placeholder="Введите средний чек" required min="2000" max="5000" />
          </div>

          {/* Кнопка для показа формы владельца */}
          <button type="button" className="btn-secondary" onClick={() => setShowOwnerForm(!showOwnerForm)}>
            {showOwnerForm ? 'Скрыть форму владельца' : 'Я владелец'}
          </button>

          {showOwnerForm && (
            <div className="owner-form">
              <h4>Информация о владельце</h4>
              <div className="form-group">
                <label htmlFor="website">Вебсайт</label>
                <input
                  type="text"
                  name="website"
                  id="website"
                  placeholder="Введите вебсайт"
                  value={ownerData.website}
                  onChange={handleOwnerChange}
                />
              </div>
              <div className="form-group">
                <label htmlFor="owner_info">Информация о владельце</label>
                <textarea
                  name="owner_info"
                  id="owner_info"
                  placeholder="Введите информацию о себе"
                  value={ownerData.owner_info}
                  onChange={handleOwnerChange}
                />
              </div>
            </div>
          )}

          {/* Кнопки для завершения добавления */}
          <button type="submit" className="btn-primary">Добавить локацию</button>
          <button type="button" className="btn-secondary" onClick={() => setShowAddLocationForm(false)}>Отмена</button>

          {/* Вывод ошибок валидации */}
          {errors && (
            <div className="error-messages">
              {errors.map((error, index) => (
                <p key={index} style={{ color: 'red' }}>{error}</p>
              ))}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default LocationForm;