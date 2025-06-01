import React, { useEffect, useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { getTourById, updateTour } from '../services/apiService';
import { TourReadClient, TourUpdateClient } from '../types';

interface EditTourFormInput extends Omit<TourUpdateClient, 'price_per_guest' | 'max_capacity'> {
  price_per_guest_str?: string;
  max_capacity_str?: string;
}

const EditTourPage: React.FC = () => {
  const { tourId } = useParams<{ tourId: string }>();
  const navigate = useNavigate();
  const { register, handleSubmit, setValue, formState: { errors, isDirty } } = useForm<EditTourFormInput>();

  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [originalTourName, setOriginalTourName] = useState<string>('');

  useEffect(() => {
    if (!tourId) {
      navigate('/tours'); // Should not happen if route is correct
      return;
    }
    const fetchTourData = async () => {
      setIsFetching(true);
      try {
        const tour = await getTourById(Number(tourId));
        setOriginalTourName(tour.name);
        // Populate form with existing data
        setValue('name', tour.name);
        setValue('destination', tour.destination);
        setValue('description', tour.description || '');
        setValue('start_date', tour.start_date.split('T')[0]); // Assuming date comes as ISO string
        setValue('end_date', tour.end_date.split('T')[0]);
        setValue('price_per_guest_str', String(tour.price_per_guest));
        setValue('max_capacity_str', tour.max_capacity ? String(tour.max_capacity) : '');
        setValue('itinerary_details', tour.itinerary_details || '');
      } catch (err) {
        setApiError('Failed to load tour data.');
        console.error(err);
      }
      setIsFetching(false);
    };
    fetchTourData();
  }, [tourId, setValue, navigate]);

  const onSubmit: SubmitHandler<EditTourFormInput> = async (data) => {
    if (!tourId) return;
    if (!isDirty) {
        navigate(`/tours/${tourId}`); // No changes, just navigate back
        return;
    }
    setIsLoading(true);
    setApiError(null);

    const tourDataToSubmit: TourUpdateClient = {
      name: data.name,
      destination: data.destination,
      description: data.description || null,
      start_date: data.start_date,
      end_date: data.end_date,
      price_per_guest: data.price_per_guest_str ? parseFloat(data.price_per_guest_str) : undefined,
      max_capacity: data.max_capacity_str ? parseInt(data.max_capacity_str, 10) : null,
      itinerary_details: data.itinerary_details || null,
    };
    // Filter out undefined values to avoid sending them if not changed/intended for partial update
    Object.keys(tourDataToSubmit).forEach(key =>
        (tourDataToSubmit as any)[key] === undefined && delete (tourDataToSubmit as any)[key]
    );

    try {
      await updateTour(Number(tourId), tourDataToSubmit);
      navigate(`/tours/${tourId}`);
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Failed to update tour.');
      console.error('Update Tour Error:', err);
    }
    setIsLoading(false);
  };

  if (isFetching) return <p>Loading tour data for editing...</p>;
  if (apiError && !originalTourName) return <p style={{ color: 'red' }}>Error: {apiError}</p>; // Show critical error if data couldn't be loaded

  return (
    <div style={{ padding: '2rem', maxWidth: '700px', margin: 'auto' }}>
      <Link to={tourId ? `/tours/${tourId}` : "/tours"} style={{ marginBottom: '1rem', display: 'inline-block' }}>&larr; Back to Tour Details</Link>
      <h1>Edit Tour: {originalTourName}</h1>
      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Form fields are same as CreateTourPage, just pre-filled */}
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

        {apiError && <p style={{ color: 'red', marginTop: '1rem' }}>Error during update: {apiError}</p>}

        <button type="submit" disabled={isLoading || !isDirty} style={{...buttonStyle, opacity: (!isDirty || isLoading) ? 0.7 : 1}}>
          {isLoading ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
};

const inputStyle: React.CSSProperties = { width: '100%', padding: '0.5rem', boxSizing: 'border-box', marginTop: '0.25rem' };
const errorStyle: React.CSSProperties = { color: 'red', fontSize: '0.875em', marginTop: '0.25rem' };
const buttonStyle: React.CSSProperties = { padding: '0.75rem', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '1rem' };

export default EditTourPage;
