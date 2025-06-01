import React, { useEffect, useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { HotelReadClient, RoomConfigurationReadClient, TourHotelAllocationCreateClient, TourHotelAllocationClient } from '../../types';
import { getAllHotelsSimple, getRoomConfigsForHotel, addHotelAllocationToTour } from '../../services/apiService';

interface AddHotelAllocationModalProps {
  tourId: number;
  isOpen: boolean;
  onClose: () => void;
  onAllocationAdded: (newAllocation: TourHotelAllocationClient) => void;
}

const AddHotelAllocationModal: React.FC<AddHotelAllocationModalProps> = ({ tourId, isOpen, onClose, onAllocationAdded }) => {
  const { register, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<TourHotelAllocationCreateClient>();

  const [hotels, setHotels] = useState<Pick<HotelReadClient, 'id' | 'name'>[]>([]);
  const [roomConfigs, setRoomConfigs] = useState<RoomConfigurationReadClient[]>([]);
  const [isLoadingHotels, setIsLoadingHotels] = useState(false);
  const [isLoadingRoomConfigs, setIsLoadingRoomConfigs] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const selectedHotelId = watch('hotel_id');

  useEffect(() => {
    if (isOpen) {
      setIsLoadingHotels(true);
      getAllHotelsSimple()
        .then(data => setHotels(data))
        .catch(err => {
            console.error("Failed to fetch hotels", err);
            setApiError("Could not load hotels for selection.");
        })
        .finally(() => setIsLoadingHotels(false));
      reset(); // Reset form when modal opens
      setRoomConfigs([]);
      setApiError(null);
    }
  }, [isOpen, reset]);

  useEffect(() => {
    if (selectedHotelId) {
      setIsLoadingRoomConfigs(true);
      setValue('room_configuration_id', undefined as any); // Reset room config selection
      getRoomConfigsForHotel(Number(selectedHotelId))
        .then(data => setRoomConfigs(data))
        .catch(err => {
            console.error("Failed to fetch room configurations", err);
            setApiError("Could not load room configurations for the selected hotel.");
            setRoomConfigs([]);
        })
        .finally(() => setIsLoadingRoomConfigs(false));
    } else {
      setRoomConfigs([]);
    }
  }, [selectedHotelId, setValue]);

  const onSubmit: SubmitHandler<TourHotelAllocationCreateClient> = async (data) => {
    setIsSubmitting(true);
    setApiError(null);
    const submissionData = {
        ...data,
        hotel_id: Number(data.hotel_id),
        room_configuration_id: Number(data.room_configuration_id),
        allocated_rooms: Number(data.allocated_rooms)
    };
    try {
      const newAllocation = await addHotelAllocationToTour(tourId, submissionData);
      onAllocationAdded(newAllocation);
      onClose();
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Failed to add hotel allocation.');
      console.error('Add Allocation Error:', err);
    }
    setIsSubmitting(false);
  };

  if (!isOpen) return null;

  return (
    <div style={modalOverlayStyle}>
      <div style={modalContentStyle}>
        <h2>Add Hotel Allocation to Tour</h2>
        <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label htmlFor="hotel_id">Hotel:</label>
            {isLoadingHotels ? <p>Loading hotels...</p> : (
              <select id="hotel_id" {...register('hotel_id', { required: 'Hotel is required' })} style={inputStyle}>
                <option value="">Select a Hotel</option>
                {hotels.map(hotel => <option key={hotel.id} value={hotel.id}>{hotel.name}</option>)}
              </select>
            )}
            {errors.hotel_id && <p style={errorStyle}>{errors.hotel_id.message}</p>}
          </div>

          <div>
            <label htmlFor="room_configuration_id">Room Configuration:</label>
            {isLoadingRoomConfigs ? <p>Loading rooms...</p> : (
              <select
                id="room_configuration_id"
                {...register('room_configuration_id', { required: 'Room configuration is required' })}
                style={inputStyle}
                disabled={!selectedHotelId || roomConfigs.length === 0}
              >
                <option value="">Select a Room Type</option>
                {roomConfigs.map(rc => <option key={rc.id} value={rc.id}>{rc.room_type} (Max: {rc.max_occupancy}, Price: ${rc.price_per_night})</option>)}
              </select>
            )}
            {errors.room_configuration_id && <p style={errorStyle}>{errors.room_configuration_id.message}</p>}
          </div>

          <div>
            <label htmlFor="allocated_rooms">Allocated Rooms:</label>
            <input id="allocated_rooms" type="number" {...register('allocated_rooms', { required: 'Number of rooms is required', min: 1 })} style={inputStyle} />
            {errors.allocated_rooms && <p style={errorStyle}>{errors.allocated_rooms.message}</p>}
          </div>

          <div style={{display: 'flex', gap: '1rem'}}>
            <div style={{flex:1}}>
                <label htmlFor="check_in_date">Check-in Date:</label>
                <input id="check_in_date" type="date" {...register('check_in_date', { required: 'Check-in date is required' })} style={inputStyle} />
                {errors.check_in_date && <p style={errorStyle}>{errors.check_in_date.message}</p>}
            </div>
            <div style={{flex:1}}>
                <label htmlFor="check_out_date">Check-out Date:</label>
                <input id="check_out_date" type="date" {...register('check_out_date', { required: 'Check-out date is required' })} style={inputStyle} />
                {errors.check_out_date && <p style={errorStyle}>{errors.check_out_date.message}</p>}
            </div>
          </div>

          {apiError && <p style={{ color: 'red', marginTop: '0.5rem' }}>Error: {apiError}</p>}

          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
            <button type="button" onClick={onClose} style={{...buttonStyle, background: '#6c757d'}}>Cancel</button>
            <button type="submit" disabled={isSubmitting || isLoadingHotels || isLoadingRoomConfigs} style={{...buttonStyle, background: '#007bff'}}>
              {isSubmitting ? 'Adding...' : 'Add Allocation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Basic Styles (can be moved to CSS files)
const modalOverlayStyle: React.CSSProperties = {
  position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
  backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex',
  justifyContent: 'center', alignItems: 'center', zIndex: 1000,
};
const modalContentStyle: React.CSSProperties = {
  background: 'white', padding: '2rem', borderRadius: '8px',
  width: '90%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto'
};
const inputStyle: React.CSSProperties = { width: '100%', padding: '0.5rem', boxSizing: 'border-box', marginTop: '0.25rem' };
const errorStyle: React.CSSProperties = { color: 'red', fontSize: '0.875em', marginTop: '0.25rem' };
const buttonStyle: React.CSSProperties = { padding: '0.6rem 1.2rem', border: 'none', borderRadius: '4px', cursor: 'pointer' };

export default AddHotelAllocationModal;
