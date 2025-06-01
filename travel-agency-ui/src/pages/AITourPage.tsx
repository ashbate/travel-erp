import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { generateAITour } from '../services/apiService';
import { AITourPromptClient, AIGeneratedItineraryClient } from '../types'; // Assuming index.ts for types
// For rendering markdown, you might need a library like 'react-markdown'
// If so, npm install react-markdown
// import ReactMarkdown from 'react-markdown';

interface FormInput extends Omit<AITourPromptClient, 'interests' | 'preferred_activities'> {
  interests_str?: string;
  preferred_activities_str?: string;
}

const AITourPage: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormInput>();
  const [itinerary, setItinerary] = useState<AIGeneratedItineraryClient | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const onSubmit: SubmitHandler<FormInput> = async (data) => {
    setIsLoading(true);
    setApiError(null);
    setItinerary(null);

    const promptData: AITourPromptClient = {
      destination: data.destination,
      duration_days: Number(data.duration_days),
      traveler_type: data.traveler_type || undefined,
      interests: data.interests_str?.split(',').map(s => s.trim()).filter(s => s) || undefined,
      budget_level: data.budget_level || undefined,
      preferred_activities: data.preferred_activities_str?.split(',').map(s => s.trim()).filter(s => s) || undefined,
    };

    try {
      const result = await generateAITour(promptData);
      setItinerary(result);
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Failed to generate itinerary.');
      console.error('AI Tour Generation Error:', err);
    }
    setIsLoading(false);
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Create Tour with AI</h1>
      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '600px', marginBottom: '2rem' }}>
        <div>
          <label htmlFor="destination">Destination:</label>
          <input id="destination" {...register('destination', { required: 'Destination is required' })} style={{width: '100%', padding: '0.5rem'}} />
          {errors.destination && <p style={{color: 'red'}}>{errors.destination.message}</p>}
        </div>
        <div>
          <label htmlFor="duration_days">Duration (days):</label>
          <input id="duration_days" type="number" {...register('duration_days', { required: 'Duration is required', min: { value: 1, message: 'Duration must be at least 1 day'} })} style={{width: '100%', padding: '0.5rem'}} />
          {errors.duration_days && <p style={{color: 'red'}}>{errors.duration_days.message}</p>}
        </div>
        <div>
          <label htmlFor="traveler_type">Traveler Type (e.g., solo, couple, family):</label>
          <input id="traveler_type" {...register('traveler_type')} style={{width: '100%', padding: '0.5rem'}} />
        </div>
        <div>
          <label htmlFor="interests_str">Interests (comma-separated, e.g., history, food):</label>
          <input id="interests_str" {...register('interests_str')} style={{width: '100%', padding: '0.5rem'}} />
        </div>
        <div>
          <label htmlFor="budget_level">Budget Level (e.g., budget, mid-range, luxury):</label>
          <input id="budget_level" {...register('budget_level')} style={{width: '100%', padding: '0.5rem'}} />
        </div>
        <div>
          <label htmlFor="preferred_activities_str">Preferred Activities (comma-separated):</label>
          <input id="preferred_activities_str" {...register('preferred_activities_str')} style={{width: '100%', padding: '0.5rem'}} />
        </div>
        <button type="submit" disabled={isLoading} style={{padding: '0.75rem', background: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer'}}>
          {isLoading ? 'Generating...' : 'Generate Itinerary'}
        </button>
      </form>

      {isLoading && <p>Loading itinerary...</p>}
      {apiError && <p style={{ color: 'red' }}>Error: {apiError}</p>}

      {itinerary && (
        <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '4px' }}>
          <h2>Suggested Itinerary: {itinerary.tour_name_suggestion}</h2>
          <p><strong>Description:</strong> {itinerary.suggested_description}</p>
          {itinerary.estimated_price_range && <p><strong>Price Range:</strong> {itinerary.estimated_price_range}</p>}
          {itinerary.warnings && itinerary.warnings.length > 0 && (
            <div>
              <strong>Warnings:</strong>
              <ul>
                {itinerary.warnings.map((warning, index) => <li key={index} style={{color: 'orange'}}>{warning}</li>)}
              </ul>
            </div>
          )}
          <h3>Itinerary Details:</h3>
          {/* For basic markdown rendering, replace newlines with <br /> or use a library */}
          <div style={{ whiteSpace: 'pre-wrap', background: '#f9f9f9', padding: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
            {itinerary.itinerary_details}
            {/* Example with react-markdown: <ReactMarkdown>{itinerary.itinerary_details}</ReactMarkdown> */}
          </div>
        </div>
      )}
    </div>
  );
};

export default AITourPage;
