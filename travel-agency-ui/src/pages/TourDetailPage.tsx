import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTourById, deleteHotelAllocation } from '../services/apiService'; // Add deleteHotelAllocation
import { TourReadClient, TourHotelAllocationClient } from '../types';
import AddHotelAllocationModal from '../components/tours/AddHotelAllocationModal';
import EditHotelAllocationModal from '../components/tours/EditHotelAllocationModal';

const TourDetailPage: React.FC = () => {
  const { tourId } = useParams<{ tourId: string }>();
  const [tour, setTour] = useState<TourReadClient | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false); // Renamed for clarity
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedAllocationForEdit, setSelectedAllocationForEdit] = useState<TourHotelAllocationClient | null>(null);

  const fetchTourData = async (showLoading: boolean = true) => {
    if (tourId) {
      if(showLoading) setIsLoading(true);
      setError(null);
      try {
        const data = await getTourById(Number(tourId));
        setTour(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch tour details.');
        console.error('Fetch Tour Detail Error:', err);
      }
      if(showLoading) setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTourData();
  }, [tourId]);

  const handleAllocationAdded = (newAllocation: TourHotelAllocationClient) => {
    fetchTourData(false); // Re-fetch without full page load indicator
  };

  const handleAllocationUpdated = (updatedAllocation: TourHotelAllocationClient) => {
    fetchTourData(false); // Re-fetch
  };

  const openEditModal = (allocation: TourHotelAllocationClient) => {
    setSelectedAllocationForEdit(allocation);
    setIsEditModalOpen(true);
  };

  const handleRemoveAllocation = async (allocationId: number) => {
    if (window.confirm('Are you sure you want to remove this hotel allocation?')) {
      try {
        await deleteHotelAllocation(allocationId);
        // Refresh tour data to reflect the deletion
        fetchTourData(false);
        // Or, for a more responsive UI without full re-fetch:
        // setTour(prevTour => prevTour ? ({
        //   ...prevTour,
        //   hotel_allocations: prevTour.hotel_allocations?.filter(alloc => alloc.id !== allocationId) || []
        // }) : null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to remove allocation.');
        console.error('Remove Allocation Error:', err);
      }
    }
  };

  if (isLoading) return <p>Loading tour details...</p>;
  // Display general error, but allow page to render if tour data is already present from a previous fetch
  if (error && !tour) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!tour && !isLoading) return <p>Tour not found.</p>; // Ensure this shows if tour is null and not loading
  if (!tour) return null; // Should be caught by above, but as a fallback


  return (
    <div style={{ padding: '1rem' }}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <Link to="/tours" style={{ marginBottom: '1rem', display: 'inline-block' }}>&larr; Back to Tours</Link>
        <Link
            to={`/tours/${tour.id}/edit`}
            style={{padding: '0.5rem 1rem', background: '#ffc107', color: 'black', textDecoration: 'none', borderRadius: '4px'}}
        >
            Edit Tour
        </Link>
      </div>
      <h1>{tour.name}</h1>
      <p><strong>Destination:</strong> {tour.destination}</p>
      {tour.travel_mode && <p><strong>Travel Mode:</strong> {tour.travel_mode}</p>}
      <p><strong>Dates:</strong> {new Date(tour.start_date).toLocaleDateString()} - {new Date(tour.end_date).toLocaleDateString()}</p>
      <p><strong>Price:</strong> ${tour.price_per_guest} per guest</p>
      {tour.max_capacity && <p><strong>Max Capacity:</strong> {tour.max_capacity} guests</p>}
      <p><strong>Current Bookings:</strong> {tour.current_bookings_count}</p>
      {tour.description && <p style={{marginTop: '1rem', whiteSpace: 'pre-wrap'}}><strong>Description:</strong><br/>{tour.description}</p>}

      {/* ... other tour details ... */}
      {error && <p style={{color: 'red', border: '1px solid red', padding: '0.5rem'}}>Page Error: {error}</p>}

      <div style={{marginTop: '1.5rem'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem'}}>
          <h3>Hotel Allocations:</h3>
          <button onClick={() => setIsAddModalOpen(true)} style={{padding: '0.5rem 1rem', background: '#17a2b8', color: 'white', border: 'none', borderRadius: '4px'}}>Add Allocation</button>
        </div>
        {tour.hotel_allocations && tour.hotel_allocations.length > 0 ? (
          <ul style={{listStyle: 'none', paddingLeft: 0}}>
            {tour.hotel_allocations.map(alloc => (
              <li key={alloc.id} style={{border: '1px solid #eee', padding: '0.75rem', marginBottom: '0.5rem', borderRadius: '4px'}}>
                <strong>Hotel ID:</strong> {alloc.hotel_id} (<i>Name lookup needed</i>) <br />
                <strong>Room Config ID:</strong> {alloc.room_configuration_id} (<i>Type lookup needed</i>) <br />
                <strong>Allocated Rooms:</strong> {alloc.allocated_rooms} <br />
                <strong>Dates:</strong> {new Date(alloc.check_in_date).toLocaleDateString()} - {new Date(alloc.check_out_date).toLocaleDateString()}
                <div style={{marginTop: '0.5rem'}}>
                  <button onClick={() => openEditModal(alloc)} style={{marginRight: '0.5rem', background: '#ffc107', border: 'none', padding: '0.3rem 0.6rem', borderRadius: '3px', cursor: 'pointer'}}>Edit</button>
                  <button onClick={() => handleRemoveAllocation(alloc.id)} style={{background: '#dc3545', color: 'white', border: 'none', padding: '0.3rem 0.6rem', borderRadius: '3px', cursor: 'pointer'}}>Remove</button>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No hotel allocations for this tour yet.</p>
        )}
      </div>

      <AddHotelAllocationModal
        tourId={Number(tourId)}
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAllocationAdded={handleAllocationAdded}
      />
      {selectedAllocationForEdit && (
        <EditHotelAllocationModal
          allocation={selectedAllocationForEdit}
          tourId={Number(tourId)}
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setSelectedAllocationForEdit(null);
          }}
          onAllocationUpdated={handleAllocationUpdated}
        />
      )}

      {/* ... (Itinerary details) ... */}
      {tour.itinerary_details && (
        <details style={{marginTop: '1rem'}}>
          <summary style={{cursor: 'pointer', fontWeight: 'bold'}}>View Itinerary Details</summary>
          <div style={{ whiteSpace: 'pre-wrap', background: '#f9f9f9', padding: '1rem', marginTop: '0.5rem', border: '1px solid #eee', borderRadius: '4px' }}>
            {tour.itinerary_details}
          </div>
        </details>
      )}
    </div>
  );
};

export default TourDetailPage;
