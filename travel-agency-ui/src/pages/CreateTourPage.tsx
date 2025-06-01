import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { createTour } from '../services/apiService';
import { TourCreateClient } from '../types';

// Form input type might be slightly different if handling dates/numbers specifically before submission
interface CreateTourFormInput extends Omit<TourCreateClient, 'price_per_guest' | 'max_capacity'> {
  price_per_guest_str: string;
  max_capacity_str?: string;
}

const CreateTourPage: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateTourFormInput>();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const onSubmit: SubmitHandler<CreateTourFormInput> = async (data) => {
    setIsLoading(true);
    setApiError(null);

    const tourDataToSubmit: TourCreateClient = {
      ...data,
      price_per_guest: parseFloat(data.price_per_guest_str),
      max_capacity: data.max_capacity_str ? parseInt(data.max_capacity_str, 10) : null,
      description: data.description || null,
      itinerary_details: data.itinerary_details || null,
    };

    try {
      const newTour = await createTour(tourDataToSubmit);
      navigate(`/tours/${newTour.id}`); // Navigate to the new tour's detail page
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Failed to create tour.');
      console.error('Create Tour Error:', err);
    }
    setIsLoading(false);
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '700px', margin: 'auto' }}>
      <h1>Create New Tour</h1>
      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label htmlFor="name">Tour Name:</label>
          <input id="name" {...register('name', { required: 'Tour name is required' })} style={inputStyle} />
          {errors.name && <p style={errorStyle}>{errors.name.message}</p>}
        </div>
        <div>
          <label htmlFor="destination">Destination:</label>
          <input id="destination" {...register('destination', { required: 'Destination is required' })} style={inputStyle} />
          {errors.destination && <p style={errorStyle}>{errors.destination.message}</p>}
        </div>
        <div>
          <label htmlFor="description">Description (Optional):</label>
          <textarea id="description" {...register('description')} style={{...inputStyle, height: '80px'}} />
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
            <div style={{flex: 1}}>
                <label htmlFor="start_date">Start Date:</label>
                <input id="start_date" type="date" {...register('start_date', { required: 'Start date is required' })} style={inputStyle} />
                {errors.start_date && <p style={errorStyle}>{errors.start_date.message}</p>}
            </div>
            <div style={{flex: 1}}>
                <label htmlFor="end_date">End Date:</label>
                <input id="end_date" type="date" {...register('end_date', { required: 'End date is required' })} style={inputStyle} />
                {errors.end_date && <p style={errorStyle}>{errors.end_date.message}</p>}
            </div>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
            <div style={{flex: 1}}>
                <label htmlFor="price_per_guest_str">Price per Guest ($):</label>
                <input id="price_per_guest_str" type="text" {...register('price_per_guest_str', { required: 'Price is required', pattern: { value: /^\d*\.?\d*$/, message: 'Invalid price format'} })} style={inputStyle} />
                {errors.price_per_guest_str && <p style={errorStyle}>{errors.price_per_guest_str.message}</p>}
            </div>
            <div style={{flex: 1}}>
                <label htmlFor="max_capacity_str">Max Capacity (Optional):</label>
                <input id="max_capacity_str" type="text" {...register('max_capacity_str', { pattern: { value: /^\d*$/, message: 'Must be a number'} })} style={inputStyle} />
                 {errors.max_capacity_str && <p style={errorStyle}>{errors.max_capacity_str.message}</p>}
            </div>
        </div>
        <div>
          <label htmlFor="itinerary_details">Itinerary Details (Optional, Markdown supported by backend):</label>
          <textarea id="itinerary_details" {...register('itinerary_details')} style={{...inputStyle, height: '120px', whiteSpace: 'pre-wrap'}} />
        </div>

        {apiError && <p style={{ color: 'red', marginTop: '1rem' }}>Error: {apiError}</p>}

        <button type="submit" disabled={isLoading} style={buttonStyle}>
          {isLoading ? 'Creating...' : 'Create Tour'}
        </button>
      </form>
    </div>
  );
};

const inputStyle: React.CSSProperties = { width: '100%', padding: '0.5rem', boxSizing: 'border-box', marginTop: '0.25rem' };
const errorStyle: React.CSSProperties = { color: 'red', fontSize: '0.875em', marginTop: '0.25rem' };
const buttonStyle: React.CSSProperties = { padding: '0.75rem', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '1rem' };

export default CreateTourPage;
