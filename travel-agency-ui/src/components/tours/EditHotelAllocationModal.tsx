import React, { useEffect, useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { HotelReadClient, RoomConfigurationReadClient, TourHotelAllocationClient, TourHotelAllocationUpdateClient } from '../../types';
import { getAllHotelsSimple, getRoomConfigsForHotel, updateHotelAllocation } from '../../services/apiService';

interface EditHotelAllocationModalProps {
  allocation: TourHotelAllocationClient | null; // Pass the existing allocation to edit
  tourId: number; // Needed if you re-use parts that depend on it, though not strictly for update by alloc ID
  isOpen: boolean;
  onClose: () => void;
  onAllocationUpdated: (updatedAllocation: TourHotelAllocationClient) => void;
}

// Use the create type for form, then map to update type
interface EditAllocationFormInput extends Omit<TourHotelAllocationCreateClient, 'hotel_id' | 'room_configuration_id' | 'allocated_rooms'> {
    hotel_id_str: string;
    room_configuration_id_str: string;
    allocated_rooms_str: string;
}

const EditHotelAllocationModal: React.FC<EditHotelAllocationModalProps> = ({ allocation, isOpen, onClose, onAllocationUpdated }) => {
  const { register, handleSubmit, watch, setValue, reset, formState: { errors, isDirty } } = useForm<EditAllocationFormInput>();

  const [hotels, setHotels] = useState<Pick<HotelReadClient, 'id' | 'name'>[]>([]);
  const [roomConfigs, setRoomConfigs] = useState<RoomConfigurationReadClient[]>([]);
  const [isLoadingHotels, setIsLoadingHotels] = useState(false);
  const [isLoadingRoomConfigs, setIsLoadingRoomConfigs] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const selectedHotelIdStr = watch('hotel_id_str');

  // Populate form with existing allocation data when modal opens or allocation changes
  useEffect(() => {
    if (isOpen && allocation) {
      reset(); // Clear previous form state
      setApiError(null);
      setValue('hotel_id_str', String(allocation.hotel_id));
      // Fetch hotels first, then set room_configuration_id once roomConfigs are loaded for that hotel
      setValue('allocated_rooms_str', String(allocation.allocated_rooms));
      setValue('check_in_date', allocation.check_in_date.split('T')[0]);
      setValue('check_out_date', allocation.check_out_date.split('T')[0]);

      setIsLoadingHotels(true);
      getAllHotelsSimple()
        .then(data => {
            setHotels(data);
            // If current hotel_id is valid, trigger room config load
            if (allocation.hotel_id && data.some(h => h.id === allocation.hotel_id)) {
                // Defer setting room_configuration_id until roomConfigs for this hotel are loaded
            }
        })
        .catch(err => {
            console.error("Failed to fetch hotels", err);
            setApiError("Could not load hotels for selection.");
        })
        .finally(() => setIsLoadingHotels(false));
    } else if (!isOpen) {
      setRoomConfigs([]); // Clear room configs when modal closes
    }
  }, [isOpen, allocation, reset, setValue]);

  // Load room configurations when selected hotel changes or when allocation data is first set
  useEffect(() => {
    const currentHotelId = selectedHotelIdStr ? Number(selectedHotelIdStr) : null;
    if (currentHotelId) {
      setIsLoadingRoomConfigs(true);
      // Don't reset room_configuration_id if it's the initial load for the current allocation's hotel
      // Only reset if the user *changes* the hotel_id_str
      // This effect might run multiple times, ensure setValue for room_config is handled carefully
      getRoomConfigsForHotel(currentHotelId)
        .then(data => {
            setRoomConfigs(data);
            // If editing, and the current hotel matches the allocation's hotel, try to set the room_config_id
            if (allocation && allocation.hotel_id === currentHotelId && data.some(rc => rc.id === allocation.room_configuration_id)) {
                setValue('room_configuration_id_str', String(allocation.room_configuration_id));
            } else if (allocation && allocation.hotel_id !== currentHotelId) {
                 setValue('room_configuration_id_str', ''); // Reset if hotel changed
            }
        })
        .catch(err => {
            console.error("Failed to fetch room configurations", err);
            setApiError("Could not load room configurations for the selected hotel.");
            setRoomConfigs([]);
        })
        .finally(() => setIsLoadingRoomConfigs(false));
    } else {
      setRoomConfigs([]);
      setValue('room_configuration_id_str', '');
    }
  // Only trigger on selectedHotelIdStr. Initial population of room_configuration_id_str is handled after roomConfigs load.
  }, [selectedHotelIdStr, allocation, setValue]);


  const onSubmit: SubmitHandler<EditAllocationFormInput> = async (data) => {
    if (!allocation) return;
    if (!isDirty) {
        onClose(); // No changes made
        return;
    }
    setIsSubmitting(true);
    setApiError(null);

    const updateData: TourHotelAllocationUpdateClient = {
        hotel_id: data.hotel_id_str ? Number(data.hotel_id_str) : undefined,
        room_configuration_id: data.room_configuration_id_str ? Number(data.room_configuration_id_str) : undefined,
        allocated_rooms: data.allocated_rooms_str ? Number(data.allocated_rooms_str) : undefined,
        check_in_date: data.check_in_date,
        check_out_date: data.check_out_date,
    };
     // Filter out undefined values to only send changed fields, assuming PATCH-like behavior for PUT
    Object.keys(updateData).forEach(key =>
        (updateData as any)[key] === undefined && delete (updateData as any)[key]
    );
    if (Object.keys(updateData).length === 0) { // Check if anything is left to update after undefined removal
        onClose();
        return;
    }

    try {
      const updated = await updateHotelAllocation(allocation.id, updateData);
      onAllocationUpdated(updated);
      onClose();
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Failed to update hotel allocation.');
      console.error('Update Allocation Error:', err);
    }
    setIsSubmitting(false);
  };

  if (!isOpen || !allocation) return null;

  return (
    <div style={modalOverlayStyle}> {/* Reuse styles from Add modal or create common ones */}
      <div style={modalContentStyle}>
        <h2>Edit Hotel Allocation</h2>
        <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Form fields are very similar to Add modal, but pre-filled */}
          <div>
            <label htmlFor="edit_hotel_id">Hotel:</label>
            {isLoadingHotels ? <p>Loading hotels...</p> : (
              <select id="edit_hotel_id" {...register('hotel_id_str', { required: 'Hotel is required' })} style={inputStyle}>
                <option value="">Select a Hotel</option>
                {hotels.map(hotel => <option key={hotel.id} value={String(hotel.id)}>{hotel.name}</option>)}
              </select>
            )}
            {errors.hotel_id_str && <p style={errorStyle}>{errors.hotel_id_str.message}</p>}
          </div>

          <div>
            <label htmlFor="edit_room_configuration_id">Room Configuration:</label>
            {isLoadingRoomConfigs ? <p>Loading rooms...</p> : (
              <select
                id="edit_room_configuration_id"
                {...register('room_configuration_id_str', { required: 'Room configuration is required' })}
                style={inputStyle}
                disabled={!selectedHotelIdStr || roomConfigs.length === 0}
              >
                <option value="">Select a Room Type</option>
                {roomConfigs.map(rc => <option key={rc.id} value={String(rc.id)}>{rc.room_type} (Max: {rc.max_occupancy}, Price: ${rc.price_per_night})</option>)}
              </select>
            )}
            {errors.room_configuration_id_str && <p style={errorStyle}>{errors.room_configuration_id_str.message}</p>}
          </div>

          <div>
            <label htmlFor="edit_allocated_rooms">Allocated Rooms:</label>
            <input id="edit_allocated_rooms" type="number" {...register('allocated_rooms_str', { required: 'Number of rooms is required', min: 1 })} style={inputStyle} />
            {errors.allocated_rooms_str && <p style={errorStyle}>{errors.allocated_rooms_str.message}</p>}
          </div>

          <div style={{display: 'flex', gap: '1rem'}}>
            <div style={{flex:1}}>
                <label htmlFor="edit_check_in_date">Check-in Date:</label>
                <input id="edit_check_in_date" type="date" {...register('check_in_date', { required: 'Check-in date is required' })} style={inputStyle} />
                {errors.check_in_date && <p style={errorStyle}>{errors.check_in_date.message}</p>}
            </div>
            <div style={{flex:1}}>
                <label htmlFor="edit_check_out_date">Check-out Date:</label>
                <input id="edit_check_out_date" type="date" {...register('check_out_date', { required: 'Check-out date is required' })} style={inputStyle} />
                {errors.check_out_date && <p style={errorStyle}>{errors.check_out_date.message}</p>}
            </div>
          </div>

          {apiError && <p style={{ color: 'red', marginTop: '0.5rem' }}>Error: {apiError}</p>}

          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
            <button type="button" onClick={onClose} style={{...buttonStyle, background: '#6c757d'}}>Cancel</button>
            <button type="submit" disabled={isSubmitting || isLoadingHotels || isLoadingRoomConfigs || !isDirty} style={{...buttonStyle, background: '#28a745', opacity: !isDirty ? 0.7 : 1}}>
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Re-use or define common styles
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

export default EditHotelAllocationModal;
